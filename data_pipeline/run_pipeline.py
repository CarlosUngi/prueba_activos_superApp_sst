import pandas as pd
import os
import sys

# Agregar el directorio actual al path para importar módulos correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transform import process_empleados, process_incapacidades, process_encuestas, check_not_null, check_foreign_key
from load import load_to_postgres, encrypt_column

def filter_and_quarantine(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """Filtra registros malos, los guarda en un log y devuelve los buenos listos para BD"""
    df['errores_validacion'] = df['errores_validacion'].fillna("")
    df_invalid = df[df['errores_validacion'] != ""]
    df_valid = df[df['errores_validacion'] == ""]
    
    if not df_invalid.empty:
        log_path = os.path.join(os.path.dirname(__file__), "cuarentena_errores.txt")
        print(f"⚠️ Se encontraron {len(df_invalid)} registros inválidos en {source_name}. Enviando a cuarentena...")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"\n--- ERRORES EN ARCHIVO: {source_name} ---\n")
            for _, row in df_invalid.iterrows():
                # Extraemos solo los datos de negocio (quitando las columnas de control)
                datos_registro = row.drop(['numero_fila', 'errores_validacion']).to_dict()
                
                f.write(f"Fila {row['numero_fila']} | Motivo: {row['errores_validacion']}\n")
                f.write(f"Registro completo: {datos_registro}\n")
                f.write("-" * 80 + "\n")
    
    # Eliminamos las columnas de tracking de los datos buenos para que no explote la BD
    return df_valid.drop(columns=['numero_fila', 'errores_validacion'])

def main():
    print("🚀 Iniciando Pipeline de Datos ETL...")
    
    # Rutas a los CSV en la raíz del proyecto (../data/)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    empleados_path = os.path.join(data_dir, "RAW_BD_EMPLEADOS.csv")
    incapacidades_path = os.path.join(data_dir, "RAW_HISTORICO_INCAPACIDADES_CONFIDENCIAL.csv")
    encuestas_path = os.path.join(data_dir, "RAW_ENCUESTAS_SINTOMAS_PELIGROS.csv")

    valid_employee_ids = set()

    # 1. EMPLEADOS
    print("\nProcesando Empleados...")
    if os.path.exists(empleados_path):
        df_emp = pd.read_csv(empleados_path)
        df_emp_clean = process_empleados(df_emp)
        df_emp_clean = check_not_null(df_emp_clean, 'ID_Empleado') # Validar PK
        
        df_emp_valid = filter_and_quarantine(df_emp_clean, "RAW_BD_EMPLEADOS.csv")
        
        # Guardamos la lista de empleados válidos para la integridad referencial
        valid_employee_ids = set(df_emp_valid['ID_Empleado'].dropna().unique())
        
        # Estandarizar nombre de columnas para PostgreSQL (minúsculas)
        df_emp_valid.columns = df_emp_valid.columns.str.lower()
        load_to_postgres(df_emp_valid, 'empleados')
    else:
        print(f"⚠️ Archivo no encontrado: {empleados_path}")

    # 2. INCAPACIDADES
    print("\nProcesando Incapacidades...")
    if os.path.exists(incapacidades_path):
        df_inc = pd.read_csv(incapacidades_path)
        df_inc_clean = process_incapacidades(df_inc)
        
        # Validaciones de BD
        df_inc_clean = check_not_null(df_inc_clean, 'COD_REGISTRO') # PK
        df_inc_clean = check_foreign_key(df_inc_clean, 'EMPLEADO_REF', valid_employee_ids) # FK
        
        df_inc_valid = filter_and_quarantine(df_inc_clean, "RAW_HISTORICO_INCAPACIDADES_CONFIDENCIAL.csv")
        
        # *** ENCRIPTACIÓN ***
        # El requerimiento dice enmascarar DIAGNOSTICO_MEDICO_CONFIDENCIAL
        df_inc_secured = encrypt_column(df_inc_valid, 'DIAGNOSTICO_MEDICO_CONFIDENCIAL')
        
        df_inc_secured.columns = df_inc_secured.columns.str.lower()
        load_to_postgres(df_inc_secured, 'incapacidades')
    else:
        print(f"⚠️ Archivo no encontrado: {incapacidades_path}")

    # 3. ENCUESTAS
    print("\nProcesando Encuestas...")
    if os.path.exists(encuestas_path):
        df_enc = pd.read_csv(encuestas_path)
        df_enc_clean = process_encuestas(df_enc)
        
        # Validaciones de BD
        df_enc_clean = check_not_null(df_enc_clean, 'ID_RESPUESTA') # PK
        df_enc_clean = check_foreign_key(df_enc_clean, 'CODIGO_EMPLEADO', valid_employee_ids) # FK
        
        df_enc_valid = filter_and_quarantine(df_enc_clean, "RAW_ENCUESTAS_SINTOMAS_PELIGROS.csv")
        df_enc_valid.columns = df_enc_valid.columns.str.lower()
        load_to_postgres(df_enc_valid, 'encuestas_sintomas')
    else:
        print(f"⚠️ Archivo no encontrado: {encuestas_path}")

    print("\n🎉 Pipeline finalizado exitosamente!")

if __name__ == "__main__":
    main()
