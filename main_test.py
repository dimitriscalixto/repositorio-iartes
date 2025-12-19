import pytest

from main_refatorado import calcular_salario_liquido

def test_salario_zero_deve_gerar_erro():
    with pytest.raises((ValueError, AssertionError)):
        calcular_salario_liquido(0)


def test_salario_negativo_deve_gerar_erro():
    with pytest.raises((ValueError, AssertionError)):
        calcular_salario_liquido(-1)


def test_inss_deve_ser_8_porcento_quando_nao_bate_teto():
    resultado = calcular_salario_liquido(1000)
    assert f"{resultado:.2f}" == "920.00"


def test_inss_deve_ser_limitado_a_500_no_teto_exato():
    resultado = calcular_salario_liquido(6250)
    assert f"{resultado:.2f}" == "5125.00"


def test_inss_deve_ficar_em_500_quando_salario_ultrapassa_o_teto():
    resultado = calcular_salario_liquido(7000)
    assert f"{resultado:.2f}" == "5800.00"


def test_irrf_deve_ser_isento_ate_2000_inclusive():
    resultado = calcular_salario_liquido(2000)
    assert f"{resultado:.2f}" == "1840.00"


def test_irrf_deve_ser_10_porcento_sobre_total_quando_acima_de_2000():
    resultado = calcular_salario_liquido(2500)
    assert f"{resultado:.2f}" == "2050.00"


def test_resultado_deve_ser_arredondado_para_duas_casas_decimais():
    resultado = calcular_salario_liquido(3333.33)
    assert f"{resultado:.2f}" == "2733.33"
