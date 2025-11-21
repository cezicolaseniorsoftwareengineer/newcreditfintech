from uuid import uuid4
from sqlalchemy.orm import Session
from app.boleto.models import TransacaoBoleto, StatusBoleto
from app.boleto.schemas import PagamentoBoletoRequest, BoletoDetalhes
from app.pix.service import get_saldo
from app.core.logger import logger, audit_log
from datetime import date, timedelta
import secrets


def consultar_boleto(codigo_barras: str) -> BoletoDetalhes:
    # Mock validation
    if not codigo_barras.isdigit() or len(codigo_barras) < 44:
        raise ValueError("Código de barras inválido")

    if codigo_barras.endswith("0000"):
        raise ValueError("Boleto vencido ou não encontrado")

    # Mock details
    return BoletoDetalhes(
        codigo_barras=codigo_barras,
        beneficiario=f"Empresa Mock {secrets.randbelow(100) + 1} LTDA",
        valor=float(f"{secrets.randbelow(491) + 10}.{secrets.randbelow(100)}"),
        vencimento=date.today() + timedelta(days=secrets.randbelow(10) + 1)
    )


def processar_pagamento(
    db: Session,
    dados: PagamentoBoletoRequest,
    user_id: str,
    correlation_id: str
) -> TransacaoBoleto:

    saldo = get_saldo(db, user_id)
    if saldo < dados.valor:
        raise ValueError("Saldo insuficiente")

    boleto = TransacaoBoleto(
        id=str(uuid4()),
        valor=dados.valor,
        codigo_barras=dados.codigo_barras,
        descricao=dados.descricao,
        status=StatusBoleto.PAGO,
        user_id=user_id,
        correlation_id=correlation_id
    )

    db.add(boleto)
    db.commit()
    db.refresh(boleto)

    audit_log(
        action="boleto_pago",
        user=user_id,
        resource=f"boleto_id={boleto.id}",
        details={
            "correlation_id": correlation_id,
            "valor": dados.valor,
            "codigo_barras": dados.codigo_barras
        }
    )

    logger.info(f"Boleto pago: id={boleto.id}, valor={dados.valor}")
    return boleto
