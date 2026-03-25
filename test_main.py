from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Opportunity Platform is running"}

def test_invalid_state():
    response = client.post("/score", json={
        "name": "Test Project",
        "state": "NY",
        "naics_code": 237,
        "opportunity_type": "pre-solicitation",
        "dollar_amount": 3000000,
        "calendar_days": 300,
        "days_until_response": 15,
        "sow_match": "strong"
    })
    assert response.status_code == 200
    assert response.json()["result"] == "NO BID"

def test_valid_bid():
    response = client.post("/score", json={
        "name": "Dallas Project",
        "state": "TX",
        "naics_code": 237,
        "opportunity_type": "pre-solicitation",
        "dollar_amount": 3000000,
        "calendar_days": 300,
        "days_until_response": 15,
        "sow_match": "strong"
    })
    assert response.status_code == 200
    assert response.json()["result"] == "BID"