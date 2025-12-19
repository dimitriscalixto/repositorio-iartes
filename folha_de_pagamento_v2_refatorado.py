from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Union, Tuple

Numero = Union[int, float, Decimal]
Money = Decimal


# Regras (constantes) — centralizadas para facilitar mudança de lei/regra
INSS_ALIQUOTA: Money = Decimal("0.08")
INSS_TETO: Money = Decimal("500.00")

VT_ALIQUOTA: Money = Decimal("0.06")

DEP_ABATIMENTO_POR_DEP: Money = Decimal("0.05")  # 5% do IR por dependente

CASAS_2: Money = Decimal("0.01")

# Faixas de IR (alíquota aplicada sobre o TOTAL do salário bruto)
# (limite_superior_inclusivo, aliquota). O último limite é "infinito".
IR_TABELA: Tuple[Tuple[Money, Money], ...] = (
    (Decimal("2000.00"), Decimal("0.00")),
    (Decimal("4000.00"), Decimal("0.10")),
    (Decimal("Infinity"), Decimal("0.20")),
)


def calcular_salario_liquido(
    salario_bruto: Numero,
    num_dependentes: int = 0,
    vale_transporte: bool = False,
) -> float:
    bruto = _validar_e_converter_entrada(salario_bruto, num_dependentes, vale_transporte)

    inss = _desconto_inss(bruto)
    ir_base = _desconto_ir_base(bruto)
    ir_final = _aplicar_abatimento_dependentes(ir_base, num_dependentes)
    vt = _desconto_vale_transporte(bruto, vale_transporte)

    liquido = bruto - inss - ir_final - vt
    liquido = _arredondar_2_casas(liquido)
    return float(liquido)


def _validar_e_converter_entrada(
    salario_bruto: Numero, num_dependentes: int, vale_transporte: bool
) -> Money:
    bruto = _as_decimal(salario_bruto)

    if bruto <= 0:
        raise ValueError("Salário bruto deve ser maior que zero.")
    if num_dependentes < 0:
        raise ValueError("Número de dependentes deve ser >= 0.")
    if not isinstance(vale_transporte, bool):
        raise TypeError("Indicador de vale-transporte deve ser booleano.")

    return bruto


def _desconto_inss(bruto: Money) -> Money:
    desconto = bruto * INSS_ALIQUOTA
    return INSS_TETO if desconto > INSS_TETO else desconto


def _aliquota_ir(bruto: Money) -> Money:
    # Implementação orientada a dados reduz if/else e facilita atualização de faixas
    for limite, aliquota in IR_TABELA:
        if bruto <= limite:
            return aliquota
    return Decimal("0")  # fallback defensivo


def _desconto_ir_base(bruto: Money) -> Money:
    return bruto * _aliquota_ir(bruto)


def _aplicar_abatimento_dependentes(ir_base: Money, dependentes: int) -> Money:
    if ir_base <= 0 or dependentes == 0:
        return ir_base

    # Abatimento percentual do IR, limitado para nunca ficar negativo
    fator = Decimal("1") - (DEP_ABATIMENTO_POR_DEP * Decimal(dependentes))
    if fator < 0:
        fator = Decimal("0")

    return ir_base * fator


def _desconto_vale_transporte(bruto: Money, optou: bool) -> Money:
    return bruto * VT_ALIQUOTA if optou else Decimal("0")


def _arredondar_2_casas(valor: Money) -> Money:
    return valor.quantize(CASAS_2, rounding=ROUND_HALF_UP)


def _as_decimal(valor: Numero) -> Money:
    # Segurança/robustez: bool é subclass de int, mas não é salário
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise TypeError("Salário bruto deve ser numérico (int, float ou Decimal).")
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))
