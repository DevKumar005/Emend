import pytest
from fastapi.testclient import TestClient
from emend.api.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models" in data

def test_demo_repos_endpoint():
    response = client.get("/api/demo-repos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    repo_ids = [r["id"] for r in data]
    assert "billing_ripple" in repo_ids
    assert "shopcalc" in repo_ids
    assert "scheduler_hard" in repo_ids

def test_create_analysis_endpoint():
    payload = {
        "repo_source": "shopcalc",
        "branch": "main",
        "failing_test": "tests/test_calculator.py::test_discount_twenty_percent",
        "mode": "hosted"
    }
    response = client.post("/api/analysis", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert "analysis_id" in data
