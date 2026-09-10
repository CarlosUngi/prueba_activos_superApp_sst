from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.database.session import get_db
from app.models.domain import Incapacidad, Usuario
from app.schemas.api_schemas import IncapacidadResponse, IncapacidadCreate
from app.api.dependencies import require_roles, get_current_user
from app.core.security import decrypt_medical_data
from app.services.alert_engine import evaluate_high_risk

router = APIRouter()

@router.get("/{emp_id}/history", response_model=List[IncapacidadResponse])
def get_medical_history(
    emp_id: str,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    PILAR A: RBAC
    Retorna la historia de incapacidades.
    Si el rol es LIDER_HRBP, enmascara el diagnóstico.
    Si el rol es MEDICO_SST, lo desencripta y lo muestra en claro.
    """
    registros = db.query(Incapacidad).filter(Incapacidad.empleado_ref == emp_id).all()
    
    # Procesar resultados en memoria según el rol
    resultados_seguros = []
    for reg in registros:
        # Copiamos el objeto para no mutar el estado de SQLAlchemy accidentalmente
        datos = {
            "cod_registro": reg.cod_registro,
            "empleado_ref": reg.empleado_ref,
            "fecha_inicio_incapacidad": reg.fecha_inicio_incapacidad,
            "dias_ausencia": reg.dias_ausencia,
            "codigo_cie10": reg.codigo_cie10,
            "categoria_salud": reg.categoria_salud,
            "entidad_expedidora": reg.entidad_expedidora,
            "diagnostico_medico_confidencial": "*** ENMASCARADO ***" # Por defecto
        }
        
        if current_user.rol == "MEDICO_SST":
            # Desencriptar solo para médicos
            datos["diagnostico_medico_confidencial"] = decrypt_medical_data(reg.diagnostico_medico_confidencial)
            
        resultados_seguros.append(datos)
        
    return resultados_seguros


@router.post("/{emp_id}/incapacities", status_code=201)
def create_incapacity(
    emp_id: str,
    incapacidad: IncapacidadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_roles(["MEDICO_SST"])) # Solo médicos pueden crear
):
    """
    PILAR B: Motor de alertas
    Registra incapacidad y detona regla de negocio en Background.
    """
    from datetime import datetime
    import uuid
    
    # En un sistema real, la inserción iría aquí (y encriptaríamos el dato antes de guardar).
    # Simularemos la inserción para el ejercicio:
    nuevo_id = f"INC-MANUAL-{str(uuid.uuid4())[:4]}"
    
    # Invocamos el Motor de Correlación asíncronamente para que la API responda en 10ms
    background_tasks.add_task(evaluate_high_risk, db, emp_id)
    
    return {"message": "Incapacidad registrada. Motor de alertas en ejecución asíncrona."}
