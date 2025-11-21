"""
Pydantic schemas for input/output validation.
Enforces strict type checking and boundary constraints.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List
from datetime import datetime


class ParcelaAmortizacao(BaseModel):
    """Represents a single row in the amortization schedule."""
    mes: int = Field(..., ge=1, description="Month number")
    parcela: float = Field(..., gt=0, description="Installment value")
    juros: float = Field(..., ge=0, description="Interest amount")
    principal: float = Field(..., ge=0, description="Principal amortization")
    saldo: float = Field(..., ge=0, description="Remaining balance")


class SimulacaoRequest(BaseModel):
    """Installment simulation request payload."""
    valor: float = Field(..., gt=0, le=1000000, description="Principal amount")
    parcelas: int = Field(..., ge=1, le=360, description="Number of installments")
    taxa_mensal: float = Field(..., gt=0, le=0.15, description="Monthly interest rate (decimal)")

    @field_validator('taxa_mensal')
    @classmethod
    def validar_taxa(cls, v: float) -> float:
        if v > 0.15:  # 15% monthly is a practical limit
            raise ValueError('Monthly rate cannot exceed 15%')
        return v


class SimulacaoResponse(BaseModel):
    """Simulation result payload."""
    parcela: float = Field(..., description="Monthly installment value")
    total_pago: float = Field(..., description="Total payable amount")
    cet_anual: float = Field(..., description="Annualized Total Effective Cost (%)")
    tabela: List[ParcelaAmortizacao] = Field(..., description="Full amortization schedule")
    simulacao_id: int = Field(..., description="Persisted simulation ID")
    criado_em: datetime = Field(..., description="Simulation timestamp")

    model_config = ConfigDict(from_attributes=True)
