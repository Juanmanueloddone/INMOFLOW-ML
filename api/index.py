from fastapi import FastAPI

app = FastAPI(title="InmoFlow ML API")

@app.get("/health")
def health():
    return {"status": "ok"}
