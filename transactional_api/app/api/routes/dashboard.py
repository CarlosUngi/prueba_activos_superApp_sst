from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.domain import Incapacidad, AlertaTemprana
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) # Ambos roles pueden entrar
):
    """
    PILAR C: Dashboard
    Devuelve datos estadísticos agregados que no violan la confidencialidad.
    """
    # 1. Total de días de ausencia históricos
    total_dias = db.query(func.sum(Incapacidad.dias_ausencia)).scalar() or 0
    
    # 2. Empleados con Alertas Tempranas activas
    alertas = db.query(AlertaTemprana).count()
    
    # 3. Top departamentos con ausentismo (Simulado en la BD actual cruzando tablas)
    # Para simplicidad, agruparemos por Categoria de Salud
    ausentismo_categoria = db.query(
        Incapacidad.categoria_salud,
        func.sum(Incapacidad.dias_ausencia).label("total_dias")
    ).group_by(Incapacidad.categoria_salud).all()
    
    categorias = [{"categoria": r[0], "dias": r[1]} for r in ausentismo_categoria]

    return {
        "rol_actual": current_user.rol,
        "metricas": {
            "total_dias_ausencia": total_dias,
            "casos_riesgo_alto": alertas,
            "ausentismo_por_categoria": categorias
        }
    }
