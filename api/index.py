# api/index.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"version": "1.0.0"}  # poné el que quieras

@app.post("/match")
def match_endpoint(payload: dict):
    # Import perezoso Y relativo: asegura que cargue desde api/ml
    from .ml.match import run_match  # <-- ajustá al nombre real de tu función
    return run_match(payload)
