"""Integration tests for the Flask API endpoints (backend/app.py)."""

import json
from unittest.mock import MagicMock, patch
import pytest

from app import app
from verifier import STATUS_LIKELY_DELIVERED, STATUS_LIKELY_BOUNCE, STATUS_UNKNOWN


@pytest.fixture
def client():
    """Create Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    def test_health_check_returns_200(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert "mailcheck" in data["service"]
        assert "max_batch_size" in data


class TestVerifyEndpointValidation:
    def test_non_json_request_returns_400(self, client):
        response = client.post(
            "/api/verify",
            data="not a json payload",
            content_type="text/plain",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

    def test_missing_emails_field_returns_400(self, client):
        response = client.post(
            "/api/verify",
            json={"other_field": []},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "Missing required field 'emails'" in data["error"]

    def test_emails_not_a_list_returns_400(self, client):
        response = client.post(
            "/api/verify",
            json={"emails": "user@example.com"},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "must be a JSON array" in data["error"]

    def test_empty_emails_list_returns_400(self, client):
        response = client.post(
            "/api/verify",
            json={"emails": []},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "cannot be empty" in data["error"]

    def test_oversized_batch_returns_400(self, client):
        too_many = [f"test{i}@example.com" for i in range(101)]
        response = client.post(
            "/api/verify",
            json={"emails": too_many},
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "limit exceeded" in data["error"]


class TestVerifyEndpointSuccess:
    @patch("verifier.dns.resolver.Resolver")
    def test_verify_valid_and_invalid_emails(self, mock_resolver_cls, client):
        # Configure mock DNS resolver
        mock_resolver = MagicMock()
        mock_resolver_cls.return_value = mock_resolver

        def mock_resolve(domain, rdtype):
            if domain == "example.com":
                rec = MagicMock()
                rec.preference = 10
                rec.exchange = "mail.example.com."
                return [rec]
            import dns.resolver
            raise dns.resolver.NXDOMAIN()

        mock_resolver.resolve.side_effect = mock_resolve

        response = client.post(
            "/api/verify",
            json={
                "emails": [
                    "legit@example.com",
                    "not-an-email",
                    "user@nonexistent-domain-404.org",
                    "legit@example.com",  # duplicate
                ]
            },
        )

        assert response.status_code == 200
        data = response.get_json()
        assert "results" in data
        assert "summary" in data

        results = data["results"]
        summary = data["summary"]

        assert summary["total_submitted"] == 4
        assert summary["unique_processed"] == 3
        assert summary["duplicates_removed"] == 1
        assert summary["likely_delivered"] == 1
        assert summary["likely_bounce"] == 2
        assert summary["unknown"] == 0

        # Check result object fields
        first_item = results[0]
        assert "email" in first_item
        assert "status" in first_item
        assert "reason" in first_item
        assert "checks_performed" in first_item
        assert first_item["status"] in [STATUS_LIKELY_DELIVERED, STATUS_LIKELY_BOUNCE, STATUS_UNKNOWN]

    def test_cors_headers_present(self, client):
        response = client.get("/api/health")
        # CORS headers should be present on responses
        assert "Access-Control-Allow-Origin" in response.headers
