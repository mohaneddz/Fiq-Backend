# Blog Service Tests

This directory contains tests for the Blog service.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_routes.py` - API endpoint tests
- `README.md` - This file

## Running Tests

From the `backend/Blog` directory:

```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_routes.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=Blog --cov-report=html
```

## Environment Setup

Tests require:
- `DB_URL` - Supabase database URL
- `SERVICE_ROLE_KEY` - Supabase service role key

Set these in a `.env` file in the backend directory.
