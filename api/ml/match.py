def handler(request):
    qs = request.get("queryString", {}) or {}
    def _get_int(key, default):
        try:
            return int(qs.get(key, default))
        except Exception:
            return default
    top_k = _get_int("top_k", 10)
    buyers = _get_int("buyers", 1)
    return {"top_k": top_k, "buyers": buyers, "results": []}
