# API Security Testing Lab

A small, local-only FastAPI project for practicing automated API security tests.
The sample tokens and profiles are fictional and intended only for this lab.
The application does not make requests to external systems.

## Requirements

- Python 3.12
- Dependencies listed in `requirements.txt` (FastAPI, HTTPX, Pytest, and Uvicorn)

Install dependencies in a virtual environment when needed:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run locally

Start the API on the loopback interface:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Uvicorn serves the app on loopback for local manual exploration. The sample endpoints are `/health`,
`/protected`, `/users/{username}/profile`, and `/items?limit=10`.

## Run security tests

```powershell
python -m pytest
```

The tests cover missing and invalid authentication, a valid lab identity,
role and ownership authorization, query input validation, and generic handling
of unhandled exceptions. HTTPX is required by FastAPI's `TestClient`.

## Next steps

- Add additional authorization and malformed-input cases as the lab grows.
- Add a machine-readable test report and a GitHub Actions workflow in a later
  stage.
