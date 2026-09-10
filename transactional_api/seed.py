import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import engine, SessionLocal, Base
from app.models.domain import Usuario, AlertaTemprana
from app.core.security import get_password_hash

def seed_db():
    print("Creando tablas base (incluyendo alertas y usuarios)...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Verificando si existen usuarios...")
    if db.query(Usuario).count() == 0:
        print("Insertando usuarios de prueba...")
        lider = Usuario(
            email="lider@superapp.com",
            hashed_password=get_password_hash("123456"),
            rol="LIDER_HRBP"
        )
        medico = Usuario(
            email="medico@superapp.com",
            hashed_password=get_password_hash("123456"),
            rol="MEDICO_SST"
        )
        db.add_all([lider, medico])
        db.commit()
        print("✅ Usuarios 'lider@superapp.com' y 'medico@superapp.com' creados (Clave: 123456)")
    else:
        print("Los usuarios ya existen.")
    db.close()

if __name__ == "__main__":
    seed_db()
