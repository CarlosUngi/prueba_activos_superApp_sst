from sqlalchemy.orm import Session
from app.models.domain import Incapacidad, AlertaTemprana, EncuestaSintoma
from datetime import datetime, timedelta

def evaluate_high_risk(db: Session, empleado_id: str):
    """
    Pilar B: Motor de Correlación (Regla de Negocio SST)
    Cruza información de dos fuentes distintas para detectar un riesgo alto.
    """
    hoy = datetime.now().date()
    hace_90_dias = hoy - timedelta(days=90)
    hace_180_dias = hoy - timedelta(days=180)
    
    # 1. Obtener los datos del empleado
    conteo_incapacidades = db.query(Incapacidad).filter(
        Incapacidad.empleado_ref == empleado_id,
        Incapacidad.fecha_inicio_incapacidad >= hace_90_dias
    ).count()
    
    ultima_encuesta = db.query(EncuestaSintoma).filter(
        EncuestaSintoma.codigo_empleado == empleado_id,
        EncuestaSintoma.fecha_encuesta >= hace_180_dias
    ).order_by(EncuestaSintoma.fecha_encuesta.desc()).first()

    alertas_a_crear = []

    # REGLA 1: Correlación (Ausentismo recurrente + Dolor severo)
    if conteo_incapacidades > 1 and ultima_encuesta and ultima_encuesta.nivel_dolor_percibido and ultima_encuesta.nivel_dolor_percibido >= 7:
        alertas_a_crear.append({
            "motivo": f"Correlación Detectada: {conteo_incapacidades} incapacidades recientes y dolor crónico (Nivel {ultima_encuesta.nivel_dolor_percibido}). Acción sugerida: Programar examen médico ocupacional.",
            "nivel": "ALTO"
        })

    # REGLA 2: Petición Directa y Urgente
    if ultima_encuesta and ultima_encuesta.requiere_valoracion_medica == True:
        alertas_a_crear.append({
            "motivo": "Intervención Urgente: El empleado solicitó expresamente valoración médica en su última encuesta. Acción sugerida: Contactar inmediatamente para agendamiento.",
            "nivel": "CRÍTICO"
        })

    alertas_generadas = []

    # Guardar las alertas (verificando que no se dupliquen el mismo día para el mismo motivo)
    for alerta_data in alertas_a_crear:
        alerta_existente = db.query(AlertaTemprana).filter(
            AlertaTemprana.empleado_ref == empleado_id,
            AlertaTemprana.fecha_alerta == hoy,
            AlertaTemprana.motivo == alerta_data["motivo"]
        ).first()
        
        if not alerta_existente:
            nueva_alerta = AlertaTemprana(
                empleado_ref=empleado_id,
                fecha_alerta=hoy,
                motivo=alerta_data["motivo"],
                nivel_riesgo=alerta_data["nivel"]
            )
            db.add(nueva_alerta)
            alertas_generadas.append({
                "nivel": alerta_data["nivel"],
                "motivo": alerta_data["motivo"]
            })
            print(f"🚨 ALERTA GATILLADA: {alerta_data['nivel']} para {empleado_id}")
            
    if alertas_generadas:
        db.commit()
        
    return alertas_generadas
