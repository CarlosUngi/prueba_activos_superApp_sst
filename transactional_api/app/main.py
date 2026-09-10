import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, medical, dashboard

app = FastAPI(
    title="SuperApp SST API",
    description="API Transaccional para Salud y Seguridad en el Trabajo",
    version="1.0.0"
)

# CORS para conectar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se restringe a localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de Auditoría y Tiempos
@app.middleware("http")
async def audit_log_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    print(f"INFO: {request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    
    return response

# Registro de Rutas
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(medical.router, prefix="/api/employees", tags=["Historias Médicas"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "Bienvenido a la API de la SuperApp SST. Ve a /docs para la documentación."}
