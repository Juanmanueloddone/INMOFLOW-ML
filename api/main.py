import os
USE_ML = os.getenv("USE_ML", "false").lower() == "true"
BLEND_ALPHA = float(os.getenv("BLEND_ALPHA", "0.30"))

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ScoreReq(BaseModel):
    demanda_id: str
    propiedad_id: str

@app.post("/ml/score")
def ml_score(req: ScoreReq):
    # Mientras USE_ML=false devolvemos stub; el contrato ya queda estable
    if not USE_ML:
        return {
            "demanda_id": req.demanda_id,
            "propiedad_id": req.propiedad_id,
            "score_ml": None,
            "rank_ml": None,
            "model_version": "none",
            "features_used_hash": None,
        }

    # (cuando lo activemos) leeremos de match_model_scores y aplicaremos blend
    return {
        "demanda_id": req.demanda_id,
        "propiedad_id": req.propiedad_id,
        "score_ml": None,
        "rank_ml": None,
        "model_version": "pending",
        "features_used_hash": None,
    }
