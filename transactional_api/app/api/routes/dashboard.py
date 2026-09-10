from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.session import get_db
from app.models.domain import Incapacidad, AlertaTemprana
from app.api.dependencies import require_roles

router = APIRouter()

TODOS_LOS_ROLES = [
    "LIDER_HRBP", "LIDER_AREA", "RELACIONES_LABORALES", 
    "MEDICO_SST", "MEDICO_OCUPACIONAL", "ADMIN_SST"
]

@router.get("/metrics")
def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(TODOS_LOS_ROLES))
):
    """
    PILAR C: Dashboard
    Devuelve datos estadísticos agregados que no violan la confidencialidad.
    """
    # 1. Total de días de ausencia históricos
    total_dias = db.query(func.sum(Incapacidad.dias_ausencia)).scalar() or 0
    
    # 2. Empleados con Alertas Tempranas activas
    alertas = db.query(AlertaTemprana).count()
    
    # 3. Top departamentos con ausentismo
    # Para simplicidad, agruparemos por Categoria de Salud
    ausentismo_categoria = db.query(
        Incapacidad.categoria_salud,
        func.sum(Incapacidad.dias_ausencia).label("total_dias")
    ).group_by(Incapacidad.categoria_salud).all()
    
    categorias = [{"categoria": r[0], "dias": r[1]} for r in ausentismo_categoria]

    # 4. Cálculo de Casos Activos vs Cerrados
    from datetime import datetime, timedelta
    hoy = datetime.now().date()
    todas_incapacidades = db.query(Incapacidad.fecha_inicio_incapacidad, Incapacidad.dias_ausencia).all()
    
    casos_activos = 0
    casos_cerrados = 0
    
    for inc in todas_incapacidades:
        if inc.fecha_inicio_incapacidad and inc.dias_ausencia:
            fecha_fin = inc.fecha_inicio_incapacidad + timedelta(days=int(inc.dias_ausencia))
            if fecha_fin >= hoy:
                casos_activos += 1
            else:
                casos_cerrados += 1

    return {
        "rol_actual": current_user.rol,
        "metricas": {
            "total_dias_ausencia": total_dias,
            "casos_riesgo_alto": alertas,
            "casos_activos": casos_activos,
            "casos_cerrados": casos_cerrados,
            "ausentismo_por_categoria": categorias
        }
    }

@router.get("/alerts_details")
def get_detailed_alerts(
    db: Session = Depends(get_db),
    current_user = Depends(require_roles(["MEDICO_SST", "MEDICO_OCUPACIONAL", "ADMIN_SST"]))
):
    """
    Retorna el listado completo de alertas tempranas con nombre del empleado.
    Solo para el Doctor/Admin.
    """
    from app.models.domain import Empleado
    
    # Hacer JOIN de Alertas con Empleados para traer el nombre
    resultados = db.query(AlertaTemprana, Empleado).join(
        Empleado, AlertaTemprana.empleado_ref == Empleado.id_empleado
    ).order_by(AlertaTemprana.fecha_alerta.desc()).all()
    
    lista_alertas = []
    for alerta, empleado in resultados:
        lista_alertas.append({
            "id_alerta": alerta.id,
            "fecha_alerta": alerta.fecha_alerta,
            "empleado_id": empleado.id_empleado,
            "nombre_empleado": empleado.nombre_completo,
            "cargo": empleado.cargo,
            "nivel_riesgo": alerta.nivel_riesgo,
            "motivo": alerta.motivo
        })
        
    return lista_alertas
