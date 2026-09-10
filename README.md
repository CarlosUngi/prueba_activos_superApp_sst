# SuperApp SST & Salud Ocupacional

Prototipo funcional para el área de Salud y Seguridad en el Trabajo, desarrollado como parte de la evaluación técnica para el rol de Lead Architect / Fullstack.

## 🏗️ Arquitectura del Proyecto

El proyecto está diseñado bajo una **Arquitectura de Capas orientada a microservicios**, priorizando la separación de responsabilidades y la seguridad de los datos confidenciales (RBAC).

*   **`db/`**: Infraestructura (PostgreSQL 16 en Docker).
*   **`data_pipeline/`**: Microservicio ETL basado en el **Paradigma Funcional** con Pandas. Extrae, limpia, estandariza y encripta (Fernet) los CSV originales antes de insertarlos en BD.
*   **`transactional_api/`**: Backend Transaccional (FastAPI). Expone los endpoints protegidos con JWT. Implementa el Pilar A (Roles) y el Pilar B (Motor de Alertas en segundo plano).
*   **`frontend/`**: Single Page Application (React 18 + Vite + TailwindCSS v4). Consume la API y muestra dashboards y datos según el nivel de autorización (Pilar C).

## 🚀 Instrucciones de Ejecución Local

### 1. Base de Datos
```bash
cd db
sudo docker compose up -d
```
*(Nota: Si usaste volúmenes antiguos en el puerto 5432, asegúrate de limpiarlos con `docker compose down -v` primero).*

### 2. Ejecutar el Data Pipeline (ETL)
Limpiará los CSV, encriptará los diagnósticos y poblará la base de datos.
```bash
cd data_pipeline
source ../.venv/bin/activate
python run_pipeline.py
```

### 3. Levantar la API Transaccional (Backend)
```bash
cd transactional_api
source ../.venv/bin/activate
uvicorn app.main:app --reload
```
La API estará disponible en `http://localhost:8000`. Swagger en `/docs`.

### 4. Levantar el Frontend (Dashboard)
En una nueva terminal:
```bash
cd frontend
npm run dev
```
La aplicación web estará disponible en `http://localhost:5173`.

---

## 🔐 Credenciales de Prueba (Demo)

El script `seed.py` del backend ya creó estos usuarios con diferentes roles para probar el Pilar A (RBAC):

1.  **Líder HRBP (Solo ve métricas agregadas y datos censurados)**
    *   Usuario: `lider@superapp.com`
    *   Clave: `123456`
2.  **Médico SST (Acceso total y desencriptación en tiempo real)**
    *   Usuario: `medico@superapp.com`
    *   Clave: `123456`

---

## 🚧 Avance Actual y Tareas Pendientes (TODO)

✅ **Completado:**
*   Infraestructura Dockerizada.
*   Pipeline ETL Funcional (limpieza de inconsistencias).
*   Backend de FastAPI (Seguridad JWT, Endpoints, Background Tasks).
*   Frontend Dashboard (React, Tailwind, Recharts, Renderizado Condicional por Rol).

⏳ **Pendiente para la próxima sesión:**
*   **Frontend - Pilar B:** Agregar un botón/formulario en el Dashboard de React (solo visible para Médicos) para registrar una nueva incapacidad. Esto permitirá simular y detonar en vivo la alerta de "Riesgo Alto" durante la demostración al equipo evaluador.

---

## 🤖 Contexto de Antigravity (Para uso interno)

*Si necesitas continuar este desarrollo mañana usando el CLI de Antigravity, usa el siguiente comando para retomar la sesión con todo el contexto intacto:*

```bash
agy --conversation 9bf8cfb3-15f7-468b-b9e3-d75d14587b41
```
