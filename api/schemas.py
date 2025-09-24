
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

from typing import List, Optional
from pydantic import BaseModel, Field

class Buyer(BaseModel):
    id: str
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    rooms_min: Optional[int] = None
    city: Optional[str] = None
    neighborhoods: List[str] = []
    must_haves: List[str] = []  # tags / amenities (ej: "balcon", "cochera")

class Listing(BaseModel):
    id: str
    price: float
    rooms: Optional[int] = None
    city: Optional[str] = None
    neighborhoods: List[str] = []
    features: List[str] = []    # tags / amenities
    vector: Optional[List[float]] = None  # opcional si más adelante precomputás embeddings

class MatchItem(BaseModel):
    listing_id: str
    score: float

class BuyerResult(BaseModel):
    buyer_id: str
    matches: List[MatchItem]

class MatchV2Request(BaseModel):
    buyers: List[Buyer]
    candidates: List[Listing]
    top_k: int = Field(default=10, ge=1, le=100)

class MatchV2Response(BaseModel):
    ok: bool
    results: List[BuyerResult]

