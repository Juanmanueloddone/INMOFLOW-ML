# api/index.py
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from .schemas import MatchRequest, MatchResponse  # <-- modelos pydantic

# --- sub-app con rutas reales (la que expone /api) ---
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

@api_app.get("/match")
def match_info():
    return {
        "ok": True,
        "message": 'Usá POST /api/match con JSON, p.ej: {"buyers": 2, "top_k": 5}',
    }

@api_app.post("/match", response_model=MatchResponse)
def match_endpoint(payload: MatchRequest = Body(...)):
    # import tardío para evitar problemas de carga
    try:
        from .ml.match import run_match  # api/ml/match.py
    except Exception as e:
        return {
            "ok": False,
            "buyers": payload.buyers,
            "top_k": payload.top_k,
            "results": [],
            "error": f"import_error: {e.__class__.__name__}: {e}",
        }
    try:
        # run_match debe devolver un dict con la forma de MatchResponse
        return run_match(payload.model_dump())
    except Exception as e:
        return {
            "ok": False,
            "buyers": payload.buyers,
            "top_k": payload.top_k,
            "results": [],
            "error": f"runtime_error: {e.__class__.__name__}: {e}",
        }

# --- app pública que carga Vercel ---
app = FastAPI()
# 1) sirve bajo /api (cuando Vercel NO recorta)
app.mount("/api", api_app)
# 2) y también en raíz (cuando Vercel SÍ recorta)
app.include_router(api_app.router)
