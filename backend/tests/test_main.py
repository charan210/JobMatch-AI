from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, create_application


from typing import Generator
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Module-scoped TestClient."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


def test_create_application() -> None:
    """Verify that the FastAPI application factory returns a configured instance."""
    test_app = create_application()
    assert isinstance(test_app, FastAPI)
    assert test_app.title is not None
    assert test_app.version is not None


def test_application_startup(client: TestClient) -> None:
    """
    Verify application startup logic.
    Initializing the TestClient triggers the FastAPI lifespan (startup/shutdown).
    If it initializes without exceptions, the test passes.
    """
    assert client.app is not None


def test_root_endpoint(client: TestClient) -> None:
    """Verify the root endpoint loads successfully."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health_endpoint(client: TestClient) -> None:
    """Verify the health endpoint loads successfully."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json().get("status") == "healthy"
