import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Credenciales DB
DB_USER = os.getenv("DB_USER", "superapp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "superapp_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "superapp_sst")

# URI para SQLAlchemy
DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Llave de encriptación (Fernet)
FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    raise ValueError("FERNET_KEY no está configurada en las variables de entorno.")
