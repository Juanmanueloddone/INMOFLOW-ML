# ml/matching_demo.py
import os
from typing import List, Dict
import numpy as np
from supabase import create_client, Client
from openai import OpenAI

# === Config: variables de entorno ===
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# === Clientes ===
sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
oa = OpenAI(api_key=OPENAI_API_KEY)

# === Utilidades ===
def embed(text: str) -> np.ndarray:
    resp = oa.embeddings.create(model="text-embedding-3-small", input=text)
    return np.array(resp.data[0].embedding, dtype=np.float32)

def cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    denom = (np.linalg.norm(a) * np.linalg.norm(b))
    return float(np.dot(a, b) / denom) if denom else 0.0

# === Carga de datos desde Supabase ===
def load_props() -> List[Dict]:
    # lee SOLO los campos que vamos a usar
    r = sb.table("propiedades").select(
        "id,nombre,zona_clave,precio,amenities"
    ).execute()
    return r.data or []

def load_buyers() -> List[Dict]:
    # leemos desde la VISTA pública v_ml_buyers_prefs
    r = sb.table("v_ml_buyers_prefs").select(
        "comprador_id,comprador_nombre,zona_clave,precio_max,amenities"
    ).execute()
    return r.data or []

# === Matching demo ===
def run_demo(top_k: int = 5) -> List[Dict]:
    props = load_props()
    buyers = load_buyers()

    # Pre-embed propiedades una sola vez
    prop_vecs = {}
    for p in props:
        # texto compacto: nombre + zona + amenities + precio (como string)
        amenities_txt = " ".join(p.get("amenities") or [])
        text = f"{p.get('nombre','')} {p.get('zona_clave','')} {amenities_txt} precio:{p.get('precio')}"
        prop_vecs[p["id"]] = embed(text)

    results: List[Dict] = []
    for b in buyers:
        am_txt = " ".join(b.get("amenities") or [])
        pref_text = (
            f"zona:{b.get('zona_clave','')} "
            f"precio_max:{b.get('precio_max')} "
            f"amenities:{am_txt}"
        )
        buyer_vec = embed(pref_text)

        # score con cada propiedad
        for p in props:
            score = cos_sim(buyer_vec, prop_vecs[p["id"]])

            # penalización simple si la propiedad excede precio_max
            precio = p.get("precio") or 0
            precio_max = b.get("precio_max") or 0
            if precio_max and precio > precio_max:
                score *= 0.85

            results.append({
                "comprador_id": b["comprador_id"],
                "comprador_nombre": b["comprador_nombre"],
                "propiedad_id": p["id"],
                "propiedad": p["nombre"],
                "zona_prop": p["zona_clave"],
                "score": round(score, 6),
            })

    # ordenar y tomar top_k
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    top = run_demo(top_k=10)
    for r in top:
        print(r)
