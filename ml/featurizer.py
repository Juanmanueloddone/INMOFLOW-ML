# ml/featurizer.py
from typing import Dict, List

def join_amenities(am: List[str] | None) -> str:
    return " ".join((am or []))

def text_prop(p: Dict) -> str:
    """
    Texto canónico para embeddings de propiedad.
    Ajusta campos a tu schema real (nombre, zona_clave, amenities, precio).
    """
    return (
        f"{p.get('nombre','')} "
        f"zona:{p.get('zona_clave','')} "
        f"amenities:{join_amenities(p.get('amenities'))} "
        f"precio:{p.get('precio')}"
    ).strip()

def text_buyer(b: Dict) -> str:
    """
    Texto canónico para embeddings de preferencias del comprador (v_ml_buyers_prefs).
    """
    return (
        f"busca_zona:{b.get('zona_clave','')} "
        f"precio_max:{b.get('precio_max')} "
        f"amenities:{join_amenities(b.get('amenities'))}"
    ).strip()

def score_rules(p: Dict, b: Dict) -> Dict[str, float]:
    """
    Señales (reglas) simples que luego ponderamos con el coseno:
    - gap de precio (mientras menor, mejor)
    - overlap de amenities
    """
    precio = float(p.get("precio") or 0)
    precio_max = float(b.get("precio_max") or 0)

    # price compatibility
    if precio_max <= 0:
        price_factor = 1.0
        price_gap = 0.0
    else:
        gap = max(precio - precio_max, 0.0)
        # penaliza si excede; normaliza por precio_max
        price_gap = gap / max(precio_max, 1.0)
        price_factor = 1.0 - min(price_gap, 1.0) * 0.35  # hasta -35%

    # amenities overlap
    pa = set(p.get("amenities") or [])
    ba = set(b.get("amenities") or [])
    overlap = len(pa & ba)
    desired = len(ba) if len(ba) > 0 else 1
    amenities_factor = 0.85 + 0.15 * (overlap / desired)  # 0.85..1.0

    # zona preferida (pequeño boost si coincide)
    zona_match = 1.05 if (p.get("zona_clave") and p.get("zona_clave") == b.get("zona_clave")) else 1.0

    return {
        "price_factor": float(price_factor),
        "amenities_factor": float(amenities_factor),
        "zona_factor": float(zona_match),
        "price_gap": float(price_gap),
        "amenities_overlap": float(overlap),
    }
