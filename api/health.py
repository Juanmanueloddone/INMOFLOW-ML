# /api/health.py
import json

def handler(request):
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": json.dumps({"ok": True})
    }
