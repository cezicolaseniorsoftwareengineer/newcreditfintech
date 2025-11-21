"""
Database connection management and ORM session factory.
Supports dialect abstraction for SQLite and PostgreSQL.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.logger import logger

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite specific: check_same_thread=False is required for FastAPI's concurrent execution model
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Yields a thread-safe database session context. Ensures connection closure upon completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Idempotent initialization of database schema artifacts."""
    logger.info("Iniciando criação de tabelas no banco de dados")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas com sucesso")
