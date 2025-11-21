from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.auth.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Extracts the current user from the access_token cookie.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Token format: "Bearer <token>"
        scheme, _, param = token.partition(" ")
        if not param:
            param = scheme  # Handle case where "Bearer " might be missing or different

        payload = jwt.decode(param, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        cpf_cnpj = payload.get("sub")
        if not cpf_cnpj or not isinstance(cpf_cnpj, str):
            raise credentials_exception
    except JWTError:  # type: ignore
        raise credentials_exception

    user = db.query(User).filter(User.cpf_cnpj == cpf_cnpj).first()
    if not user:
        raise credentials_exception

    return user
