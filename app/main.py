"""A small, local-only API for practicing security testing."""

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="API Security Testing Lab", version="0.1.0")

# These values are deliberately fake and exist only for local test scenarios.
LAB_TOKENS = {
    "lab-user-token": {"username": "alice", "role": "user"},
    "lab-admin-token": {"username": "admin", "role": "admin"},
}


def authenticate(authorization: str | None) -> dict[str, str]:
    """Return the lab identity for a valid bearer token."""
    scheme, _, token = (authorization or "").partition(" ")
    identity = LAB_TOKENS.get(token) if scheme.lower() == "bearer" else None
    if identity is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return identity


@app.exception_handler(Exception)
async def safe_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    """Return a generic response without exposing exception details."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/protected")
def protected(authorization: str | None = Header(default=None)) -> dict[str, str]:
    identity = authenticate(authorization)
    return {"username": identity["username"], "role": identity["role"]}


@app.get("/users/{username}/profile")
def read_profile(
    username: str,
    authorization: str | None = Header(default=None),
) -> dict[str, str]:
    identity = authenticate(authorization)
    if identity["role"] != "admin" and identity["username"] != username:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"username": username, "profile": "Local lab profile"}


@app.get("/items")
def list_items(limit: int = Query(default=10, ge=1, le=100)) -> dict[str, int]:
    return {"limit": limit}
