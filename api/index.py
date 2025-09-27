# api/index.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from .schemas import MatchV2Request, MatchV2Response  # usamos el contrato v2 como único

# --- sub-app real que expone /api ---
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # abrimos para probar; luego limitá a tus dominios
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.get("/health")
def health():
    return {"ok": True}

@api_app.get("/version")
def version():
    return {"version": "1.0.0"}

# ÚNICA ruta de matching en prod (ML real)
@api_app.post("/match", response_model=MatchV2Response)
def match(payload: MatchV2Request = Body(...)):
    try:
        from .ml.match import run_match_v2   # api/ml/match.py
    except Exception as e:
        return {"ok": False, "results": [], "error": f"import_error: {e.__class__.__name__}: {e}"}
    try:
        # run_match_v2 espera un objeto Pydantic y devuelve un dict (model_dump)
        return run_match_v2(payload)
    except Exception as e:
        return {"ok": False, "results": [], "error": f"runtime_error: {e.__class__.__name__}: {e}"}

# --- app pública que carga Vercel ---
app = FastAPI()
app.mount("/api", api_app)          # /api/*
app.include_router(api_app.router)  # y también en raíz por si Vercel recorta
