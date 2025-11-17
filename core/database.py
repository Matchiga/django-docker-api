from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
from decouple import config
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = (
    f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}"
    f"@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=config('DEBUG', default=False, cast=bool),  # Log SQL em desenvolvimento
    pool_size=10,           # Número de conexões no pool
    max_overflow=20,        # Conexões extras permitidas
    pool_pre_ping=True,     # Verifica conexão antes de usar
    pool_recycle=3600,      # Recicla conexões após 1 hora
)

session_factory = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
SessionLocal = scoped_session(session_factory)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Banco de dados PostgreSQL inicializado com sucesso!")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        raise


def reset_database():
    if config('DEBUG', default=False, cast=bool):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        logger.warning("🔄 Banco de dados resetado!")
    else:
        raise Exception("❌ Reset de banco não permitido em produção!")
