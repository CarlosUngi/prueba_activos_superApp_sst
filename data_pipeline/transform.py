import pandas as pd
import numpy as np
import re

# ==========================================
# FUNCIONES PURAS DE LIMPIEZA (ETL)
# ==========================================

def init_error_tracking(df: pd.DataFrame) -> pd.DataFrame:
    """Inicializa las columnas para tracking de errores"""
    df = df.copy()
    # Guardamos el índice original como número de fila (sumamos 2 para coincidir con Excel/CSV con header)
    df['numero_fila'] = df.index + 2 
    df['errores_validacion'] = ""
    return df

def _extract_id(val):
    if pd.isna(val): return np.nan
    val_str = str(val)
    match = re.search(r'(\d+)', val_str)
    if match:
        num = int(match.group(1))
        return f"EMP-{num:03d}"
    return val_str

def clean_employee_ids(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    if col_name in df.columns:
        original = df[col_name].astype(str)
        df[col_name] = df[col_name].apply(_extract_id)
        
        failed_mask = df[col_name].isna() & (original != 'nan') & (original != '')
        if failed_mask.any():
            df.loc[failed_mask, 'errores_validacion'] += "[ID '" + original[failed_mask] + "'] inválido "
    return df

def clean_strings_capitalize(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.capitalize()
            df[col] = df[col].replace({'Nan': np.nan, 'None': np.nan})
    return df

def parse_dates_standard(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    df = df.copy()
    for col in columns:
        if col in df.columns:
            original = df[col].astype(str)
            parsed = pd.to_datetime(df[col], format='mixed', dayfirst=True, errors='coerce').dt.date
            
            failed_mask = df[col].notna() & (df[col] != '') & parsed.isna()
            if failed_mask.any():
                df.loc[failed_mask, 'errores_validacion'] += "[Fecha '" + original[failed_mask] + f"' no procesable en {col}] "
            
            df[col] = parsed
    return df

def extract_numeric_days(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    if col_name in df.columns:
        original = df[col_name].astype(str)
        extracted = df[col_name].astype(str).str.extract(r'(\d+)')[0].astype(float)
        
        failed_mask = df[col_name].notna() & (df[col_name] != '') & extracted.isna()
        if failed_mask.any():
            df.loc[failed_mask, 'errores_validacion'] += "[Valor '" + original[failed_mask] + f"' no numérico en {col_name}] "
        
        df[col_name] = extracted
    return df

def map_boolean_values(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    if col_name in df.columns:
        original = df[col_name].astype(str)
        mapping = {
            'si': True, 's': True, '1': True, 'yes': True,
            'no': False, 'n': False, '0': False
        }
        df[col_name] = df[col_name].astype(str).str.lower().str.strip().map(mapping)
        
        failed_mask = df[col_name].isna() & (original != 'nan') & (original != '')
        if failed_mask.any():
            df.loc[failed_mask, 'errores_validacion'] += "[Booleano '" + original[failed_mask] + f"' no reconocido en {col_name}] "
    return df

def map_pain_levels(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df = df.copy()
    if col_name in df.columns:
        def _convert_pain(val):
            val_str = str(val).lower().strip()
            if val_str == 'bajo': return 3
            if val_str == 'medio': return 5
            if val_str == 'alto': return 8
            try:
                return float(val)
            except ValueError:
                return np.nan
                
        original = df[col_name].astype(str)
        df[col_name] = df[col_name].apply(_convert_pain)
        
        failed_mask = df[col_name].isna() & (original != 'nan') & (original != '')
        if failed_mask.any():
            df.loc[failed_mask, 'errores_validacion'] += "[Nivel de dolor '" + original[failed_mask] + f"' no mapeable en {col_name}] "
        
    return df

def check_not_null(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """Verifica que un campo obligatorio (como la PK) no esté vacío"""
    df = df.copy()
    if col_name in df.columns:
        missing = df[col_name].isna() | (df[col_name].astype(str).str.strip() == '') | (df[col_name].astype(str) == 'nan')
        if missing.any():
            df.loc[missing, 'errores_validacion'] += f"[{col_name} es obligatorio y está vacío] "
    return df

def check_foreign_key(df: pd.DataFrame, col_name: str, valid_ids: set) -> pd.DataFrame:
    """Verifica que los IDs existan en el DataFrame maestro (Integridad Referencial)"""
    df = df.copy()
    if col_name in df.columns:
        missing = ~df[col_name].isin(valid_ids) & df[col_name].notna() & (df[col_name].astype(str).str.strip() != '')
        if missing.any():
            df.loc[missing, 'errores_validacion'] += "[Referencia Huérfana: ID '" + df.loc[missing, col_name].astype(str) + "'] no existe en empleados "
    return df

# ==========================================
# PIPELINES PRINCIPALES POR ARCHIVO
# ==========================================

def process_empleados(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(init_error_tracking)
          .pipe(clean_employee_ids, 'ID_Empleado')
          .pipe(clean_strings_capitalize, ['Area_Trabajo', 'Cargo'])
          .pipe(parse_dates_standard, ['Fecha_Ingreso'])
    )

def process_incapacidades(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(init_error_tracking)
          .pipe(clean_employee_ids, 'EMPLEADO_REF')
          .pipe(parse_dates_standard, ['FECHA_INICIO_INCAPACIDAD'])
          .pipe(extract_numeric_days, 'DIAS_AUSENCIA')
          .pipe(clean_strings_capitalize, ['CATEGORIA_SALUD', 'ENTIDAD_EXPEDIDORA'])
    )

def process_encuestas(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.pipe(init_error_tracking)
          .pipe(clean_employee_ids, 'CODIGO_EMPLEADO')
          .pipe(parse_dates_standard, ['FECHA_ENCUESTA'])
          .pipe(map_pain_levels, 'NIVEL_DOLOR_PERCIBIDO')
          .pipe(map_boolean_values, 'REQUIERE_VALORACION_MEDICA')
          .pipe(clean_strings_capitalize, ['SINTOMA_PRINCIPAL', 'PELIGRO_IDENTIFICADO'])
    )
