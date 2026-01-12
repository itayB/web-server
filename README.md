# Web Server Template

A production-ready FastAPI template project with built-in health checks, structured logging, and comprehensive test coverage. Get started quickly with modern Python web development best practices.

## Prerequisites

- **[uv](https://docs.astral.sh/uv/)** - Fast Python package installer and environment manager (required)
- **pre-commit** - Git hook manager for code quality checks (install before first contribution)

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

## Running

```bash
python -m web_server
```

## Running with Docker

```bash
docker run -p 8080:8080 itayb/web-server:latest
```

## Contribution

```bash
pre-commit install --install-hooks -t pre-commit -t commit-msg
```

## Tests

```bash
py.test -o junit_family=xunit2 --junitxml result.xml -xv --ff --cov=web_server --cov-report=xml --cov-report=term-missing tests
```
