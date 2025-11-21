from sqlalchemy import Float, String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import enum
from app.core.database import Base


class StatusBoleto(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    FALHOU = "FALHOU"


class TransacaoBoleto(Base):
    __tablename__ = "transacoes_boleto"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    codigo_barras: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String(500), nullable=True)
    status: Mapped[StatusBoleto] = mapped_column(Enum(StatusBoleto), nullable=False, default=StatusBoleto.PENDENTE)
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    correlation_id: Mapped[str] = mapped_column(String(100), nullable=True)
