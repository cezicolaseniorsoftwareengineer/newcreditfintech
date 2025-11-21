"""
Unit tests for Installment module.
Validates compound interest calculation, CET, and persistence.
"""
import pytest
from app.parcelamento.service import calcular_parcelas
from app.parcelamento.schemas import SimulacaoRequest


def test_calculo_parcelamento_basico():
    """Tests basic installment calculation."""
    dados = SimulacaoRequest(
        valor=1000.0,
        parcelas=12,
        taxa_mensal=0.035
    )

    resultado = calcular_parcelas(dados)

    assert resultado["parcela"] > 0
    assert resultado["total_pago"] > 1000.0
    assert resultado["cet_anual"] > 0
    assert len(resultado["tabela"]) == 12


def test_primeira_parcela_juros():
    """Validates interest calculation for the first installment."""
    dados = SimulacaoRequest(
        valor=1000.0,
        parcelas=12,
        taxa_mensal=0.035
    )

    resultado = calcular_parcelas(dados)
    primeira = resultado["tabela"][0]

    # Interest of first installment = initial balance * rate
    assert abs(primeira["juros"] - 35.0) < 0.01
    assert primeira["mes"] == 1


def test_saldo_final_zero():
    """Verifies that the final balance is zero after all installments."""
    dados = SimulacaoRequest(
        valor=5000.0,
        parcelas=24,
        taxa_mensal=0.02
    )

    resultado = calcular_parcelas(dados)
    ultima = resultado["tabela"][-1]

    assert ultima["saldo"] == 0.0


def test_total_pago_maior_que_valor():
    """Total paid must be greater than principal (due to interest)."""
    dados = SimulacaoRequest(
        valor=2000.0,
        parcelas=10,
        taxa_mensal=0.05
    )

    resultado = calcular_parcelas(dados)

    assert resultado["total_pago"] > 2000.0


def test_validacao_valor_negativo():
    """Validates rejection of negative value."""
    with pytest.raises(Exception):
        SimulacaoRequest(
            valor=-100.0,
            parcelas=12,
            taxa_mensal=0.035
        )


def test_validacao_taxa_excessiva():
    """Validates rejection of excessive interest rate."""
    with pytest.raises(Exception):
        SimulacaoRequest(
            valor=1000.0,
            parcelas=12,
            taxa_mensal=0.20  # 20% - above limit
        )


def test_parcelas_decrescentes():
    """Verifies that installments have decreasing balance."""
    dados = SimulacaoRequest(
        valor=3000.0,
        parcelas=6,
        taxa_mensal=0.03
    )

    resultado = calcular_parcelas(dados)

    for i in range(len(resultado["tabela"]) - 1):
        assert resultado["tabela"][i]["saldo"] > resultado["tabela"][i + 1]["saldo"]
