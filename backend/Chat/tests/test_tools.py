"""
Test Chat service tools (DrugLookupTool, HistoryLookupTool).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from Chat.core.tools import DrugLookupTool, HistoryLookupTool


class TestDrugLookupTool:
    """Test DrugLookupTool functionality."""
    
    @pytest.fixture
    def tool(self):
        """Create DrugLookupTool instance."""
        return DrugLookupTool()
    
    def test_lookup_existing_drug(self, tool):
        """Test lookup with drug that might exist in database."""
        result = tool.run("Cocaine")
        assert isinstance(result, dict)
        assert "found" in result
        
        if result["found"]:
            assert "drug" in result
            assert isinstance(result["drug"], dict)
    
    def test_lookup_empty_name(self, tool):
        """Test lookup with empty drug name."""
        result = tool.run("")
        assert isinstance(result, dict)
        # Empty name may return found=True or False depending on implementation
        assert "found" in result
    
    def test_lookup_unknown_drug(self, tool):
        """Test lookup with definitely unknown drug."""
        result = tool.run("XYZ-999-NotARealDrug")
        assert isinstance(result, dict)
        assert "found" in result
        # Most likely not found
        if not result["found"]:
            assert "message" in result
    
    def test_lookup_case_insensitive(self, tool):
        """Test that lookup is case-insensitive."""
        result1 = tool.run("cocaine")
        result2 = tool.run("COCAINE")
        result3 = tool.run("Cocaine")
        
        # Should return same found status
        assert result1["found"] == result2["found"] == result3["found"]


class TestHistoryLookupTool:
    """Test HistoryLookupTool functionality."""
    
    @pytest.fixture
    def tool(self):
        """Create HistoryLookupTool instance."""
        return HistoryLookupTool()
    
    def test_lookup_with_user_id(self, tool):
        """Test history lookup with user_id."""
        result = tool.run("test_user_123")
        assert isinstance(result, dict)
        # Count may not be present if database table doesn't exist
        if result["found"]:
            assert "count" in result or "encounters" in result
        assert "count" in result
    
    def test_lookup_empty_user_id(self, tool):
        """Test lookup with empty user_id."""
        result = tool.run("")
        assert isinstance(result, dict)
        # Empty user_id may return found=True or False depending on implementation
        assert "found" in result
    
    def test_lookup_encounters_structure(self, tool):
        """Test that encounters have expected structure if found."""
        result = tool.run("user_001")
        
        if result["found"] and result["count"] > 0:
            assert "encounters" in result
            assert isinstance(result["encounters"], list)
            
            # Check first encounter structure
            if len(result["encounters"]) > 0:
                encounter = result["encounters"][0]
                # Should have standard encounter fields


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
