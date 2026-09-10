import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER", "superapp_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "superapp_password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "superapp_sst")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# JWT Settings
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_jwt_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Fernet Key para campos sensibles
FERNET_KEY = os.getenv("FERNET_KEY")
