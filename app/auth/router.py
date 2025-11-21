from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.models import User
from app.auth.schemas import UserCreate, UserLogin
from app.auth.service import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from app.core.logger import logger
from uuid import uuid4

router = APIRouter()


@router.post("/register")
def register(response: Response, user: UserCreate, db: Session = Depends(get_db)):  # type: ignore
    db_user = db.query(User).filter((User.email == user.email) | (User.cpf_cnpj == user.cpf_cnpj)).first()  # type: ignore
    if db_user:
        raise HTTPException(status_code=400, detail="Email ou CPF/CNPJ já cadastrado")

    hashed_password = get_password_hash(user.password)
    new_user = User(
        nome=user.nome,
        email=user.email,
        cpf_cnpj=user.cpf_cnpj,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Auto-login after registration
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.cpf_cnpj, "nome": new_user.nome},
        expires_delta=access_token_expires
    )

    # Set cookie with strict security settings
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevent JavaScript access (XSS protection)
        secure=True,    # Only send over HTTPS
        samesite="lax", # CSRF protection
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer", "nome": new_user.nome}
@router.post("/login")
def login(response: Response, user_in: UserLogin, db: Session = Depends(get_db)):  # type: ignore
    user = db.query(User).filter(User.cpf_cnpj == user_in.cpf_cnpj).first()  # type: ignore
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.cpf_cnpj, "nome": user.nome},
        expires_delta=access_token_expires
    )

    # Set cookie with strict security settings
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  # Prevent JavaScript access (XSS protection)
        secure=True,    # Only send over HTTPS
        samesite="lax", # CSRF protection
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {"access_token": access_token, "token_type": "bearer", "nome": user.nome}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}
