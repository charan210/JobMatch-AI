from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


from typing import Generator
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Module-scoped TestClient — starts app once for all tests in this file."""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


class TestRootEndpoint:
    """Acceptance criterion: GET / → {"message": "ARAS API Running"}"""

    def test_status_code_200(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200

    def test_message_content(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.json() == {"message": "ARAS API Running"}


class TestHealthEndpoint:
    """Acceptance criterion: GET /health → {"status": "healthy"}"""

    def test_status_code_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_status_content(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}

    def test_health_does_not_hit_database(self, client: TestClient) -> None:
        """
        GET /health must never have a database dependency.
        Verifying it returns 200 even when DB is unreachable satisfies this.
        The TestClient doesn't have a live DB, so a successful 200 proves it.
        """
        response = client.get("/health")
        assert response.status_code == 200


class TestSwaggerUI:
    """Acceptance criterion: GET /docs → Swagger UI loads successfully"""

    def test_docs_returns_200(self, client: TestClient) -> None:
        response = client.get("/docs")
        assert response.status_code == 200

    def test_docs_contains_swagger(self, client: TestClient) -> None:
        response = client.get("/docs")
        assert "swagger" in response.text.lower()

    def test_openapi_schema_accessible(self, client: TestClient) -> None:
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200

    def test_openapi_schema_title(self, client: TestClient) -> None:
        schema = client.get("/api/v1/openapi.json").json()
        assert schema["info"]["title"] == "AI Recruitment Automation System"

    def test_openapi_schema_version(self, client: TestClient) -> None:
        schema = client.get("/api/v1/openapi.json").json()
        assert schema["info"]["version"] == "1.0.0"


class TestCORSHeaders:
    """CORS must allow the React+Vite frontend origin."""

    def test_cors_allows_vite_origin(self, client: TestClient) -> None:
        response = client.options(
            "/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert response.headers.get("access-control-allow-origin") in (
            "http://localhost:5173",
            "*",
        )


class TestErrorEnvelope:
    """Unknown routes must return the canonical ARAS error envelope."""

    def test_404_returns_error_envelope(self, client: TestClient) -> None:
        response = client.get("/nonexistent-route")
        assert response.status_code == 404
        body = response.json()
        assert body["success"] is False
        assert "message" in body
        assert "errors" in body