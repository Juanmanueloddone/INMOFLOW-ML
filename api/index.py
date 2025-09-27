
# api/index.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from .schemas import (
    MatchRequest, MatchResponse,
    MatchV2Request, MatchV2Response,   # <-- v2
)

# --- sub-app con rutas reales (la que expone /api) ---
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # abrir para probar; luego limitá a tus dominios
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.get("/health")
def health():
    return {"ok": True}

@api_app.get("/version")
def version():
    return {"version": "1.0.0"}

@api_app.get("/match")
def match_info():
    return {
        "ok": True,
        "message": 'Usá POST /api/match con JSON, p.ej: {"buyers": 2, "top_k": 5}',
    }

# --- NUEVA RUTA V2 ---
@api_app.post("/match/v2", response_model=MatchV2Response)
def match_v2_endpoint(payload: MatchV2Request = Body(...)):
    try:
        from .ml.match import run_match_v2
    except Exception as e:
        return {"ok": False, "results": [], "error": f"import_error: {e.__class__.__name__}: {e}"}

    try:
        # OJO: sin .model_dump()
        return run_match_v2(payload)
    except Exception as e:
        return {"ok": False, "results": [], "error": f"runtime_error: {e.__class__.__name__}: {e}"}

    try:
        return run_match(payload.model_dump())
    except Exception as e:
        return {
            "ok": False,
            "buyers": payload.buyers,
            "top_k": payload.top_k,
            "results": [],
            "error": f"runtime_error: {e.__class__.__name__}: {e}",
        }

# --- NUEVA RUTA V2 ---
@api_app.post("/match/v2")  # <- sacamos response_model=MatchV2Response
def match_v2_endpoint(payload: MatchV2Request = Body(...)):
    try:
        from .ml.match import run_match_v2
    except Exception as e:
        return {"ok": False, "results": [], "error": f"import_error: {e.__class__.__name__}: {e}"}
    try:
        return run_match_v2(payload.model_dump())
    except Exception as e:
        return {"ok": False, "results": [], "error": f"runtime_error: {e.__class__.__name__}: {e}"}

# --- app pública que carga Vercel ---
app = FastAPI()
# 1) sirve bajo /api (cuando Vercel NO recorta)
app.mount("/api", api_app)
# 2) y también en raíz (cuando Vercel SÍ recorta)
app.include_router(api_app.router)
