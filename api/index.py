from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/version")
async def version():
    return JSONResponse({"version": "1.0.0"})
