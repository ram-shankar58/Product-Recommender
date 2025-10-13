from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sample_flow():
    # seed
    r = client.post("/load-sample-data")
    assert r.status_code == 200
    # recommend
    r = client.post("/recommendations", json={"user_id": 1, "k": 3})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        assert "explanation" in data[0]
