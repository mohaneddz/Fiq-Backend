"""
Test feature engineering for relapse prediction.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import numpy as np
from Relapse.core.features import FeatureEngineering


class TestFeatureEngineering:
    """Test FeatureEngineering class."""
    
    @pytest.fixture
    def feature_engineer(self):
        """Create FeatureEngineering instance."""
        return FeatureEngineering()
    
    @pytest.fixture
    def sample_input(self):
        """Sample input data for feature extraction."""
        return {
            "days_clean": 30,
            "craving_scores": [3, 2, 4, 3, 2],
            "sleep_hours": [7, 6.5, 7, 8, 6],
            "trigger_events": [{"days_ago": 3}],
            "support_sessions": 2,
            "medication_adherence": {
                "doses_taken": 9,
                "doses_prescribed": 10
            }
        }
    
    def test_extract_features_returns_dict(self, feature_engineer, sample_input):
        """Test that engineer_features returns a dictionary."""
        features = feature_engineer.engineer_features(sample_input)
        assert isinstance(features, dict)
    
    def test_all_six_features_present(self, feature_engineer, sample_input):
        """Test that all 6 required features are extracted."""
        features = feature_engineer.engineer_features(sample_input)
        
        required_features = [
            'days_clean',
            'craving_trend',
            'sleep_deviation',
            'trigger_count',
            'support_sessions',
            'medication_adherence'
        ]
        
        for feature in required_features:
            assert feature in features, f"Missing feature: {feature}"
    
    def test_days_clean_feature(self, feature_engineer, sample_input):
        """Test days_clean feature extraction."""
        features = feature_engineer.engineer_features(sample_input)
        assert features['days_clean'] == 30
        assert isinstance(features['days_clean'], (int, float))
    
    def test_craving_trend_calculation(self, feature_engineer, sample_input):
        """Test craving_trend is calculated correctly."""
        features = feature_engineer.engineer_features(sample_input)
        
        # Should be rolling average
        expected_avg = np.mean(sample_input['craving_scores'])
        assert abs(features['craving_trend'] - expected_avg) < 0.01
    
    def test_sleep_deviation_calculation(self, feature_engineer, sample_input):
        """Test sleep_deviation is calculated correctly."""
        features = feature_engineer.engineer_features(sample_input)
        
        # Should be standard deviation
        expected_std = np.std(sample_input['sleep_hours'])
        assert abs(features['sleep_deviation'] - expected_std) < 0.01
    
    def test_trigger_count_feature(self, feature_engineer, sample_input):
        """Test trigger_count feature extraction."""
        features = feature_engineer.engineer_features(sample_input)
        
        # Should count triggers within window (e.g., 7 days)
        assert features['trigger_count'] >= 0
        assert isinstance(features['trigger_count'], (int, float))
    
    def test_support_sessions_feature(self, feature_engineer, sample_input):
        """Test support_sessions feature extraction."""
        features = feature_engineer.engineer_features(sample_input)
        assert features['support_sessions'] == 2
    
    def test_medication_adherence_calculation(self, feature_engineer, sample_input):
        """Test medication_adherence percentage calculation."""
        features = feature_engineer.engineer_features(sample_input)
        
        expected = (9 / 10) * 100  # 90%
        assert abs(features['medication_adherence'] - expected) < 0.01
    
    def test_empty_craving_scores(self, feature_engineer):
        """Test handling of empty craving scores."""
        input_data = {
            "days_clean": 10,
            "craving_scores": [],
            "sleep_hours": [7],
            "trigger_events": [],
            "support_sessions": 1,
            "medication_adherence": {"doses_taken": 5, "doses_prescribed": 5}
        }
        
        features = feature_engineer.engineer_features(input_data)
        assert 'craving_trend' in features
        assert features['craving_trend'] == 0 or not np.isnan(features['craving_trend'])
    
    def test_zero_medication_prescribed(self, feature_engineer):
        """Test handling when no medication prescribed."""
        input_data = {
            "days_clean": 10,
            "craving_scores": [2],
            "sleep_hours": [7],
            "trigger_events": [],
            "support_sessions": 1,
            "medication_adherence": {"doses_taken": 0, "doses_prescribed": 0}
        }
        
        features = feature_engineer.engineer_features(input_data)
        # Should handle division by zero gracefully
        assert 'medication_adherence' in features
        assert features['medication_adherence'] >= 0
    
    def test_features_dict_values(self, feature_engineer, sample_input):
        """Test that features contain valid numeric values."""
        features = feature_engineer.engineer_features(sample_input)
        
        # Check all features are numeric and not NaN
        for key, value in features.items():
            assert isinstance(value, (int, float))
            assert not np.isnan(value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
