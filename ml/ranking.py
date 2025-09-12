# ml/ranking.py
from typing import Dict, List
import numpy as np
from .featurizer import text_prop, text_buyer, score_rules
from .embeddings import embed_cached, cos_sim

def rank_props_for_buyer(props: List[Dict], buyer: Dict, top_k: int = 20) -> List[Dict]:
    """
    Ranking v1: embeddings (cosine) * reglas (precio/zona/amenities).
    Devuelve lista de dicts con razones.
    """
    b_txt = text_buyer(buyer)
    b_vec = embed_cached(b_txt)

    scored: List[Dict] = []
    for p in props:
        p_txt = text_prop(p)
        p_vec = embed_cached(p_txt)

        base = cos_sim(b_vec, p_vec)  # 0..1 aprox
        rules = score_rules(p, buyer)

        # score final: multiplicativo (interpretable)
        final = base * rules["price_factor"] * rules["amenities_factor"] * rules["zona_factor"]

        scored.append({
            "comprador_id": buyer["comprador_id"],
            "comprador_nombre": buyer["comprador_nombre"],
            "propiedad_id": p["id"],
            "propiedad": p["nombre"],
            "zona_prop": p.get("zona_clave"),
            "score": round(float(final), 6),
            "reasons": {
                "cosine": round(float(base), 4),
                "price_factor": round(rules["price_factor"], 3),
                "amenities_factor": round(rules["amenities_factor"], 3),
                "zona_factor": round(rules["zona_factor"], 3),
                "price_gap": round(rules["price_gap"], 3),
                "amenities_overlap": int(rules["amenities_overlap"]),
            }
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]
