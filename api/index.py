# api/index.py
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

class VersionInfo(BaseModel):
    service: str
    version: str

@app.get("/version", response_model=VersionInfo)
def version():
    return VersionInfo(service="inmoflow-ml", version="0.1.0")

# Stub del endpoint de matching para probar que responde
@app.get("/ml/match")
def match(top_k: int = Query(10, ge=1, le=100), buyers: int = Query(1, ge=1, le=1000)):
    # Por ahora devuelve un payload vacío pero válido
    return {"top_k": top_k, "buyers": buyers, "results": []}
