"""
Data models for PIX transactions.
Supports idempotency, state tracking, and audit trails.
"""
from sqlalchemy import Float, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import enum
from app.core.database import Base


class StatusPix(str, enum.Enum):
    """Enumeration of valid transaction states."""
    CRIADO = "CRIADO"
    PROCESSANDO = "PROCESSANDO"
    CONFIRMADO = "CONFIRMADO"
    FALHOU = "FALHOU"
    CANCELADO = "CANCELADO"
    AGENDADO = "AGENDADO"


class TipoTransacao(str, enum.Enum):
    """Type of transaction."""
    ENVIADO = "ENVIADO"
    RECEBIDO = "RECEBIDO"


class TransacaoPix(Base):
    """Entity representing a PIX transaction with idempotency constraints."""

    __tablename__ = "transacoes_pix"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)  # UUID
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    chave_pix: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tipo_chave: Mapped[str] = mapped_column(String(20), nullable=False)  # CPF, EMAIL, TELEFONE, ALEATORIA
    tipo: Mapped[TipoTransacao] = mapped_column(Enum(TipoTransacao), nullable=False, default=TipoTransacao.ENVIADO)
    status: Mapped[StatusPix] = mapped_column(Enum(StatusPix), nullable=False, default=StatusPix.CRIADO, index=True)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)  # Foreign Key to User
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=True)
    data_agendamento: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TransacaoPix(id={self.id}, valor={self.valor}, status={self.status}, tipo={self.tipo})>"
