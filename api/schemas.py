from typing import List, Optional
from pydantic import BaseModel

# ---------- v1 (dummy) ----------
class MatchRequest(BaseModel):
    buyers: int = 1
    top_k: int = 10

class MatchResponse(BaseModel):
    ok: bool = True
    buyers: int
    top_k: int
    results: List[dict] = []

# ---------- v2 (real) ----------
class Buyer(BaseModel):
    id: int
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rooms_min: Optional[int] = None
    must_haves: List[str] = []

class Listing(BaseModel):
    id: str
    price: float
    rooms: Optional[int] = None
    features: List[str] = []
    # opcionalmente un embedding precomputado
    vector: Optional[List[float]] = None

class MatchItem(BaseModel):
    listing_id: str
    score: float

class BuyerResult(BaseModel):
    buyer_id: int
    matches: List[MatchItem]

class MatchV2Request(BaseModel):
    buyers: List[Buyer]
    candidates: List[Listing]
    top_k: int = 10

class MatchV2Response(BaseModel):
    ok: bool = True
    results: List[BuyerResult] = []
