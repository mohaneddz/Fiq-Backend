"""
Test all Chat service endpoints.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import json
from Chat.app import create_app


@pytest.fixture
def client():
    """Create test client."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test /health endpoint."""
    
    def test_health_check(self, client):
        """Test health endpoint returns 200 and correct structure."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'request_id' in data
        assert data['data']['status'] == 'healthy'
        assert data['data']['service'] == 'chat'


class TestChatEndpoint:
    """Test /chat endpoint (full agent execution)."""
    
    def test_chat_missing_message(self, client):
        """Test chat endpoint with missing message."""
        response = client.post('/chat',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Message is required' in data['error']
    
    def test_chat_drug_query(self, client):
        """Test chat with drug-related question."""
        response = client.post('/chat',
                              json={
                                  'message': 'What are the risks of fentanyl?',
                                  'user_id': 'test_user_123'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'response' in data['data']
        
        # Validate response schema
        resp = data['data']['response']
        assert 'summary' in resp
        assert 'risks' in resp
        assert 'what_to_do' in resp
        assert 'safety' in resp
        assert 'urgent_signs' in resp['safety']
        assert 'hotlines' in resp['safety']
        
        # Check types
        assert isinstance(resp['summary'], str)
        assert isinstance(resp['risks'], list)
        assert isinstance(resp['what_to_do'], list)
        assert isinstance(resp['safety']['urgent_signs'], list)
        assert isinstance(resp['safety']['hotlines'], list)
    
    def test_chat_with_user_id(self, client):
        """Test chat with user_id for personalized responses."""
        response = client.post('/chat',
                              json={
                                  'message': 'Can you summarize my progress?',
                                  'user_id': 'user_456'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'response' in data['data']
    
    def test_chat_unknown_drug(self, client):
        """Test chat with unknown/made-up drug."""
        response = client.post('/chat',
                              json={
                                  'message': 'What are the risks of Xylazine-XYZ-999?',
                                  'user_id': 'test_user_789'
                              },
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        
        resp = data['data']['response']
        summary = resp['summary'].lower()
        # Should indicate drug not found
        assert any(phrase in summary for phrase in ['not found', 'unable to verify', 'unknown'])


class TestRAGEndpoint:
    """Test /chat/rag/query endpoint."""
    
    def test_rag_query_success(self, client):
        """Test RAG query with valid input."""
        response = client.post('/chat/rag/query',
                              json={'query': 'opioid withdrawal symptoms'},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'results' in data['data']
        assert isinstance(data['data']['results'], list)
    
    def test_rag_query_missing_query(self, client):
        """Test RAG query without query parameter."""
        response = client.post('/chat/rag/query',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400


class TestToolEndpoints:
    """Test tool-specific endpoints."""
    
    def test_drug_lookup_found(self, client):
        """Test drug lookup with existing drug."""
        response = client.post('/chat/tools/drug_lookup',
                              json={'drug_name': 'Cocaine'},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'found' in data['data']
    
    def test_drug_lookup_missing_name(self, client):
        """Test drug lookup without drug_name."""
        response = client.post('/chat/tools/drug_lookup',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400
    
    def test_history_lookup_with_user_id(self, client):
        """Test history lookup with user_id."""
        response = client.post('/chat/tools/history_lookup',
                              json={'user_id': 'user_001'},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'found' in data['data']
    
    def test_history_lookup_missing_user_id(self, client):
        """Test history lookup without user_id."""
        response = client.post('/chat/tools/history_lookup',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400


class TestWebSearchEndpoint:
    """Test /chat/websearch endpoint."""
    
    def test_websearch_query(self, client):
        """Test web search with query."""
        response = client.post('/chat/websearch',
                              json={'query': 'naloxone availability'},
                              content_type='application/json')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_websearch_missing_query(self, client):
        """Test web search without query."""
        response = client.post('/chat/websearch',
                              json={},
                              content_type='application/json')
        assert response.status_code == 400


class TestIngestEndpoint:
    """Test /chat/ingest/drugs endpoint."""
    
    def test_ingest_drugs(self, client):
        """Test building vector index from drugs database."""
        response = client.post('/chat/ingest/drugs')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'count' in data['data']


class TestLogsEndpoint:
    """Test /chat/logs/tail endpoint."""
    
    def test_tail_logs_default(self, client):
        """Test tailing logs with default count."""
        response = client.get('/chat/logs/tail')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'logs' in data['data']
        assert isinstance(data['data']['logs'], list)
    
    def test_tail_logs_with_count(self, client):
        """Test tailing logs with custom count."""
        response = client.get('/chat/logs/tail?n=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']['logs']) <= 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
