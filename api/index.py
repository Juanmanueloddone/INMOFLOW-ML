# api/index.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS abierto para probar; luego lo cerramos a tus dominios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
def match_endpoint(payload: dict = Body(...)):
    # import tardío para evitar problemas de carga
    try:
        from ml.match import run_match  # <- paquete de raíz, no relativo
    except Exception as e:
        # devolvemos JSON legible en vez de 500 para no volvernos locos
        return {"ok": False, "error": f"import_error: {e.__class__.__name__}: {e}"}
    try:
        result = run_match(payload)
        return result
    except Exception as e:
        return {"ok": False, "error": f"runtime_error: {e.__class__.__name__}: {e}"}
