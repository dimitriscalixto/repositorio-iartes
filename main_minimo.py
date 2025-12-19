from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP


def calcular_salario_liquido(salario_bruto: float) -> float:
    if salario_bruto <= 0:
        raise ValueError("Salário bruto deve ser maior que zero.")

    bruto = Decimal(str(salario_bruto))

    # INSS: 8% limitado a R$ 500,00
    inss = bruto * Decimal("0.08")
    if inss > Decimal("500"):
        inss = Decimal("500")

    # IRRF: isento até 2000 (inclusive), senão 10% do total do bruto
    irrf = Decimal("0")
    if bruto > Decimal("2000"):
        irrf = bruto * Decimal("0.10")

    liquido = bruto - inss - irrf

    # Arredondamento para 2 casas decimais (padrão monetário)
    liquido = liquido.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(liquido)
