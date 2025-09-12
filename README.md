# InmoFlow ML


Servicio de ML para ranking/clustering. Este repo está aislado de `inmoflow-portal`.


## Dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
make dev
# GET http://localhost:8000/health
# GET http://localhost:8000/version
