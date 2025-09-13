# api/index.py
from fastapi import FastAPI
from typing import List, Dict

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}

@app.get("/version")
def version() -> Dict[str, str]:
    return {"service": "inmoflow-ml", "version": "0.1.0"}

# demo super simple (luego lo cambiamos por el real)
@app.get("/ml/match")
def match(top_k: int = 5, buyers: int = 1) -> Dict[str, object]:
    dummy = [{"comprador_id": i+1, "propiedad_id": j+1, "score": 0.9 - 0.01*j}
             for i in range(buyers) for j in range(top_k)]
    return {"results": dummy}
