from sqlalchemy import Column, Integer, String, Date, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Medicamento(Base):
    __tablename__ = "medicamentos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_produto = Column(String(100))
    nome_produto = Column(String(500))
    data_finalizacao_processo = Column(Date, nullable=True)
    categoria_regulatoria = Column(String(100), nullable=True)
    numero_registro_produto = Column(String(50), nullable=True)
    data_vencimento_registro = Column(Date, nullable=True)
    numero_processo = Column(String(100), nullable=True)
    classe_terapeutica = Column(String(500), nullable=True)
    empresa_detentora_registro = Column(Text, nullable=True)
    situacao_registro = Column(String(100), nullable=True)
    principio_ativo = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
