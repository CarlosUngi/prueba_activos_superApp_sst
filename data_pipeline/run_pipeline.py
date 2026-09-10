import pandas as pd
import os
import sys

# Agregar el directorio actual al path para importar módulos correctamente
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from transform import process_empleados, process_incapacidades, process_encuestas
from load import load_to_postgres, encrypt_column

def main():
    print("🚀 Iniciando Pipeline de Datos ETL...")
    
    # Rutas a los CSV (asumiendo que están en ../data/)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    
    empleados_path = os.path.join(data_dir, "RAW_BD_EMPLEADOS.csv")
    incapacidades_path = os.path.join(data_dir, "RAW_HISTORICO_INCAPACIDADES_CONFIDENCIAL.csv")
    encuestas_path = os.path.join(data_dir, "RAW_ENCUESTAS_SINTOMAS_PELIGROS.csv")
    
    # 1. EMPLEADOS
    print("\nProcesando Empleados...")
    if os.path.exists(empleados_path):
        df_emp = pd.read_csv(empleados_path)
        df_emp_clean = process_empleados(df_emp)
        # Estandarizar nombre de columnas para PostgreSQL (minúsculas)
        df_emp_clean.columns = df_emp_clean.columns.str.lower()
        load_to_postgres(df_emp_clean, 'empleados')
    else:
        print(f"⚠️ Archivo no encontrado: {empleados_path}")

    # 2. INCAPACIDADES
    print("\nProcesando Incapacidades...")
    if os.path.exists(incapacidades_path):
        df_inc = pd.read_csv(incapacidades_path)
        df_inc_clean = process_incapacidades(df_inc)
        
        # *** ENCRIPTACIÓN ***
        # El requerimiento dice enmascarar DIAGNOSTICO_MEDICO_CONFIDENCIAL
        df_inc_secured = encrypt_column(df_inc_clean, 'DIAGNOSTICO_MEDICO_CONFIDENCIAL')
        
        df_inc_secured.columns = df_inc_secured.columns.str.lower()
        load_to_postgres(df_inc_secured, 'incapacidades')
    else:
        print(f"⚠️ Archivo no encontrado: {incapacidades_path}")

    # 3. ENCUESTAS
    print("\nProcesando Encuestas...")
    if os.path.exists(encuestas_path):
        df_enc = pd.read_csv(encuestas_path)
        df_enc_clean = process_encuestas(df_enc)
        df_enc_clean.columns = df_enc_clean.columns.str.lower()
        load_to_postgres(df_enc_clean, 'encuestas_sintomas')
    else:
        print(f"⚠️ Archivo no encontrado: {encuestas_path}")

    print("\n🎉 Pipeline finalizado exitosamente!")

if __name__ == "__main__":
    main()
