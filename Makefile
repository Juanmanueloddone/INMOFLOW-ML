.PHONY: dev test run docker


dev:
uvicorn api.main:app --reload --port 8000


test:
pytest


run:
uvicorn api.main:app --host 0.0.0.0 --port $${PORT:-8000}


docker:
docker build -f infra/docker/Dockerfile -t inmoflow-ml:dev .
