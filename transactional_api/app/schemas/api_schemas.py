from pydantic import BaseModel
from typing import Optional
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str

class IncapacidadBase(BaseModel):
    fecha_inicio_incapacidad: date
    dias_ausencia: float
    codigo_cie10: Optional[str] = None
    diagnostico_medico_confidencial: Optional[str] = None
    categoria_salud: Optional[str] = None
    entidad_expedidora: Optional[str] = None

class IncapacidadCreate(IncapacidadBase):
    pass

class IncapacidadResponse(IncapacidadBase):
    cod_registro: str
    empleado_ref: str
    
    class Config:
        from_attributes = True

class EmpleadoResponse(BaseModel):
    id_empleado: str
    nombre_completo: str
    area_trabajo: Optional[str]
    cargo: Optional[str]

    class Config:
        from_attributes = True

class EncuestaResponse(BaseModel):
    id_respuesta: str
    codigo_empleado: str
    fecha_encuesta: date
    sintoma_principal: Optional[str] = None
    peligro_identificado: Optional[str] = None
    nivel_dolor_percibido: Optional[float] = None
    requiere_valoracion_medica: Optional[bool] = None

    class Config:
        from_attributes = True
