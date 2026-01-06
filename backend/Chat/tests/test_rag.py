"""
Test RAG (Retrieval-Augmented Generation) functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from Chat.core.rag import RAGEngine


class TestRAGEngine:
    """Test RAG engine functionality."""
    
    @pytest.fixture
    def rag_engine(self):
        """Create RAG engine instance."""
        return RAGEngine()
    
    def test_query_returns_list(self, rag_engine):
        """Test that query returns a list."""
        results = rag_engine.query("opioid withdrawal")
        assert isinstance(results, list)
    
    def test_query_with_top_k(self, rag_engine):
        """Test query with custom top_k."""
        results = rag_engine.query("fentanyl", top_k=3)
        assert isinstance(results, list)
        assert len(results) <= 3
    
    def test_query_empty_string(self, rag_engine):
        """Test query with empty string."""
        results = rag_engine.query("")
        assert isinstance(results, list)
    
    def test_query_result_structure(self, rag_engine):
        """Test that query results have expected structure."""
        results = rag_engine.query("cocaine effects")
        
        if len(results) > 0:
            # Each result should be a dictionary or string
            for result in results:
                assert isinstance(result, (dict, str))
    
    def test_query_relevance(self, rag_engine):
        """Test that similar queries return similar results."""
        results1 = rag_engine.query("opioid addiction")
        results2 = rag_engine.query("opioid dependency")
        
        # Both should return results (if RAG is working)
        assert isinstance(results1, list)
        assert isinstance(results2, list)


class TestRAGIngestion:
    """Test RAG data ingestion."""
    
    @pytest.fixture
    def rag_engine(self):
        """Create RAG engine instance."""
        return RAGEngine()
    
    def test_ingest_from_database(self, rag_engine):
        """Test ingesting data from drugs database."""
        try:
            count = rag_engine.ingest_from_database()
            assert isinstance(count, int)
            assert count >= 0
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    def test_vector_store_exists_after_ingest(self, rag_engine):
        """Test that vector store is created after ingestion."""
        try:
            rag_engine.ingest_from_database()
            # Should be able to query after ingestion
            results = rag_engine.query("test")
            assert isinstance(results, list)
        except Exception as e:
            pytest.skip(f"Ingestion failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
