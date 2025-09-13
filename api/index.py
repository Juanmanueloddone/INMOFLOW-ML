from fastapi import FastAPI
from fastapi.responses import JSONResponse

__all__ = ["app"]  # <-- le decimos a Vercel qué exportar

app = FastAPI()

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/version")
async def version():
    return JSONResponse({"version": "1.0.0"})
