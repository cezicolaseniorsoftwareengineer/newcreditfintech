from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.auth.models import User
from app.auth.schemas import UserCreate, UserLogin
from app.auth.service import get_password_hash, verify_password, create_access_token
from datetime import timedelta
from app.core.config import settings
from authlib.integrations.starlette_client import OAuth  # type: ignore
from app.core.logger import logger
from uuid import uuid4

router = APIRouter()

# OAuth Configuration
oauth = OAuth()
oauth.register(  # type: ignore
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


@router.get("/google/login")
async def google_login(request: Request):  # type: ignore
    """Redirects user to Google for authentication."""
    redirect_uri = request.url_for('google_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)  # type: ignore


@router.get("/google/callback")
async def google_callback(request: Request, response: Response, db: Session = Depends(get_db)):
    """Handles the callback from Google."""
    try:
        token = await oauth.google.authorize_access_token(request)  # type: ignore
        user_info = token.get('userinfo')  # type: ignore

        if not user_info:
            # Fallback if userinfo is not in token (depends on provider config)
            user_info = await oauth.google.userinfo(token=token)  # type: ignore

        email = user_info.get('email')  # type: ignore
        name = user_info.get('name')  # type: ignore
        google_sub = user_info.get('sub')  # type: ignore

        if not email:
            raise HTTPException(status_code=400, detail="Google did not return an email address.")

        # Check if user exists
        user = db.query(User).filter(User.email == email).first()  # type: ignore

        if not user:
            # Auto-register user
            # Note: We don't have CPF/CNPJ from Google.
            # We will generate a placeholder to satisfy the DB constraint.
            # In a real app, we would redirect to a "Finish Registration" page.
            placeholder_cpf = f"GOOGLE_{google_sub}"[:20]  # Limit to 20 chars

            # Check if this placeholder already exists (unlikely but possible)
            if db.query(User).filter(User.cpf_cnpj == placeholder_cpf).first():  # type: ignore
                placeholder_cpf = f"G_{uuid4().hex}"[:20]

            new_user = User(
                nome=name,
                email=email,
                cpf_cnpj=placeholder_cpf,
                hashed_password=get_password_hash(uuid4().hex)  # Random password
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
            logger.info(f"New user auto-registered via Google: {email}")
        else:
            logger.info(f"User logged in via Google: {email}")

        # Create Access Token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.cpf_cnpj, "nome": user.nome},
            expires_delta=access_token_expires
        )

        # Set cookie with strict security settings
        response = RedirectResponse(url="/")
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,  # Prevent JavaScript access (XSS protection)
            secure=True,    # Only send over HTTPS
            samesite="lax", # CSRF protection
            max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        return response

    except Exception as e:
        logger.error(f"Google Auth Error: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")


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
