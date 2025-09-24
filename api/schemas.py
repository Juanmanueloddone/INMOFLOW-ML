
from pydantic import BaseModel
from typing import List, Any, Dict

class MatchRequest(BaseModel):
    buyers: int = 1
    top_k: int = 10

class BuyerMatch(BaseModel):
    buyer_id: int
    matches: List[Dict[str, Any]] = []

class MatchResponse(BaseModel):
    ok: bool
    buyers: int
    top_k: int
    results: List[BuyerMatch]
