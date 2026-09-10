from passlib.context import CryptContext
from cryptography.fernet import Fernet
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, ALGORITHM, FERNET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
cipher_suite = Fernet(FERNET_KEY.encode())

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decrypt_medical_data(encrypted_text: str) -> str:
    """Desencripta un dato usando Fernet."""
    if not encrypted_text or not isinstance(encrypted_text, str):
        return ""
    try:
        return cipher_suite.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return encrypted_text  # Si no está encriptado (insertado por defecto), devolvemos el texto plano

def encrypt_medical_data(plain_text: str) -> str:
    """Encripta un dato usando Fernet."""
    if not plain_text:
        return ""
    return cipher_suite.encrypt(plain_text.encode()).decode()
