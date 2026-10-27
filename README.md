# API Security Testing Lab

![API Security Tests](https://github.com/agustiininicabral/api-security-testing-lab/actions/workflows/tests.yml/badge.svg)

A small, local-only FastAPI project for practicing automated API security tests.
The sample tokens and profiles are fictional, and the application makes no
requests to external systems. This is a training lab, not production
authentication or authorization code.

## Requirements

- Python 3.12
- Runtime dependencies are declared in `requirements.txt`
- Test and development dependencies are declared in `requirements-dev.txt`
- `requirements-lock.txt` pins the resolved dependency versions, including transitives

## Install (Windows PowerShell)

Create a virtual environment and install the development dependencies with the
version constraints:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -c requirements-lock.txt
```

To install only the API runtime:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -c requirements-lock.txt
```

## Run locally

Start the API on the loopback interface:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The sample endpoints are `/health`, `/protected`,
`/users/{username}/profile`, and `/items?limit=10`.

## Run tests and quality checks

Run the complete test suite and generate a JUnit report:

```powershell
.\.venv\Scripts\python.exe -m pytest -v --junitxml=pytest-report.xml
```

Check formatting, lint rules, and dependency consistency:

```powershell
.\.venv\Scripts\ruff.exe format --check app tests
.\.venv\Scripts\ruff.exe check app tests
.\.venv\Scripts\python.exe -m pip check
```

The generated test report is excluded from version control. GitHub Actions runs
these checks on pushes and pull requests, then uploads the JUnit report as a
short-lived artifact.

## Security scenarios covered

- Missing, invalid, and malformed bearer credentials.
- Case-insensitive bearer scheme handling.
- User and administrator roles.
- Ownership-based profile access and forbidden cross-user access.
- Missing authentication on protected profile routes.
- Query parameter validation, including lower and upper bounds.
- Generic HTTP 500 responses that do not expose internal exception details.
- Registration of the generic exception handler.

The tokens are hard-coded fictional lab values by design. Do not use this
application as a production authentication system or expose it to an untrusted
network.

## Verified CI evidence

- [GitHub Actions run — 27 October 2026](https://github.com/agustiininicabral/api-security-testing-lab/actions/runs/40451076624): **success**.
- **30 tests passed**, with dependency consistency, Ruff formatting, and lint checks passing.
- Pytest reported one Starlette/AnyIO deprecation warning; it does not fail the suite and remains a known cleanup item.
- The JUnit XML report is uploaded as a workflow artifact and retained for 7 days.

## License

MIT. See [LICENSE](LICENSE).
