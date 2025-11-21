"""
Pydantic schemas for fraud analysis.
Enforces strict input validation and format constraints.
"""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class TransacaoAntifraude(BaseModel):
    """Fraud analysis request payload."""
    valor: float = Field(..., gt=0, description="Transaction value (R$)")
    horario: str = Field(..., description="Transaction time (HH:MM)")
    tentativas_ultimas_24h: int = Field(..., ge=0, description="Attempts in last 24h")
    tipo_transacao: str = Field(default="PIX", description="Transaction type")
    origem: Optional[str] = Field(None, description="Transaction origin")

    @field_validator('horario')
    @classmethod
    def validar_horario(cls, v: str) -> str:
        """Validates time format (HH:MM) and logical constraints."""
        try:
            hour, minute = map(int, v.split(':'))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError
            return v
        except Exception:
            raise ValueError('Invalid time format. Use HH:MM')

    @field_validator('tentativas_ultimas_24h')
    @classmethod
    def validar_tentativas(cls, v: int) -> int:
        """Sanity check for attempt counters to prevent integer overflow or DoS."""
        if v > 100:
            raise ValueError('Number of attempts exceeds reasonable limit')
        return v


class ResultadoAntifraude(BaseModel):
    """Fraud analysis result payload."""
    score: int = Field(..., ge=0, le=100, description="Risk Score (0-100)")
    aprovado: bool = Field(..., description="Approval status")
    motivo: str = Field(..., description="Decision reason")
    regras_ativadas: List[str] = Field(..., description="Rules contributing to score")
    nivel_risco: str = Field(..., description="Risk Level: BAIXO, MEDIO, ALTO")
    recomendacao: str = Field(..., description="Action recommendation")
