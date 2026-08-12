# Voice Service Tests

This directory contains tests for the Voice service.

## Test Structure

- `conftest.py` - Pytest configuration and shared fixtures
- `test_routes.py` - API endpoint tests
- `README.md` - This file

## Running Tests

From the `backend/Voice` directory:

```bash
pytest tests/ -v
```

Run specific test file:
```bash
pytest tests/test_routes.py -v
```

Run with coverage:
```bash
pytest tests/ --cov=Voice --cov-report=html
```

## Environment Setup

Tests require:
- `CHAT_SERVICE_URL` - Chat service URL (e.g., http://localhost:5001)

Set this in a `.env` file in the backend directory.

## Notes

- STT/TTS tests are skipped by default as they require models and audio hardware
- Integration tests require Chat service to be running
- Use `@pytest.mark.skip` for tests requiring expensive resources
