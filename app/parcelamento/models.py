"""
Data models for installment simulations.
Persists historical data for audit and analytics.
"""
from sqlalchemy import Integer, Float, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
from app.core.database import Base


class SimulacaoParcelamento(Base):
    """Entity representing a performed installment simulation."""

    __tablename__ = "simulacoes_parcelamento"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    parcelas: Mapped[int] = mapped_column(Integer, nullable=False)
    taxa_mensal: Mapped[float] = mapped_column(Float, nullable=False)
    valor_parcela: Mapped[float] = mapped_column(Float, nullable=False)
    total_pago: Mapped[float] = mapped_column(Float, nullable=False)
    cet_anual: Mapped[float] = mapped_column(Float, nullable=False)
    tabela_amortizacao: Mapped[str] = mapped_column(Text, nullable=False)  # Serialized JSON
    criado_em: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    correlation_id: Mapped[str] = mapped_column(String(100), index=True, nullable=True)

    def __repr__(self):
        return f"<SimulacaoParcelamento(id={self.id}, valor={self.valor}, parcelas={self.parcelas})>"
