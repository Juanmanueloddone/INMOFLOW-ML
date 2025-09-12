# api/main.py (añade este bloque al que ya deployaste o reemplaza el /demo por /match)
from fastapi import FastAPI, APIRouter, Query
from .schemas import VersionInfo
import os
from supabase import create_client
from ml.ranking import rank_props_for_buyer

app = FastAPI(title="InmoFlow ML API", version="0.2.0")

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/version", response_model=VersionInfo)
def version(): return VersionInfo(service="inmoflow-ml", version="0.2.0")

router = APIRouter(prefix="/ml", tags=["ml"])

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
sb = create_client(SUPABASE_URL, SUPABASE_KEY)

def _load_props():
    res = sb.table("propiedades").select("id,nombre,zona_clave,precio,amenities").execute()
    return res.data or []

def _load_buyers(limit: int = 10):
    res = sb.table("v_ml_buyers_prefs").select(
        "comprador_id,comprador_nombre,zona_clave,precio_max,amenities"
    ).limit(limit).execute()
    return res.data or []

@router.get("/match")
def ml_match(top_k: int = Query(10, ge=1, le=100), buyers: int = Query(2, ge=1, le=50)):
    """
    Matching v1 (embeddings + reglas) para N compradores.
    Respuesta: top_k por comprador con razones.
    """
    props = _load_props()
    buyers_data = _load_buyers(limit=buyers)

    output = []
    for b in buyers_data:
        ranked = rank_props_for_buyer(props, b, top_k=top_k)
        output.append({"comprador_id": b["comprador_id"], "comprador": b["comprador_nombre"], "results": ranked})
    return {"results": output}

app.include_router(router)
