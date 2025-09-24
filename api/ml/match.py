# api/ml/match.py
from typing import Dict, Any, List
import numpy as np
from ..schemas import (
    MatchV2Request, MatchV2Response, BuyerResult, MatchItem, Buyer, Listing
)

# --- helpers de features (baseline) ---

def _minmax(x: float, lo: float, hi: float) -> float:
    if lo is None or hi is None or lo >= hi:
        return 0.0
    x = max(min(x, hi), lo)
    return (x - lo) / (hi - lo)

def _build_tag_vocab(buyers: List[Buyer], candidates: List[Listing]) -> Dict[str, int]:
    vocab: Dict[str, int] = {}
    def add(tag: str):
        if tag not in vocab:
            vocab[tag] = len(vocab)
    for b in buyers:
        for t in b.must_haves:
            add(t.lower())
    for l in candidates:
        for t in l.features:
            add(t.lower())
    return vocab

def _buyer_vector(b: Buyer, price_lo: float, price_hi: float, tag_vocab: Dict[str,int]) -> np.ndarray:
    # precio “objetivo”: medio del presupuesto o 0 si no hay
    if b.budget_min is not None and b.budget_max is not None:
        target_price = 0.5 * (b.budget_min + b.budget_max)
    elif b.budget_max is not None:
        target_price = b.budget_max
    elif b.budget_min is not None:
        target_price = b.budget_min
    else:
        target_price = price_lo

    price_norm = _minmax(target_price, price_lo, price_hi)
    rooms_norm = (b.rooms_min or 0) / 10.0

    tag_vec = np.zeros(len(tag_vocab), dtype=float)
    for t in b.must_haves:
        idx = tag_vocab.get(t.lower())
        if idx is not None:
            tag_vec[idx] = 1.0

    return np.concatenate([np.array([price_norm, rooms_norm]), tag_vec])

def _listing_vector(l: Listing, price_lo: float, price_hi: float, tag_vocab: Dict[str,int]) -> np.ndarray:
    if l.vector:
        return np.array(l.vector, dtype=float)

    price_norm = _minmax(l.price, price_lo, price_hi)
    rooms_norm = (l.rooms or 0) / 10.0

    tag_vec = np.zeros(len(tag_vocab), dtype=float)
    for t in l.features:
        idx = tag_vocab.get(t.lower())
        if idx is not None:
            tag_vec[idx] = 1.0

    return np.concatenate([np.array([price_norm, rooms_norm]), tag_vec])

def _cosine(a: np.ndarray, B: np.ndarray) -> np.ndarray:
    # a: (d,), B: (n,d) -> (n,)
    a_n = a / (np.linalg.norm(a) + 1e-9)
    B_n = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-9)
    return B_n @ a_n

def _budget_penalty(b: Buyer, prices: np.ndarray) -> np.ndarray:
    # penaliza listings fuera del presupuesto del buyer
    if b.budget_min is None and b.budget_max is None:
        return np.zeros_like(prices)
    lo = b.budget_min if b.budget_min is not None else -np.inf
    hi = b.budget_max if b.budget_max is not None else np.inf
    penalty = np.zeros_like(prices)
    penalty[prices < lo] = -0.25  # fuera por abajo
    penalty[prices > hi] = -0.25  # fuera por arriba
    return penalty

# --- API principal ---

def run_match_v2(req: MatchV2Request) -> Dict[str, Any]:
    buyers = req.buyers
    cands = req.candidates
    top_k = req.top_k

    if not buyers or not cands:
        return {"ok": True, "results": []}

    # rango de precios del pool (para normalizar)
    prices = np.array([c.price for c in cands], dtype=float)
    price_lo = float(np.nanmin(prices))
    price_hi = float(np.nanmax(prices)) if np.nanmax(prices) > price_lo else price_lo + 1.0

    tag_vocab = _build_tag_vocab(buyers, cands)
    L = np.vstack([_listing_vector(l, price_lo, price_hi, tag_vocab) for l in cands])

    results: List[BuyerResult] = []
    for b in buyers:
        v_b = _buyer_vector(b, price_lo, price_hi, tag_vocab)
        sim = _cosine(v_b, L)

        # ajuste por presupuesto
        penalty = _budget_penalty(b, prices)
        score = sim + penalty

        # top-k
        idx = np.argsort(-score)[:top_k]
        matches = [MatchItem(listing_id=cands[i].id, score=float(score[i])) for i in idx]
        results.append(BuyerResult(buyer_id=b.id, matches=matches))

    return MatchV2Response(ok=True, results=results).model_dump()

# Mantengo el run_match "viejo" (dummy) para /api/match (compat)
def run_match(payload: Dict[str, Any]) -> Dict[str, Any]:
    buyers = int(payload.get("buyers", 1))
    top_k = int(payload.get("top_k", 10))
    return {
        "ok": True,
        "buyers": buyers,
        "top_k": top_k,
        "results": [{"buyer_id": i+1, "matches": []} for i in range(buyers)],
    }
