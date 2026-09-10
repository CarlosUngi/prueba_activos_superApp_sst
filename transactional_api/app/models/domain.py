from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from app.database.session import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    rol = Column(String) # 'LIDER_HRBP' o 'MEDICO_SST'

class Empleado(Base):
    __tablename__ = "empleados"
    id_empleado = Column(String, primary_key=True, index=True)
    nombre_completo = Column(String)
    area_trabajo = Column(String)
    cargo = Column(String)
    fecha_ingreso = Column(Date)

class Incapacidad(Base):
    __tablename__ = "incapacidades"
    cod_registro = Column(String, primary_key=True, index=True)
    empleado_ref = Column(String, ForeignKey("empleados.id_empleado"))
    fecha_inicio_incapacidad = Column(Date)
    dias_ausencia = Column(Float)
    codigo_cie10 = Column(String)
    diagnostico_medico_confidencial = Column(String) # Guardado encriptado
    categoria_salud = Column(String)
    entidad_expedidora = Column(String)

class EncuestaSintoma(Base):
    __tablename__ = "encuestas_sintomas"
    id_respuesta = Column(String, primary_key=True, index=True)
    codigo_empleado = Column(String, ForeignKey("empleados.id_empleado"))
    fecha_encuesta = Column(Date)
    sintoma_principal = Column(String)
    peligro_identificado = Column(String)
    nivel_dolor_percibido = Column(Float)
    requiere_valoracion_medica = Column(Boolean)

class AlertaTemprana(Base):
    __tablename__ = "alertas_tempranas"
    id = Column(Integer, primary_key=True, index=True)
    empleado_ref = Column(String, ForeignKey("empleados.id_empleado"))
    fecha_alerta = Column(Date)
    motivo = Column(String)
    nivel_riesgo = Column(String) # 'ALTO'
