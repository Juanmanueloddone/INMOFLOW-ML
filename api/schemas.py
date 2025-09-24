# api/schemas.py
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# -------- V1 --------
class MatchRequest(BaseModel):
    buyers: int = Field(1, ge=1, le=1000)
    top_k: int = Field(10, ge=1, le=1000)

class MatchItem(BaseModel):
    buyer_id: int
    matches: List[Dict[str, Any]] = []

class MatchResponse(BaseModel):
    ok: bool
    buyers: int
    top_k: int
    results: List[MatchItem]
    error: Optional[str] = None

# -------- V2 --------
class BuyerProfile(BaseModel):
    id: int
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    city: Optional[str] = None
    features: Dict[str, Any] = {}

class MatchV2Request(BaseModel):
    buyers: List[BuyerProfile]
    top_k: int = Field(10, ge=1, le=1000)

class MatchV2Result(BaseModel):
    buyer_id: int
    matches: List[Dict[str, Any]] = []

class MatchV2Response(BaseModel):
    ok: bool
    results: List[MatchV2Result]
    error: Optional[str] = None
