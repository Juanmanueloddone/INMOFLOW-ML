from fastapi import FastAPI
from pydantic import BaseModel

class VersionInfo(BaseModel):
    service: str
    version: str

app = FastAPI()

@app.get("/", response_model=VersionInfo)
def version():
    return VersionInfo(service="inmoflow-ml", version="0.1.0")
