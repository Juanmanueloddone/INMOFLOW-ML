from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware

# sub-app con tus rutas reales
api_app = FastAPI()
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@api_app.get("/health")
def health():
    return {"ok": True}

@api_app.get("/version")
def version():
    return {"version": "1.0.0"}

@api_app.post("/match")
def match_endpoint(payload: dict = Body(...)):
    try:
        from ml.match import run_match
    except Exception as e:
        return {"ok": False, "error": f"import_error: {e.__class__.__name__}: {e}"}
    try:
        return run_match(payload)
    except Exception as e:
        return {"ok": False, "error": f"runtime_error: {e.__class__.__name__}: {e}"}

# app pública que carga Vercel
app = FastAPI()
# 1) sirve bajo /api (cuando Vercel NO recorta)
app.mount("/api", api_app)
# 2) y también en raíz (cuando Vercel SÍ recorta)
app.include_router(api_app.router)
