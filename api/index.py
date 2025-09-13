# api/index.py
from fastapi import FastAPI, Query
from pydantic import BaseModel

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

class VersionInfo(BaseModel):
    service: str = "inmoflow-ml"
    version: str = "0.1.0"

@app.get("/version", response_model=VersionInfo)
def version():
    return VersionInfo()

@app.get("/ml/match")
def match(
    top_k: int = Query(10, ge=1, le=100),
    buyers: int = Query(1, ge=1, le=1000),
):
    return {"top_k": top_k, "buyers": buyers, "results": []}
