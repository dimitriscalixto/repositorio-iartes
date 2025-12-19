from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

Numero = Union[int, float, Decimal]


INSS_ALIQUOTA = Decimal("0.08")
INSS_TETO = Decimal("500.00")

VT_ALIQUOTA = Decimal("0.06")

IR_LIMITE_ISENCAO = Decimal("2000.00")
IR_LIMITE_FAIXA_10 = Decimal("4000.00")
IR_ALIQUOTA_10 = Decimal("0.10")
IR_ALIQUOTA_20 = Decimal("0.20")

DEP_ABATIMENTO_POR_DEP = Decimal("0.05")  # 5% do IR por dependente

CASAS_2 = Decimal("0.01")


def calcular_salario_liquido(
    salario_bruto: Numero,
    num_dependentes: int = 0,
    vale_transporte: bool = False
) -> float:
    bruto = _as_decimal(salario_bruto)

    if bruto <= 0:
        raise ValueError("Salário bruto deve ser maior que zero.")
    if num_dependentes < 0:
        raise ValueError("Número de dependentes deve ser >= 0.")
    if not isinstance(vale_transporte, bool):
        raise TypeError("Indicador de vale-transporte deve ser booleano.")

    inss = _calcular_inss(bruto)
    ir_base = _calcular_ir_base(bruto)
    ir_final = _aplicar_abatimento_dependentes(ir_base, num_dependentes)
    vt = _calcular_vt(bruto, vale_transporte)

    liquido = bruto - inss - ir_final - vt
    liquido = liquido.quantize(CASAS_2, rounding=ROUND_HALF_UP)
    return float(liquido)


def _calcular_inss(bruto: Decimal) -> Decimal:
    desconto = bruto * INSS_ALIQUOTA
    return INSS_TETO if desconto > INSS_TETO else desconto


def _calcular_ir_base(bruto: Decimal) -> Decimal:
    if bruto <= IR_LIMITE_ISENCAO:
        return Decimal("0")
    if bruto <= IR_LIMITE_FAIXA_10:
        return bruto * IR_ALIQUOTA_10
    return bruto * IR_ALIQUOTA_20


def _aplicar_abatimento_dependentes(ir_base: Decimal, dependentes: int) -> Decimal:
    if ir_base <= 0 or dependentes == 0:
        return ir_base

    abatimento_pct = DEP_ABATIMENTO_POR_DEP * Decimal(dependentes)
    if abatimento_pct > Decimal("1"):
        abatimento_pct = Decimal("1")

    ir_final = ir_base * (Decimal("1") - abatimento_pct)
    if ir_final < 0:
        ir_final = Decimal("0")
    return ir_final


def _calcular_vt(bruto: Decimal, optou_vt: bool) -> Decimal:
    return (bruto * VT_ALIQUOTA) if optou_vt else Decimal("0")


def _as_decimal(valor: Numero) -> Decimal:
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise TypeError("Salário bruto deve ser numérico (int, float ou Decimal).")
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))
