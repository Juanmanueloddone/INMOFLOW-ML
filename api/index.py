from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import APIRouter

app = FastAPI()
router = APIRouter(prefix="/api")

@router.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@router.get("/version")
async def version():
    return JSONResponse({"version": "1.0.0"})

app.include_router(router)
# Tip: exportar también con nombre 'handler' no molesta al runtime de Vercel:
handler = app
