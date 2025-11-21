from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class BoletoConsulta(BaseModel):
    codigo_barras: str = Field(..., min_length=44, max_length=48, description="Código de barras ou linha digitável")


class BoletoDetalhes(BaseModel):
    codigo_barras: str
    beneficiario: str
    valor: float
    vencimento: date
    status: str = "PENDENTE"


class PagamentoBoletoRequest(BaseModel):
    codigo_barras: str
    valor: float
    descricao: Optional[str] = "Pagamento de Boleto"


class PagamentoResponse(BaseModel):
    id: str
    status: str
    mensagem: str
    comprovante: str
