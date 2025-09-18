import os

def handler(request):
    return {
        "service": "InmoFlow ML API",
        "version": os.getenv("IMAGE_VERSION", "0.1.0")
    }
