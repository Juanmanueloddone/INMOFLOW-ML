import json

def handler(request):
    # request.query_string puede venir en bytes o str según la runtime
    try:
        from urllib.parse import parse_qs
        qs_raw = request.query_string
        if isinstance(qs_raw, bytes):
            qs_raw = qs_raw.decode("utf-8", errors="ignore")
        qs = parse_qs(qs_raw or "")
        top_k = int((qs.get("top_k") or ["10"])[0])
        buyers = int((qs.get("buyers") or ["1"])[0])
    except Exception:
        top_k = 10
        buyers = 1

    body = {"top_k": top_k, "buyers": buyers, "results": []}
    return (200, {"Content-Type": "application/json"}, json.dumps(body))
