from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Medicamento
from app.schemas import StatsResponse
from app.auth import get_api_key

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """Get statistics about medicamentos"""
    total = db.query(Medicamento).count()
    
    # Stats by situacao
    situacao_stats = db.query(
        Medicamento.situacao_registro,
        func.count(Medicamento.id).label("count")
    ).group_by(Medicamento.situacao_registro).all()
    
    por_situacao = {situacao or "N/A": count for situacao, count in situacao_stats}
    
    # Stats by categoria
    categoria_stats = db.query(
        Medicamento.categoria_regulatoria,
        func.count(Medicamento.id).label("count")
    ).group_by(Medicamento.categoria_regulatoria).all()
    
    por_categoria = {categoria or "N/A": count for categoria, count in categoria_stats}
    
    return StatsResponse(
        total_medicamentos=total,
        por_situacao=por_situacao,
        por_categoria=por_categoria
    )
