from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/")
def match(
    top_k: int = Query(10, ge=1, le=100),
    buyers: int = Query(1, ge=1, le=1000),
):
    # stub, responde algo válido
    return {"top_k": top_k, "buyers": buyers, "results": []}
