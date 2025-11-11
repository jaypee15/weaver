import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_query_without_auth():
    response = client.post(
        "/v1/tenants/00000000-0000-0000-0000-000000000000/query",
        json={"query": "test"}
    )
    assert response.status_code == 401


def test_invalid_api_key():
    response = client.post(
        "/v1/tenants/00000000-0000-0000-0000-000000000000/query",
        json={"query": "test"},
        headers={"Authorization": "Bearer invalid_key"}
    )
    assert response.status_code == 401

