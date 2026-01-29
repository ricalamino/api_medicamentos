from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/medicamentos_db")
    secret_key: str = os.getenv("SECRET_KEY", "change-me-in-production")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")

    class Config:
        env_file = ".env"


settings = Settings()

# Ensure UTF-8 encoding in connection
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"client_encoding": "utf8"} if 'postgresql' in settings.database_url else {},
    echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
