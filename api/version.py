import json

def handler(request):
    body = {"service": "inmoflow-ml", "version": "0.1.0"}
    return (200, {"Content-Type": "application/json"}, json.dumps(body))
