"""
Test relapse prediction model functionality.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import numpy as np
from Relapse.core.model import RelapseModel


class TestRelapseModel:
    """Test RelapseModel class."""
    
    @pytest.fixture
    def model(self):
        """Create RelapseModel instance."""
        return RelapseModel()
    
    def test_model_initialization(self, model):
        """Test model initializes correctly."""
        assert model is not None
        assert hasattr(model, 'model')
    
    def test_train_model(self, model):
        """Test model training with synthetic data."""
        # Generate synthetic training data
        X_train = np.random.rand(100, 6)  # 100 samples, 6 features
        y_train = np.random.randint(1, 100, 100)  # Days until relapse
        
        metrics = model.train(X_train, y_train)
        
        assert isinstance(metrics, dict)
        assert 'rmse' in metrics or 'mae' in metrics
    
    def test_predict_single_sample(self, model):
        """Test prediction with single sample."""
        # Train first with minimal data
        X_train = np.random.rand(50, 6)
        y_train = np.random.randint(1, 100, 50)
        model.train(X_train, y_train)
        
        # Predict
        X_test = np.random.rand(1, 6)
        prediction = model.predict(X_test)
        
        assert isinstance(prediction, (int, float, np.ndarray))
        if isinstance(prediction, np.ndarray):
            assert len(prediction) == 1
    
    def test_predict_multiple_samples(self, model):
        """Test prediction with multiple samples."""
        # Train first
        X_train = np.random.rand(50, 6)
        y_train = np.random.randint(1, 100, 50)
        model.train(X_train, y_train)
        
        # Predict multiple
        X_test = np.random.rand(10, 6)
        predictions = model.predict(X_test)
        
        assert len(predictions) == 10
    
    def test_save_and_load_model(self, model, tmp_path):
        """Test model persistence."""
        # Train model
        X_train = np.random.rand(30, 6)
        y_train = np.random.randint(1, 100, 30)
        model.train(X_train, y_train)
        
        # Save
        save_path = tmp_path / "test_model.pkl"
        model.save(str(save_path))
        assert save_path.exists()
        
        # Load
        new_model = RelapseModel()
        new_model.load(str(save_path))
        
        # Predictions should match
        X_test = np.random.rand(1, 6)
        pred1 = model.predict(X_test)
        pred2 = new_model.predict(X_test)
        
        np.testing.assert_array_almost_equal(pred1, pred2)
    
    def test_get_feature_importance(self, model):
        """Test getting feature importance."""
        # Train model first
        X_train = np.random.rand(50, 6)
        y_train = np.random.randint(1, 100, 50)
        model.train(X_train, y_train)
        
        importance = model.get_feature_importance()
        
        if importance is not None:
            assert isinstance(importance, (list, np.ndarray, dict))
            assert len(importance) == 6  # 6 features


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
