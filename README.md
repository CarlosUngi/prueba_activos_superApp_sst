# SuperApp SST - Sistema de Salud en el Trabajo

Este proyecto implementa la prueba técnica para el cargo de Backend Developer.
El sistema cuenta con Arquitectura Hexagonal/Limpia en el backend, un pipeline de datos ETL con Pandas, y un frontend interactivo en React.

## Requisitos Previos

- Python 3.10 o superior
- Node.js 18 o superior
- Docker y Docker Compose (para la base de datos PostgreSQL)

## Paso 1: Levantar la Base de Datos

En la raiz del proyecto, inicia la base de datos PostgreSQL mediante Docker:

```bash
docker-compose up -d
```

Asegurate de que el contenedor este corriendo en el puerto 5432.

## Paso 2: Ejecutar el ETL y Poblar Datos

El pipeline de datos lee los CSVs, limpia los datos, y los inserta en la base de datos.

1. Ve a la carpeta del pipeline:
```bash
cd data_pipeline
```
2. Activa el entorno y corre el pipeline:
```bash
source .venv/bin/activate
python run_pipeline.py
```

## Paso 3: Levantar el Backend (FastAPI)

El backend expone la API REST, implementa RBAC y el motor de alertas.

1. Ve a la carpeta del API:
```bash
cd transactional_api
```
2. Activa el entorno:
```bash
source .venv/bin/activate
```
3. Ejecuta el script de inicialización (seed) para crear las tablas base y los usuarios de prueba:
```bash
python seed.py
```
4. Inicia el servidor:
```bash
uvicorn app.main:app --reload
```
La documentacion de la API estara disponible en: http://localhost:8000/docs

## Paso 4: Levantar el Frontend (React)

1. Ve a la carpeta del frontend:
```bash
cd frontend
```
2. Inicia la aplicacion de desarrollo:
```bash
npm run dev
```
La aplicacion estara disponible en: http://localhost:5173

## Usuarios de Prueba (Demo)

Puedes iniciar sesion en el frontend con los siguientes perfiles:

- Perfil HRBP (Lider)
  Email: lider@superapp.com
  Password: 123456

- Perfil Medico SST (Administrador Medico)
  Email: medico@superapp.com
  Password: 123456

Para probar el motor de alertas, ingresa como Medico y agrega incapacidades al EMP-014.
