# Chat Service Tests

Comprehensive test suite for the Chat service covering all endpoints, features, and functionality.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_routes.py           # All API endpoint tests
├── test_validation.py       # Response validation tests
├── test_agent.py            # Agent orchestration tests
├── test_tools.py            # Tool functionality tests
└── test_rag.py              # RAG engine tests
```

## Running Tests

### Run All Tests
```bash
cd Chat
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_routes.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_routes.py::TestChatEndpoint -v
```

### Run Specific Test
```bash
pytest tests/test_routes.py::TestChatEndpoint::test_chat_drug_query -v
```

### Run with Coverage
```bash
pytest tests/ --cov=Chat --cov-report=html
```

## Test Coverage

### Endpoints Tested (test_routes.py)
- ✅ GET `/health` - Health check
- ✅ POST `/chat` - Full agent execution
  - Missing message validation
  - Drug query with tool calls
  - User history integration
  - Unknown drug handling
- ✅ POST `/chat/rag/query` - RAG retrieval
- ✅ POST `/chat/tools/drug_lookup` - Drug database query
- ✅ POST `/chat/tools/history_lookup` - User history query
- ✅ POST `/chat/websearch` - Web search
- ✅ POST `/chat/ingest/drugs` - Vector index building
- ✅ GET `/chat/logs/tail` - Log retrieval

### Response Validation (test_validation.py)
- ✅ Valid response schema validation
- ✅ Missing field detection
- ✅ Type checking (str, list, dict)
- ✅ Fallback response generation
- ✅ Safety field validation

### Agent Features (test_agent.py)
- ✅ Tool execution for all 4 tools
- ✅ Tool-call logging
- ✅ Conversation history management
- ✅ Fallback response handling
- ✅ Tool schema validation

### Tool Functionality (test_tools.py)
- ✅ DrugLookupTool
  - Existing drug lookup
  - Unknown drug handling
  - Case-insensitive search
  - Empty input validation
- ✅ HistoryLookupTool
  - User history retrieval
  - Empty user_id handling
  - Encounter structure validation

### RAG Engine (test_rag.py)
- ✅ Query execution
- ✅ Top-k results
- ✅ Result structure validation
- ✅ Database ingestion
- ✅ Vector store persistence

## Prerequisites

### Install Test Dependencies
```bash
pip install pytest pytest-cov
```

### Environment Setup
Ensure `.env` file has required variables:
```
GROQ_API_KEY=your_key_here
```

### Database Setup
Initialize databases before running tests:
```bash
cd Chat/data
sqlite3 drugs.db < drugs.sql
sqlite3 history.db < history.sql
```

## Test Data

Tests use:
- Mock Groq API responses (in conftest.py)
- Existing database records
- Synthetic test inputs

## Expected Failures

Some tests may skip if:
- GROQ_API_KEY not set
- Databases not initialized
- Model not trained (for prediction tests)

## CI/CD Integration

Add to GitHub Actions:
```yaml
- name: Run Chat tests
  run: |
    cd backend/Chat
    pytest tests/ -v --cov=Chat
```

## Writing New Tests

Follow this pattern:
```python
class TestNewFeature:
    """Test description."""
    
    @pytest.fixture
    def setup_data(self):
        """Fixture for test data."""
        return {"key": "value"}
    
    def test_feature_behavior(self, client, setup_data):
        """Test specific behavior."""
        response = client.post('/endpoint', json=setup_data)
        assert response.status_code == 200
```

## Coverage Goals

- Endpoint coverage: 100%
- Feature coverage: >90%
- Edge case coverage: >80%

## Troubleshooting

**Tests hanging:**
- Check if Groq API is responding
- Verify database connections

**Import errors:**
- Ensure `sys.path` includes backend directory
- Check all `__init__.py` files exist

**Fixture errors:**
- Review conftest.py setup
- Check fixture scope and dependencies
