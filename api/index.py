# api/index.py
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

class VersionInfo(BaseModel):
    service: str
    version: str

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/version", response_model=VersionInfo)
def version():
    return VersionInfo(
        service="InmoFlow ML API",
        version=os.getenv("IMAGE_VERSION", "0.1.0")
    )
