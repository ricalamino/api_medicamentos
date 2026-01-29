from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class MedicamentoBase(BaseModel):
    tipo_produto: Optional[str] = None
    nome_produto: Optional[str] = None
    data_finalizacao_processo: Optional[date] = None
    categoria_regulatoria: Optional[str] = None
    numero_registro_produto: Optional[str] = None
    data_vencimento_registro: Optional[date] = None
    numero_processo: Optional[str] = None
    classe_terapeutica: Optional[str] = None
    empresa_detentora_registro: Optional[str] = None
    situacao_registro: Optional[str] = None
    principio_ativo: Optional[str] = None


class MedicamentoCreate(MedicamentoBase):
    pass


class MedicamentoResponse(MedicamentoBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MedicamentoListResponse(BaseModel):
    items: list[MedicamentoResponse]
    total: int
    page: int
    limit: int
    pages: int


class APIKeyCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)


class APIKeyResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class APIKeyCreateResponse(BaseModel):
    id: int
    key: str
    name: str
    is_active: bool
    created_at: datetime
    message: str = "Save this key securely. It will not be shown again."

    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    total_medicamentos: int
    por_situacao: dict[str, int]
    por_categoria: dict[str, int]
