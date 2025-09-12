from fastapi import FastAPI
from .schemas import VersionInfo


app = FastAPI(title="InmoFlow ML API", version="0.1.0")


@app.get("/health")
def health():
return {"status": "ok"}


@app.get("/version", response_model=VersionInfo)
def version():
return VersionInfo(service="inmoflow-ml", version="0.1.0")
