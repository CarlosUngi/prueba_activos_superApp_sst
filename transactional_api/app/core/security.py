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
    if not encrypted_text:
        return None
    try:
        return cipher_suite.decrypt(encrypted_text.encode()).decode()
    except Exception:
        return "*** ERROR DESCIFRANDO ***"
