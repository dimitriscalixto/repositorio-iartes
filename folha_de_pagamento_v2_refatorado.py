from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Tuple

# Alias para clareza semântica
Money = Decimal

@dataclass(frozen=True)
class FaixaIR:
    """Representa uma linha da tabela progressiva de IR."""
    limite_superior: Money
    aliquota: Money

@dataclass(frozen=True)
class RegrasFiscais:
    """
    Configuração das regras fiscais.
    Permite injeção de dependência para diferentes anos ou regimes.
    O 'frozen=True' garante Segurança (imutabilidade).
    """
    inss_aliquota: Money = Decimal("0.08")
    inss_teto: Money = Decimal("500.00")
    vt_aliquota: Money = Decimal("0.06")
    # Regra Python original: 5% de abatimento sobre o imposto devido por dependente
    dep_abatimento_percentual: Money = Decimal("0.05") 
    
    # Tabela padrão configurada conforme exercício
    tabela_ir: List[FaixaIR] = field(default_factory=lambda: [
        FaixaIR(Decimal("2000.00"), Decimal("0.00")),
        FaixaIR(Decimal("4000.00"), Decimal("0.10")),
        FaixaIR(Decimal("Infinity"), Decimal("0.20")),
    ])

class CalculadoraFolha:
    """
    Classe pura de lógica. Não contém dados hardcoded.
    Recebe as regras no construtor.
    """
    def __init__(self, regras: RegrasFiscais = RegrasFiscais()):
        self.regras = regras

    def calcular_liquido(self, salario_bruto: float, num_dependentes: int = 0, vale_transporte: bool = False) -> float:
        # 1. Validação e Conversão (Sanitização)
        bruto = self._sanitizar_entrada(salario_bruto, num_dependentes)

        # 2. Cálculos Isolados
        desc_inss = self._calcular_inss(bruto)
        desc_vt = self._calcular_vt(bruto, vale_transporte)
        
        # O IR depende do bruto para achar a faixa, e depois dos dependentes para o abatimento
        ir_bruto = self._calcular_ir_base(bruto)
        desc_ir = self._aplicar_abatimento_dependentes(ir_bruto, num_dependentes)

        # 3. Consolidação
        liquido = bruto - desc_inss - desc_vt - desc_ir
        return float(self._arredondar(liquido))

    def _sanitizar_entrada(self, salario: float, dependentes: int) -> Money:
        if salario <= 0:
            raise ValueError("O salário bruto deve ser positivo.")
        if dependentes < 0:
            raise ValueError("O número de dependentes não pode ser negativo.")
        return Decimal(str(salario))

    def _calcular_inss(self, bruto: Money) -> Money:
        calculado = bruto * self.regras.inss_aliquota
        return min(calculado, self.regras.inss_teto)

    def _calcular_vt(self, bruto: Money, optou: bool) -> Money:
        if not optou:
            return Decimal("0.00")
        return self._arredondar(bruto * self.regras.vt_aliquota)

    def _calcular_ir_base(self, bruto: Money) -> Money:
        for faixa in self.regras.tabela_ir:
            if bruto <= faixa.limite_superior:
                return self._arredondar(bruto * faixa.aliquota)
        return Decimal("0.00") # Should be unreachable due to Infinity

    def _aplicar_abatimento_dependentes(self, ir_base: Money, dependentes: int) -> Money:
        if ir_base <= 0 or dependentes == 0:
            return ir_base
        
        # Lógica: 1 - (0.05 * n_dependentes)
        fator_reducao = Decimal("1.00") - (self.regras.dep_abatimento_percentual * dependentes)
        
        # Segurança: Imposto não pode ser negativo (governo devendo ao funcionário)
        fator_reducao = max(fator_reducao, Decimal("0.00"))
        
        return self._arredondar(ir_base * fator_reducao)

    def _arredondar(self, valor: Money) -> Money:
        return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)