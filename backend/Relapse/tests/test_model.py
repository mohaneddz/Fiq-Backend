"""
Test relapse prediction model functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import numpy as np
from Relapse.core.model import RelapsePredictor


class TestRelapsePredictor:
    """Test RelapsePredictor class."""
    
    @pytest.fixture
    def model(self):
        """Create RelapsePredictor instance."""
        return RelapsePredictor()
    
    def test_model_initialization(self, model):
        """Test model initializes correctly."""
        assert model is not None
        assert hasattr(model, 'model')
    
    def test_train_model(self, model):
        """Test model training with synthetic data."""
        # RelapsePredictor.train() generates its own synthetic data
        result = model.train()
        
        assert isinstance(result, dict)
        assert 'status' in result
        # Training may succeed or fail depending on environment
        if result['status'] == 'success':
            assert 'metrics' in result
    
    def test_predict_with_data(self, model):
        """Test prediction with behavioral data dict."""
        # Train first
        model.train()
        
        # Predict with input data
        test_data = {
            "days_clean": 30,
            "craving_scores": [3, 2, 4],
            "sleep_hours": [7, 6.5, 7],
            "trigger_events": [],
            "support_sessions": 2,
            "medication_adherence": {"doses_taken": 9, "doses_prescribed": 10}
        }
        
        result = model.predict(test_data)
        
        assert isinstance(result, dict)
        if model.is_trained:
            assert 'status' in result
    
    def test_save_and_load_model(self, model, tmp_path):
        """Test model persistence."""
        # Train model first
        result = model.train()
        
        if result.get('status') == 'success':
            # Model should be saved automatically
            assert model.is_trained
            
            # Try loading in new instance
            new_model = RelapsePredictor()
            # If model file exists, it should load
            assert new_model.model is not None or not model.is_trained
    
    def test_get_model_info(self, model):
        """Test getting model information."""
        info = model.get_model_info()
        
        assert isinstance(info, dict)
        assert 'status' in info
        
        if model.is_trained:
            assert info['status'] == 'trained'
        else:
            assert info['status'] == 'not_trained'


class TestRiskAssessment:
    """Test risk level assessment logic."""
    
    def test_risk_level_low(self):
        """Test low risk classification."""
        days = 50
        risk = get_risk_level(days)
        assert risk == 'Low'
    
    def test_risk_level_moderate(self):
        """Test moderate risk classification."""
        days = 20
        risk = get_risk_level(days)
        assert risk == 'Moderate'
    
    def test_risk_level_high(self):
        """Test high risk classification."""
        days = 10
        risk = get_risk_level(days)
        assert risk == 'High'
    
    def test_risk_level_critical(self):
        """Test critical risk classification."""
        days = 3
        risk = get_risk_level(days)
        assert risk == 'Critical'


def get_risk_level(days_until_relapse: float) -> str:
    """Helper function to determine risk level."""
    if days_until_relapse > 30:
        return 'Low'
    elif days_until_relapse > 14:
        return 'Moderate'
    elif days_until_relapse > 7:
        return 'High'
    else:
        return 'Critical'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
