import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_update_traffic():
    payload = {"intersection_id": "Anna Nagar", "congestion": 12, "incident": "accident"}
    response = client.post("/update_traffic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["received"] == payload 