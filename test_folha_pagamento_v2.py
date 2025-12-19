import pytest
from decimal import Decimal
from folha_de_pagamento_v2_refatorado import CalculadoraFolha, RegrasFiscais

# Fixture: Prepara a calculadora antes dos testes
@pytest.fixture
def calculadora():
    return CalculadoraFolha() # Usa regras padrão

# ======== TESTES DE ERROS (Validação) ========
@pytest.mark.parametrize("salario, dependentes", [
    (0, 0),
    (-100, 0),
    (2000, -1)
])
def test_deve_lancar_erro_entradas_invalidas(calculadora, salario, dependentes):
    with pytest.raises(ValueError):
        calculadora.calcular_liquido(salario, dependentes)

# ======== TESTES DE REGRAS DE NEGÓCIO (Tabela de Cenários) ========
# Estrutura: Bruto, Dep, VT, Esperado, Descrição do Cenário
cenarios_calculo = [
    # Cenário 1: Salário Baixo (Isento IR, INSS 8%, Sem VT)
    (1000.00, 0, False, 920.00, "Salário Baixo: Apenas INSS"),
    
    # Cenário 2: Limite Isenção IR (2000)
    # INSS: 160.00 (8%), IR: 0.00
    (2000.00, 0, False, 1840.00, "Limite Isenção IR"),

    # Cenário 3: Faixa 1 IR (3000)
    # INSS: 240.00, IR: 300.00 (10%)
    (3000.00, 0, False, 2460.00, "Faixa 1 IR"),
    
    # Cenário 4: Teto INSS + Faixa 2 IR (7000)
    # INSS: 500.00 (Teto), IR: 1400.00 (20%)
    (7000.00, 0, False, 5100.00, "Teto INSS + Faixa 2 IR"),

    # Cenário 5: Uso de Vale Transporte (3000)
    # Liq Base: 2460.00 - VT(180.00) = 2280.00
    (3000.00, 0, True, 2280.00, "Com Vale Transporte"),

    # Cenário 6: Dependentes (4000 com 2 filhos)
    # INSS: 320.00
    # IR Base: 400.00 (10%)
    # Abatimento: 2 * 5% = 10%. IR Final = 360.00
    # Liq: 4000 - 320 - 360 = 3320.00
    (4000.00, 2, False, 3320.00, "Com Dependentes"),

    # Cenário 7: Muitos Dependentes Zeram IR (3000 com 20 filhos)
    # IR Base: 300.00. Abatimento 20*5% = 100% de desconto. IR = 0.
    # Liq: 3000 - 240(INSS) = 2760.00
    (3000.00, 20, False, 2760.00, "Dependentes Zerando IR"),
    
    # Cenário 8: Arredondamento
    (3333.33, 0, False, 2733.33, "Verificação de Arredondamento"),
]

@pytest.mark.parametrize("bruto, deps, vt, esperado, motivo", cenarios_calculo)
def test_calculo_salario_liquido(calculadora, bruto, deps, vt, esperado, motivo):
    resultado = calculadora.calcular_liquido(bruto, deps, vt)
    # Comparar floats requer cuidado, mas como o sistema arredonda para 2 casas
    # no retorno, a comparação direta costuma funcionar. 
    # Para ser purista, convertemos o esperado para string ou usamos pytest.approx
    assert resultado == pytest.approx(esperado, abs=0.01), f"Falha no cenário: {motivo}"

# ======== TESTE DE EXTENSIBILIDADE (Novo!) ========
def test_deve_suportar_novas_regras_sem_mexer_na_logica():
    """
    Testa a Manutenibilidade: Injeta uma regra fictícia (Ex: INSS dobrou para 16%)
    sem alterar a classe CalculadoraFolha.
    """
    regras_futuro = RegrasFiscais(inss_aliquota=Decimal("0.16")) # 16%
    calc_futuro = CalculadoraFolha(regras_futuro)
    
    # 1000 * 16% = 160 desc. Liq = 840.
    assert calc_futuro.calcular_liquido(1000, 0, False) == 840.00