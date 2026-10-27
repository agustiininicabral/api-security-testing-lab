"""Security-focused tests for the local API lab."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, safe_unhandled_error

client = TestClient(app)


def test_protected_endpoint_rejects_missing_credentials() -> None:
    response = client.get("/protected")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "authorization",
    [
        "Bearer invalid",
        "Basic lab-user-token",
        "Bearer",
        "Bearer ",
        "Bearer  lab-user-token",
        "Bearer lab-user-token extra",
        "Bearer\tlab-user-token",
    ],
    ids=[
        "unknown-token",
        "wrong-scheme",
        "missing-token",
        "empty-token",
        "extra-space",
        "extra-token-data",
        "tab-separator",
    ],
)
def test_protected_endpoint_rejects_malformed_or_invalid_credentials(
    authorization: str,
) -> None:
    response = client.get(
        "/protected",
        headers={"Authorization": authorization},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_endpoint_accepts_lab_user() -> None:
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer lab-user-token"},
    )

    assert response.status_code == 200
    assert response.json() == {"username": "alice", "role": "user"}


def test_bearer_scheme_is_case_insensitive() -> None:
    response = client.get(
        "/protected",
        headers={"Authorization": "bEaReR lab-user-token"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


def test_user_can_read_own_profile() -> None:
    response = client.get(
        "/users/alice/profile",
        headers={"Authorization": "Bearer lab-user-token"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "username": "alice",
        "profile": "Local lab profile",
    }


def test_user_cannot_read_another_users_profile() -> None:
    response = client.get(
        "/users/admin/profile",
        headers={"Authorization": "Bearer lab-user-token"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}


def test_profile_endpoint_rejects_missing_credentials() -> None:
    response = client.get("/users/alice/profile")

    assert response.status_code == 401


def test_admin_can_read_another_users_profile() -> None:
    response = client.get(
        "/users/alice/profile",
        headers={"Authorization": "Bearer lab-admin-token"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "alice"


@pytest.mark.parametrize("limit", [0, -1, 101, "not-a-number", "1.5"])
def test_item_limit_validation_rejects_out_of_range_values(limit: str | int) -> None:
    response = client.get("/items", params={"limit": limit})

    assert response.status_code == 422


@pytest.mark.parametrize("limit", [1, 100])
def test_item_limit_validation_accepts_boundary_values(limit: int) -> None:
    response = client.get("/items", params={"limit": limit})

    assert response.status_code == 200
    assert response.json() == {"limit": limit}


def test_item_limit_defaults_to_ten() -> None:
    response = client.get("/items")

    assert response.status_code == 200
    assert response.json() == {"limit": 10}


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


def test_global_exception_handler_is_registered() -> None:
    assert app.exception_handlers.get(Exception) is safe_unhandled_error


@pytest.mark.parametrize(
    ("path", "authorization"),
    [
        ("/users/alice/profile", None),
        ("/users/alice/profile", "Bearer invalid"),
        ("/users/alice/profile", "Basic lab-user-token"),
        ("/users/alice/profile", "Bearer"),
        ("/users/alice/profile", "Bearer lab-user-token extra"),
    ],
    ids=[
        "missing-credentials",
        "unknown-token",
        "wrong-scheme",
        "missing-token",
        "extra-token-data",
    ],
)
def test_profile_endpoint_rejects_missing_or_malformed_credentials(
    path: str,
    authorization: str | None,
) -> None:
    headers = {"Authorization": authorization} if authorization is not None else {}

    response = client.get(path, headers=headers)

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_forbidden_profile_response_does_not_disclose_profile_data() -> None:
    response = client.get(
        "/users/admin/profile",
        headers={"Authorization": "Bearer lab-user-token"},
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden"}
    assert "Local lab profile" not in response.text
    assert "admin" not in response.text
