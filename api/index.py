# api/ml/match.py

from typing import Dict, Any, List

def run_match(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recibe el payload del POST /api/match y devuelve un JSON de prueba.
    Más adelante acá va la lógica real de matching.
    """
    # Tomamos parámetros con defaults seguros
    buyers = int(payload.get("buyers", 1))
    top_k = int(payload.get("top_k", 10))

    # Dummy: armamos una estructura de resultados vacía por buyer
    results: List[Dict[str, Any]] = [
        {"buyer_id": i + 1, "matches": []} for i in range(buyers)
    ]

    return {
        "ok": True,
        "buyers": buyers,
        "top_k": top_k,
        "results": results,
    }
