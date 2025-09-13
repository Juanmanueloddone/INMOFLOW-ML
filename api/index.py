from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum  # <-- clave para Vercel

app = FastAPI()

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/version")
async def version():
    return JSONResponse({"version": "1.0.0"})

handler = Mangum(app)  # <-- Vercel invoca esto
