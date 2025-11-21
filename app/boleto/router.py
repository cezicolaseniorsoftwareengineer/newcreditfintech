from fastapi import APIRouter, Depends, HTTPException, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from uuid import uuid4

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.auth.models import User
from app.boleto.schemas import BoletoConsulta, BoletoDetalhes, PagamentoBoletoRequest, PagamentoResponse
from app.boleto.service import consultar_boleto, processar_pagamento
from app.pix.service import get_saldo

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/ui/boleto", response_class=HTMLResponse)
async def view_boleto(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    saldo = get_saldo(db, current_user.id)
    return templates.TemplateResponse("boleto.html", {
        "request": request,
        "user_name": current_user.nome,
        "saldo": saldo,
        "page": "boleto"
    })


@router.post("/api/boleto/consulta", response_model=BoletoDetalhes)
def api_consultar_boleto(
    dados: BoletoConsulta,
    current_user: User = Depends(get_current_user)
):
    try:
        return consultar_boleto(dados.codigo_barras)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/api/boleto/pagar", response_model=PagamentoResponse)
def api_pagar_boleto(
    dados: PagamentoBoletoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    x_correlation_id: str = Header(default=None)
):
    correlation_id = x_correlation_id or str(uuid4())
    try:
        boleto = processar_pagamento(db, dados, current_user.id, correlation_id)
        return PagamentoResponse(
            id=boleto.id,
            status="SUCESSO",
            mensagem="Pagamento realizado com sucesso",
            comprovante=f"COMP-{boleto.id[:8].upper()}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Erro interno ao processar pagamento")
