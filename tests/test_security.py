"""Security-focused tests for the local API lab."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, safe_unhandled_error

client = TestClient(app)


def test_protected_endpoint_rejects_missing_credentials() -> None:
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_rejects_invalid_credentials() -> None:
    response = client.get("/protected", headers={"Authorization": "Bearer invalid"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_protected_endpoint_accepts_lab_user() -> None:
    response = client.get(
        "/protected", headers={"Authorization": "Bearer lab-user-token"}
    )

    assert response.status_code == 200
    assert response.json() == {"username": "alice", "role": "user"}


def test_user_cannot_read_another_users_profile() -> None:
    response = client.get(
        "/users/admin/profile",
        headers={"Authorization": "Bearer lab-user-token"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_admin_can_read_another_users_profile() -> None:
    response = client.get(
        "/users/alice/profile",
        headers={"Authorization": "Bearer lab-admin-token"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_item_limit_validation_rejects_out_of_range_values() -> None:
    for limit in (0, 101, "not-a-number"):
        response = client.get("/items", params={"limit": limit})
        assert response.status_code == 422


def test_unhandled_error_response_does_not_expose_exception_details() -> None:
    error_app = FastAPI()
    error_app.add_exception_handler(Exception, safe_unhandled_error)

    @error_app.get("/failure")
    def fail() -> None:
        raise RuntimeError("sensitive internal detail")

    response = TestClient(error_app, raise_server_exceptions=False).get("/failure")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "sensitive internal detail" not in response.text
