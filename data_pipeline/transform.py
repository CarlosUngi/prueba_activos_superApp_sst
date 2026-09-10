import pandas as pd
import numpy as np
import re

# ==========================================
# FUNCIONES PURAS DE LIMPIEZA (ETL)
# ==========================================

def _extract_id(val):
    """Extrae números y formatea a EMP-XXX"""
    if pd.isna(val): return np.nan
    val_str = str(val)
    match = re.search(r'(\d+)', val_str)
    if match:
        num = int(match.group(1))
        return f"EMP-{num:03d}"
    return val_str

def clean_employee_ids(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Estandariza los IDs de empleado"""
    df = df.copy()
    if col_name in df.columns:
        df[col_name] = df[col_name].apply(_extract_id)
    return df

def clean_strings_capitalize(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Convierte strings a Capitalize eliminando espacios en los extremos"""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.capitalize()
            # Reemplazar string 'Nan' generados por astype
            df[col] = df[col].replace({'Nan': np.nan, 'None': np.nan})
    return df

def parse_dates_standard(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Unifica formatos de fecha a YYYY-MM-DD"""
    df = df.copy()
    for col in columns:
        if col in df.columns:
            # dayfirst=True ayuda con los formatos DD/MM/YYYY
            df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce').dt.date
    return df

def extract_numeric_days(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Extrae solo el número de campos como '2 dias', '15'"""
    df = df.copy()
    if col_name in df.columns:
        df[col_name] = df[col_name].astype(str).str.extract(r'(\d+)')[0].astype(float)
    return df

def map_boolean_values(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Mapea valores variados a True/False"""
    df = df.copy()
    if col_name in df.columns:
        mapping = {
            'si': True, 's': True, '1': True, 'yes': True,
            'no': False, 'n': False, '0': False
        }
        # A minúsculas y quitar espacios para mapear seguro
        df[col_name] = df[col_name].astype(str).str.lower().str.strip().map(mapping)
    return df

def map_pain_levels(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Mapea niveles de dolor en texto a escala numérica (1-10)"""
    df = df.copy()
    if col_name in df.columns:
        def _convert_pain(val):
            val_str = str(val).lower().strip()
            if val_str == 'bajo': return 3
            if val_str == 'medio': return 5
            if val_str == 'alto': return 8
            # Si es numérico, intentamos retornarlo
            try:
                return float(val)
            except ValueError:
                return np.nan
        df[col_name] = df[col_name].apply(_convert_pain)
    return df

# ==========================================
# PIPELINES PRINCIPALES POR ARCHIVO
# ==========================================

def process_empleados(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(clean_employee_ids, 'ID_Empleado')
          .pipe(clean_strings_capitalize, ['Area_Trabajo', 'Cargo'])
          .pipe(parse_dates_standard, ['Fecha_Ingreso'])
    )

def process_incapacidades(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(clean_employee_ids, 'EMPLEADO_REF')
          .pipe(parse_dates_standard, ['FECHA_INICIO_INCAPACIDAD'])
          .pipe(extract_numeric_days, 'DIAS_AUSENCIA')
          .pipe(clean_strings_capitalize, ['CATEGORIA_SALUD', 'ENTIDAD_EXPEDIDORA'])
    )

def process_encuestas(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(clean_employee_ids, 'CODIGO_EMPLEADO')
          .pipe(parse_dates_standard, ['FECHA_ENCUESTA'])
          .pipe(map_pain_levels, 'NIVEL_DOLOR_PERCIBIDO')
          .pipe(map_boolean_values, 'REQUIERE_VALORACION_MEDICA')
          .pipe(clean_strings_capitalize, ['SINTOMA_PRINCIPAL', 'PELIGRO_IDENTIFICADO'])
    )
