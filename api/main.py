# api/main.py
from fastapi import FastAPI, APIRouter, Query
from .schemas import VersionInfo
import os
from uuid import uuid4
from supabase import create_client, Client
from ml.matching_demo import run_demo  # usa tu script de embeddings/matching

# ---------- App ----------
app = FastAPI(title="InmoFlow ML API", version="0.1.0")

# ---------- Health & Version ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version", response_model=VersionInfo)
def version():
    return VersionInfo(service="inmoflow-ml", version="0.1.0")

# ---------- ML Router (en este mismo archivo) ----------
router = APIRouter(prefix="/ml", tags=["ml"])

# Vars de entorno (configuradas en Vercel)
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # usar Service Role en servidor
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@router.get("/demo-match")
def ml_demo_match(top_k: int = Query(10, ge=1, le=100), persist: int = 0):
    """
    Ejecuta el matching demo (embeddings + cosine).
    - top_k: cantidad de resultados.
    - persist=1: guarda el batch en ml.matches_demo.
    """
    results = run_demo(top_k=top_k)

    if persist == 1:
        run_id = str(uuid4())
        rows = [
            {
                "run_id": run_id,
                "comprador_id": r["comprador_id"],
                "comprador_nombre": r["comprador_nombre"],
                "propiedad_id": r["propiedad_id"],
                "propiedad_nombre": r["propiedad"],
                "zona_prop": r["zona_prop"],
                "score": r["score"],
            }
            for r in results
        ]
        if rows:
            sb.table("ml.matches_demo").insert(rows).execute()
        return {"run_id": run_id, "saved": len(rows), "results": results}

    return {"results": results}

# Montar router
app.include_router(router)
