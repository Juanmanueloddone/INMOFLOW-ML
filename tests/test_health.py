from fastapi.testclient import TestClient
from api.main import app


client = TestClient(app)


def test_health():
r = client.get("/health")
assert r.status_code == 200
assert r.json().get("status") == "ok"


def test_version():
r = client.get("/version")
assert r.status_code == 200
data = r.json()
assert data.get("service") == "inmoflow-ml"
assert data.get("version") == "0.1.0"
