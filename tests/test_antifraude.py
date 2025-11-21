"""
Unit tests for Anti-Fraud module.
Validates risk rules and scoring logic using data-driven tests.
"""
import pytest
from app.antifraude.schemas import TransacaoAntifraude
from app.antifraude.rules import (
    MotorAntifraude,
    RegraHorarioNoturno,
    RegraValorAlto,
    RegraTentativasExcessivas
)


@pytest.mark.parametrize("valor, horario, tentativas, esperado_aprovado, esperado_risco", [
    (50.0, "14:30", 1, True, "BAIXO"),
    (350.0, "14:00", 1, True, "MEDIO"),  # High value only (+30)
    (1500.0, "23:00", 5, False, "ALTO"),  # All rules (+30+40+50 = 120 -> 100)
])
def test_analise_risco_cenarios(valor: float, horario: str, tentativas: int, esperado_aprovado: bool, esperado_risco: str):
    """
    Data-driven test for risk analysis scenarios.
    Covers Low, Medium, and High risk cases.
    """
    motor = MotorAntifraude()
    transacao = TransacaoAntifraude(
        valor=valor,
        horario=horario,
        tentativas_ultimas_24h=tentativas,
        origem=None
    )

    resultado = motor.analisar(transacao)

    assert resultado["aprovado"] is esperado_aprovado
    assert resultado["nivel_risco"] == esperado_risco


@pytest.mark.parametrize("horario, esperado", [
    ("23:30", True),  # Night
    ("04:00", True),  # Early morning
    ("14:00", False),  # Afternoon
    ("06:01", False),  # Edge case
])
def test_regra_horario_noturno(horario: str, esperado: bool):
    """Validates Night Time Rule boundary conditions."""
    regra = RegraHorarioNoturno()
    transacao = TransacaoAntifraude(
        valor=100.0,
        horario=horario,
        tentativas_ultimas_24h=1,
        origem=None
    )
    assert regra.avaliar(transacao) is esperado


def test_regra_valor_alto():
    """Validates High Value Rule activation."""
    regra = RegraValorAlto(limite=300.0)

    # Value above limit
    transacao_alta = TransacaoAntifraude(
        valor=500.0,
        horario="10:00",
        tentativas_ultimas_24h=1,
        origem=None
    )
    assert regra.avaliar(transacao_alta) is True

    # Value below limit
    transacao_baixa = TransacaoAntifraude(
        valor=200.0,
        horario="10:00",
        tentativas_ultimas_24h=1,
        origem=None
    )
    assert regra.avaliar(transacao_baixa) is False


def test_regra_tentativas_excessivas():
    """Validates Excessive Attempts Rule activation."""
    regra = RegraTentativasExcessivas(limite=3)

    # Excessive attempts
    transacao_excessiva = TransacaoAntifraude(
        valor=100.0,
        horario="10:00",
        tentativas_ultimas_24h=5,
        origem=None
    )
    assert regra.avaliar(transacao_excessiva) is True

    # Normal attempts
    transacao_normal = TransacaoAntifraude(
        valor=100.0,
        horario="10:00",
        tentativas_ultimas_24h=2,
        origem=None
    )
    assert regra.avaliar(transacao_normal) is False


def test_score_acumulado():
    """Verifies correct score accumulation from multiple rules."""
    motor = MotorAntifraude()

    transacao = TransacaoAntifraude(
        valor=400.0,  # +30 points
        horario="01:00",  # +40 points
        tentativas_ultimas_24h=1,
        origem=None
    )

    resultado = motor.analisar(transacao)

    # Score should be 70 (30 + 40)
    assert resultado["score"] == 70
    assert len(resultado["regras_ativadas"]) == 2


def test_validacao_horario_invalido():
    """Validates rejection of invalid time format."""
    with pytest.raises(Exception):
        TransacaoAntifraude(
            valor=100.0,
            horario="25:00",  # Invalid time
            tentativas_ultimas_24h=1,
            origem=None
        )


def test_multiplas_regras_ativadas():
    """Verifies simultaneous activation of multiple rules."""
    motor = MotorAntifraude()

    transacao = TransacaoAntifraude(
        valor=350.0,  # Activates high value rule
        horario="23:00",  # Activates night time rule
        tentativas_ultimas_24h=4,  # Activates excessive attempts rule
        origem=None
    )

    resultado = motor.analisar(transacao)

    assert len(resultado["regras_ativadas"]) == 3
    assert resultado["score"] == 100  # Capped at 100
