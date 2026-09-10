from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.domain import Incapacidad, Usuario, EncuestaSintoma
from app.schemas.api_schemas import IncapacidadResponse, IncapacidadCreate, EncuestaResponse
from app.api.dependencies import require_roles, get_current_user
from app.core.security import decrypt_medical_data, encrypt_medical_data
from app.services.alert_engine import evaluate_high_risk

router = APIRouter()

@router.get("/{emp_id}/history", response_model=List[IncapacidadResponse])
def get_medical_history(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["MEDICO_SST", "MEDICO_OCUPACIONAL", "ADMIN_SST"]))
):
    """
    PILAR A: RBAC
    Retorna la historia de incapacidades.
    Endpoint restringido estrictamente para el rol Médico y sus homólogos.
    LIDER_HRBP y similares recibirán un error 403 Forbidden.
    """
    registros = db.query(Incapacidad).filter(Incapacidad.empleado_ref == emp_id).all()
    
    resultados_seguros = []
    for reg in registros:
        datos = {
            "cod_registro": reg.cod_registro,
            "empleado_ref": reg.empleado_ref,
            "fecha_inicio_incapacidad": reg.fecha_inicio_incapacidad,
            "dias_ausencia": reg.dias_ausencia,
            "codigo_cie10": reg.codigo_cie10,
            "categoria_salud": reg.categoria_salud,
            "entidad_expedidora": reg.entidad_expedidora,
            "diagnostico_medico_confidencial": decrypt_medical_data(reg.diagnostico_medico_confidencial)
        }
        resultados_seguros.append(datos)
        
    return resultados_seguros


@router.post("/{emp_id}/incapacities", status_code=201)
def create_incapacity(
    emp_id: str,
    incapacidad: IncapacidadCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["MEDICO_SST", "MEDICO_OCUPACIONAL", "ADMIN_SST"]))
):
    """
    PILAR B: Motor de alertas
    Registra incapacidad y detona regla de negocio sincrónicamente para devolver las notificaciones al Frontend.
    """
    from datetime import datetime
    import uuid
    
    # 1. Guardar la incapacidad real en la base de datos
    nuevo_id = f"INC-MANUAL-{str(uuid.uuid4())[:6]}"
    
    nueva_inc = Incapacidad(
        cod_registro=nuevo_id,
        empleado_ref=emp_id,
        fecha_inicio_incapacidad=incapacidad.fecha_inicio_incapacidad,
        dias_ausencia=incapacidad.dias_ausencia,
        codigo_cie10=incapacidad.codigo_cie10,
        diagnostico_medico_confidencial=encrypt_medical_data(incapacidad.diagnostico_medico_confidencial),
        categoria_salud=incapacidad.categoria_salud,
        entidad_expedidora=incapacidad.entidad_expedidora
    )
    db.add(nueva_inc)
    db.commit()
    db.refresh(nueva_inc)
    
    # 2. Invocamos el Motor de Correlación Sincrónicamente
    alertas_generadas = evaluate_high_risk(db, emp_id)
    
    return {
        "message": "Incapacidad registrada exitosamente.",
        "incapacidad_id": nuevo_id,
        "alertas_detonadas": alertas_generadas
    }

@router.get("/{emp_id}/surveys", response_model=List[EncuestaResponse])
def get_employee_surveys(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["MEDICO_SST", "MEDICO_OCUPACIONAL", "ADMIN_SST"]))
):
    """
    Retorna el listado de encuestas de síntomas diligenciadas por el empleado.
    Restringido únicamente al rol Médico y sus homólogos.
    """
    encuestas = db.query(EncuestaSintoma).filter(EncuestaSintoma.codigo_empleado == emp_id).all()
    return encuestas
