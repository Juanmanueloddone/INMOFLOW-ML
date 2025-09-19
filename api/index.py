# api/index.py
from fastapi import FastAPI, APIRouter

app = FastAPI()

# Defino un router "base" con las rutas reales
base = APIRouter()

@base.get("/health")
def health():
    return {"ok": True}

@base.get("/version")
def version():
    return {"version": "1.0.0"}

@base.post("/match")
def match_endpoint(payload: dict):
    # Import perezoso para evitar problemas de import al arrancar
    from .ml.match import run_match  # ajustá el import si tu función está en otro módulo
    return run_match(payload)

# 1) Montado sin prefijo -> /health, /version, /match
app.include_router(base)

# 2) Montado con prefijo /api -> /api/health, /api/version, /api/match
app.include_router(base, prefix="/api")
