"""
Test response validation functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
from Chat.api.routes import validate_response_schema, get_fallback_response


class TestResponseValidation:
    """Test response schema validation."""
    
    def test_valid_response(self):
        """Test validation with valid response structure."""
        valid_response = {
            "summary": "This is a valid summary.",
            "risks": ["Risk 1", "Risk 2"],
            "what_to_do": ["Action 1", "Action 2"],
            "safety": {
                "urgent_signs": ["Sign 1", "Sign 2"],
                "hotlines": ["988", "1-800-662-4357"]
            }
        }
        
        result = validate_response_schema(valid_response)
        assert result == valid_response
    
    def test_missing_summary(self):
        """Test validation with missing summary."""
        invalid_response = {
            "risks": ["Risk 1"],
            "what_to_do": ["Action 1"],
            "safety": {
                "urgent_signs": ["Sign 1"],
                "hotlines": ["988"]
            }
        }
        
        result = validate_response_schema(invalid_response)
        assert result != invalid_response
        assert "summary" in result  # Should have fallback
    
    def test_missing_risks(self):
        """Test validation with missing risks."""
        invalid_response = {
            "summary": "Summary here",
            "what_to_do": ["Action 1"],
            "safety": {
                "urgent_signs": ["Sign 1"],
                "hotlines": ["988"]
            }
        }
        
        result = validate_response_schema(invalid_response)
        assert "risks" in result
        assert isinstance(result["risks"], list)
    
    def test_invalid_safety_structure(self):
        """Test validation with invalid safety object."""
        invalid_response = {
            "summary": "Summary here",
            "risks": ["Risk 1"],
            "what_to_do": ["Action 1"],
            "safety": {
                "urgent_signs": ["Sign 1"]
                # Missing hotlines
            }
        }
        
        result = validate_response_schema(invalid_response)
        assert "hotlines" in result["safety"]
        assert isinstance(result["safety"]["hotlines"], list)
    
    def test_wrong_types(self):
        """Test validation with wrong field types."""
        invalid_response = {
            "summary": 123,  # Should be string
            "risks": "not a list",
            "what_to_do": ["Action 1"],
            "safety": {
                "urgent_signs": ["Sign 1"],
                "hotlines": ["988"]
            }
        }
        
        result = validate_response_schema(invalid_response)
        assert isinstance(result["summary"], str)
        assert isinstance(result["risks"], list)
    
    def test_not_dict(self):
        """Test validation with non-dict input."""
        result = validate_response_schema("not a dict")
        fallback = get_fallback_response()
        assert result == fallback
    
    def test_fallback_response_structure(self):
        """Test that fallback response has correct structure."""
        fallback = get_fallback_response()
        
        assert "summary" in fallback
        assert "risks" in fallback
        assert "what_to_do" in fallback
        assert "safety" in fallback
        assert "urgent_signs" in fallback["safety"]
        assert "hotlines" in fallback["safety"]
        
        # Validate types
        assert isinstance(fallback["summary"], str)
        assert isinstance(fallback["risks"], list)
        assert isinstance(fallback["what_to_do"], list)
        assert isinstance(fallback["safety"]["urgent_signs"], list)
        assert isinstance(fallback["safety"]["hotlines"], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
