# api/main.py
from fastapi import FastAPI, Query
from schemas import VersionInfo
import os
from supabase import create_client
from ml.matching_demo import run_demo

app = FastAPI(title="InmoFlow ML API", version="0.1.0")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/version", response_model=VersionInfo)
def version():
    return VersionInfo(service="inmoflow-ml", version="0.1.0")

@app.get("/ml/match")
def match(top_k: int = Query(10), buyers: int = Query(2)):
    """
    Corre el demo de matching usando embeddings
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    supabase = create_client(supabase_url, supabase_key)

    # query propiedades y compradores simulados
    props = supabase.table("propiedades").select(
        "id, nombre, zona_clave, precio, amenities"
    ).limit(20).execute().data

    buyers_prefs = supabase.table("v_ml_buyers_prefs").select(
        "comprador_id, comprador_nombre, zona_clave, precio_max, amenities"
    ).limit(buyers).execute().data

    results = run_demo(props, buyers_prefs, top_k=top_k)
    return {"matches": results}
