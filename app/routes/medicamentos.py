from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from math import ceil

from app.database import get_db
from app.models import Medicamento
from app.schemas import MedicamentoResponse, MedicamentoListResponse, StatsResponse
from app.auth import get_api_key

router = APIRouter(prefix="/medicamentos", tags=["medicamentos"])


@router.get("", response_model=MedicamentoListResponse)
def list_medicamentos(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    nome: Optional[str] = None,
    principio_ativo: Optional[str] = None,
    classe_terapeutica: Optional[str] = None,
    situacao: Optional[str] = None,
    categoria_regulatoria: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """List medicamentos with pagination and filters"""
    query = db.query(Medicamento)
    
    if nome:
        query = query.filter(Medicamento.nome_produto.ilike(f"%{nome}%"))
    if principio_ativo:
        query = query.filter(Medicamento.principio_ativo.ilike(f"%{principio_ativo}%"))
    if classe_terapeutica:
        query = query.filter(Medicamento.classe_terapeutica.ilike(f"%{classe_terapeutica}%"))
    if situacao:
        query = query.filter(Medicamento.situacao_registro.ilike(f"%{situacao}%"))
    if categoria_regulatoria:
        query = query.filter(Medicamento.categoria_regulatoria.ilike(f"%{categoria_regulatoria}%"))
    
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = ceil(total / limit) if total > 0 else 0
    
    return MedicamentoListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )


@router.get("/{medicamento_id}", response_model=MedicamentoResponse)
def get_medicamento(
    medicamento_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Get medicamento by ID"""
    medicamento = db.query(Medicamento).filter(Medicamento.id == medicamento_id).first()
    if not medicamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medicamento not found"
        )
    return medicamento


@router.get("/search", response_model=MedicamentoListResponse)
def search_medicamentos(
    q: str = Query(..., min_length=1, description="Search term"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Search medicamentos by name or principio ativo"""
    query = db.query(Medicamento).filter(
        or_(
            Medicamento.nome_produto.ilike(f"%{q}%"),
            Medicamento.principio_ativo.ilike(f"%{q}%")
        )
    )
    
    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = ceil(total / limit) if total > 0 else 0
    
    return MedicamentoListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        pages=pages
    )
