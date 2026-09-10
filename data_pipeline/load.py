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

def load_to_postgres(df: pd.DataFrame, table_name: str, pk_col: str):
    """Carga un DataFrame a PostgreSQL de forma idempotente (evitando duplicados)"""
    engine = create_engine(DATABASE_URI)
    try:
        # Extraer los IDs existentes en la base de datos
        try:
            existing_ids = pd.read_sql(f"SELECT {pk_col} FROM {table_name}", engine)[pk_col].tolist()
        except Exception:
            existing_ids = []  # Si la tabla no existe o hay error, asumimos vacía
            
        # Filtrar el DataFrame para dejar solo los registros nuevos
        if existing_ids:
            # Asegurar que ambos lados sean del mismo tipo (string) para la comparación
            df_new = df[~df[pk_col].astype(str).isin([str(i) for i in existing_ids])]
        else:
            df_new = df
            
        if df_new.empty:
            print(f"La tabla {table_name} ya está al día. (0 registros nuevos)")
            return
            
        df_new.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Datos cargados exitosamente en la tabla: {table_name} ({len(df_new)} registros nuevos)")
    except Exception as e:
        print(f"Error al cargar datos en {table_name}: {e}")

