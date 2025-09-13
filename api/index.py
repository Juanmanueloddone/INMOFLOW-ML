from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/api/version")
async def version():
    return JSONResponse({"version": "1.0.0"})
