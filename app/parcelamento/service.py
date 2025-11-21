"""
Business logic for installment calculation.
Implements Price Table (compound interest) and Total Effective Cost (CET) algorithms.
"""
import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.parcelamento.models import SimulacaoParcelamento
from app.parcelamento.schemas import SimulacaoRequest
from app.core.logger import logger, audit_log


def calcular_parcelas(dados: SimulacaoRequest) -> Dict[str, Any]:
    """
    Calculates amortization schedule using the Price Table method.
    Returns monthly installment, total payable amount, annualized CET, and detailed amortization breakdown.

    Formula: PMT = PV * [(1+i)^n * i] / [(1+i)^n - 1]
    """
    valor = dados.valor
    parcelas = dados.parcelas
    taxa = dados.taxa_mensal

    # Installment calculation (Price Table)
    fator = (1 + taxa) ** parcelas
    parcela = valor * (taxa * fator) / (fator - 1)

    # Amortization schedule generation
    amortizacao: List[Dict[str, Any]] = []
    saldo = valor

    for i in range(parcelas):
        juros = saldo * taxa
        principal = parcela - juros
        saldo -= principal

        # Avoid negative balance due to floating point rounding
        if saldo < 0.01:
            saldo = 0

        amortizacao.append({
            "mes": i + 1,
            "parcela": round(parcela, 2),
            "juros": round(juros, 2),
            "principal": round(principal, 2),
            "saldo": round(saldo, 2)
        })

    # CET (Total Effective Cost) calculation - Annualized
    total_pago = parcela * parcelas
    cet_mensal = (total_pago / valor) ** (1 / parcelas) - 1
    cet_anual = ((1 + cet_mensal) ** 12 - 1) * 100

    logger.info(f"Simulação calculada: valor={valor}, parcelas={parcelas}, parcela={round(parcela, 2)}")

    return {
        "parcela": round(parcela, 2),
        "total_pago": round(total_pago, 2),
        "cet_anual": round(cet_anual, 2),
        "tabela": amortizacao
    }


def salvar_simulacao(
    db: Session,
    dados: SimulacaoRequest,
    resultado: Dict[str, Any],
    correlation_id: str
) -> SimulacaoParcelamento:
    """
    Persists simulation results for audit trails and historical analysis.
    """
    simulacao = SimulacaoParcelamento(
        valor=dados.valor,
        parcelas=dados.parcelas,
        taxa_mensal=dados.taxa_mensal,
        valor_parcela=resultado["parcela"],
        total_pago=resultado["total_pago"],
        cet_anual=resultado["cet_anual"],
        tabela_amortizacao=json.dumps(resultado["tabela"]),
        correlation_id=correlation_id
    )

    db.add(simulacao)
    db.commit()
    db.refresh(simulacao)

    audit_log(
        action="simulacao_parcelamento",
        user="sistema",
        resource=f"simulacao_id={simulacao.id}",
        details={"correlation_id": correlation_id, "valor": dados.valor, "parcelas": dados.parcelas}
    )

    logger.info(f"Simulação persistida: id={simulacao.id}")

    return simulacao
