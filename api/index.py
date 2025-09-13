# api/index.py
from fastapi import FastAPI

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version")
def version():
    return {"service": "inmoflow_ml", "version": "0.1.0"}
