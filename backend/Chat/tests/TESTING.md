# Test Requirements

## Install Test Dependencies

For coverage reports, install pytest-cov:

```bash
pip install pytest-cov
```

Then run with coverage:
```bash
pytest tests/ --cov=Chat --cov-report=html
```

## Basic Test Run (without coverage)

```bash
pytest tests/ -v
```

## Quick Test Run

```bash
# Run all tests
pytest tests/

# Run specific file
pytest tests/test_routes.py -v

# Run specific test
pytest tests/test_routes.py::TestChatEndpoint::test_chat_drug_query -v
```
