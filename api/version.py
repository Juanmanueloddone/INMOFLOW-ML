# /api/version.py
import json, os

def handler(request):
    body = {
        "service": "InmoFlow ML API",
        "version": os.getenv("IMAGE_VERSION", "0.1.0")
    }
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(body)
    }
