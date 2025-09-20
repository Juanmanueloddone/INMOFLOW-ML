# api/index.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlencode
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # abrimos para probar; luego limitá a tus dominios
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/version")
def version():
    return {"version": "1.0.0"}

@app.post("/match")
def match_endpoint(payload: dict = Body(default={})):
    # Import tardío para evitar problemas en cold start / resolución de paquetes
    try:
        # tu handler está en api/ml/match.py
        from api.ml.match import handler
    except Exception as e:
        return {"ok": False, "error": f"import_error: {e.__class__.__name__}: {e}"}

    # Adapter minimal: construye un objeto con .query_string (lo que espera tu handler)
    class Req:
        def __init__(self, qs: str):
            self.query_string = qs  # puede ser str; tu handler ya tolera bytes/str

    qs = urlencode(payload or {})  # enviamos el JSON como query-string para el handler
    req = Req(qs)

    try:
        status, headers, body = handler(req)   # tu handler devuelve (status, headers, body_str)
        try:
            data = json.loads(body) if isinstance(body, (str, bytes)) else body
        except Exception:
            data = {"raw": body}
        return {"ok": status == 200, "status": status, "data": data}
    except Exception as e:
        return {"ok": False, "error": f"runtime_error: {e.__class__.__name__}: {e}"}
