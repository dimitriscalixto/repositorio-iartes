import pytest
from folha_de_pagamento_v2_refatorado import calcular_salario_liquido


# ======== VALIDAÇÕES DE ENTRADA ========

def test_salario_menor_ou_igual_a_zero_deve_lancar_erro():
    with pytest.raises(ValueError):
        calcular_salario_liquido(0, 0, False)
    with pytest.raises(ValueError):
        calcular_salario_liquido(-100, 0, False)


def test_dependentes_negativos_devem_lancar_erro():
    with pytest.raises(ValueError):
        calcular_salario_liquido(2000, -1, False)


# ======== INSS ========

def test_inss_deve_ser_8_porcento_ate_o_teto():
    # 8% de 4000 = 320.00, sem teto
    resultado = calcular_salario_liquido(4000, 0, False)
    # IR = 10% de 4000 = 400; INSS = 320
    # líquido = 4000 - 320 - 400 = 3280
    assert f"{resultado:.2f}" == "3280.00"


def test_inss_nao_pode_ultrapassar_teto_de_500():
    # 8% de 7000 = 560, aplica teto de 500
    # IR = 20% de 7000 = 1400
    # líquido = 7000 - 500 - 1400 = 5100
    assert f"{calcular_salario_liquido(7000, 0, False):.2f}" == "5100.00"


# ======== IMPOSTO DE RENDA ========

def test_irrf_isento_ate_2000():
    # INSS = 8% de 2000 = 160; IR = 0
    # líquido = 2000 - 160 = 1840.00
    assert f"{calcular_salario_liquido(2000, 0, False):.2f}" == "1840.00"


def test_irrf_10_porcento_para_faixa_intermediaria():
    # bruto = 3000; INSS = 240; IR = 300
    # líquido = 3000 - 240 - 300 = 2460
    assert f"{calcular_salario_liquido(3000, 0, False):.2f}" == "2460.00"


def test_irrf_20_porcento_para_faixa_superior():
    # bruto = 5000; INSS=400; IR=1000
    # líquido = 5000 - 400 - 1000 = 3600
    assert f"{calcular_salario_liquido(5000, 0, False):.2f}" == "3600.00"


# ======== DEPENDENTES ========

def test_dependentes_reduzem_ir_em_5_porcento_por_dependente():
    # bruto = 4000; INSS=320; IR base=400; dependentes=2 -> -10% IR
    # IR final = 400 - (10% de 400) = 360
    # líquido = 4000 - 320 - 360 = 3320
    assert f"{calcular_salario_liquido(4000, 2, False):.2f}" == "3320.00"


def test_irrf_nao_pode_ficar_negativo_com_muitos_dependentes():
    # bruto = 3000; IR base=300; dependentes=10 -> -50% IR = 150
    # líquido = 3000 - 240 - 150 = 2610
    assert f"{calcular_salario_liquido(3000, 10, False):.2f}" == "2610.00"


# ======== VALE-TRANSPORTE ========

def test_vale_transporte_aplica_desconto_de_6_porcento():
    # bruto=3000; INSS=240; IR=300; VT=180
    # líquido=3000-240-300-180=2280
    assert f"{calcular_salario_liquido(3000, 0, True):.2f}" == "2280.00"


def test_sem_vale_transporte_nao_aplica_desconto():
    # mesmo caso acima, mas sem VT
    assert f"{calcular_salario_liquido(3000, 0, False):.2f}" == "2460.00"


# ======== GERAIS ========

def test_resultado_arredondado_para_duas_casas():
    # bruto 3333.33 -> INSS=266.6664, IR=333.333 (10%)
    # líquido=3333.33 - 266.6664 - 333.333 = 2733.3306 -> 2733.33
    resultado = calcular_salario_liquido(3333.33, 0, False)
    assert f"{resultado:.2f}" == "2733.33"
