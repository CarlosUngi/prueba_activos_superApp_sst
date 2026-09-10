import pandas as pd
from sqlalchemy import create_engine
from cryptography.fernet import Fernet
from config import DATABASE_URI, FERNET_KEY

# Instanciar el encriptador de Fernet
cipher_suite = Fernet(FERNET_KEY.encode())

def encrypt_column(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Encripta todos los valores de una columna usando Fernet"""
    df = df.copy()
    if col_name in df.columns:
        def _encrypt_val(val):
            if pd.isna(val) or val == "":
                return None
            return cipher_suite.encrypt(str(val).encode()).decode()
            
        df[col_name] = df[col_name].apply(_encrypt_val)
    return df

def load_to_postgres(df: pd.DataFrame, table_name: str):
    """Carga un DataFrame a PostgreSQL"""
    engine = create_engine(DATABASE_URI)
    try:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"✅ Datos cargados exitosamente en la tabla: {table_name} ({len(df)} registros)")
    except Exception as e:
        print(f"❌ Error al cargar datos en {table_name}: {e}")

