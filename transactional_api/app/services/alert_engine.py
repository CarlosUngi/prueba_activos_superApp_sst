from sqlalchemy.orm import Session
from app.models.domain import Incapacidad, AlertaTemprana
from datetime import datetime, timedelta

def evaluate_high_risk(db: Session, empleado_id: str):
    """
    Regla de Negocio (Pilar B):
    Si acumula más de 2 incapacidades en los últimos 60 días, detonar Alerta de Riesgo Alto.
    """
    fecha_limite = datetime.now().date() - timedelta(days=60)
    
    # Contar incapacidades recientes
    conteo_incapacidades = db.query(Incapacidad).filter(
        Incapacidad.empleado_ref == empleado_id,
        Incapacidad.fecha_inicio_incapacidad >= fecha_limite
    ).count()
    
    if conteo_incapacidades > 2:
        # Verificar si ya existe la alerta para no duplicar en el mismo día
        alerta_existente = db.query(AlertaTemprana).filter(
            AlertaTemprana.empleado_ref == empleado_id,
            AlertaTemprana.fecha_alerta == datetime.now().date()
        ).first()
        
        if not alerta_existente:
            nueva_alerta = AlertaTemprana(
                empleado_ref=empleado_id,
                fecha_alerta=datetime.now().date(),
                motivo=f"Acumulación de {conteo_incapacidades} incapacidades en 60 días",
                nivel_riesgo="ALTO"
            )
            db.add(nueva_alerta)
            db.commit()
            print(f"🚨 ALERTA GATILLADA: Riesgo Alto para {empleado_id}")
