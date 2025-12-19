from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Union

Numero = Union[int, float, Decimal]

INSS_ALIQUOTA = Decimal("0.08")
INSS_TETO = Decimal("500.00")

IRRF_LIMITE_ISENCAO = Decimal("2000.00")
IRRF_ALIQUOTA = Decimal("0.10")

CASAS_2 = Decimal("0.01")


def calcular_salario_liquido(salario_bruto: Numero) -> float:
    bruto = _validar_salario(_as_decimal(salario_bruto))

    liquido = bruto - _desconto_inss(bruto) - _desconto_irrf(bruto)
    liquido = _arredondar_2_casas(liquido)

    return float(liquido)


def _validar_salario(bruto: Decimal) -> Decimal:
    if bruto <= 0:
        raise ValueError("Salário bruto deve ser maior que zero.")
    return bruto


def _desconto_inss(bruto: Decimal) -> Decimal:
    desconto = bruto * INSS_ALIQUOTA
    return INSS_TETO if desconto > INSS_TETO else desconto


def _desconto_irrf(bruto: Decimal) -> Decimal:
    return (bruto * IRRF_ALIQUOTA) if bruto > IRRF_LIMITE_ISENCAO else Decimal("0")


def _arredondar_2_casas(valor: Decimal) -> Decimal:
    return valor.quantize(CASAS_2, rounding=ROUND_HALF_UP)


def _as_decimal(valor: Numero) -> Decimal:
    # Mais estrito: só aceita int/float/Decimal (não aceita str, None, etc.)
    # bool é subclass de int, então bloqueamos explicitamente.
    if isinstance(valor, bool) or not isinstance(valor, (int, float, Decimal)):
        raise TypeError("Salário bruto deve ser numérico (int, float ou Decimal).")
    # str(float) evita ruído binário comum em cálculos monetários
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))
