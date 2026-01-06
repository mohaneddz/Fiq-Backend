"""
Feature engineering for relapse prediction.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from Relapse import config


class FeatureEngineering:
    """Feature engineering pipeline for relapse prediction."""
    
    @staticmethod
    def engineer_features(data: Dict[str, Any]) -> Dict[str, float]:
        """
        Engineer features from raw behavioral data.
        
        Args:
            data: Dictionary containing raw behavioral signals
            
        Returns:
            Dictionary of engineered features
        """
        features = {}
        
        # Feature 1: Days clean (direct feature)
        features['days_clean'] = float(data.get('days_clean', 0))
        
        # Feature 2: Craving trend (rolling average)
        craving_scores = data.get('craving_scores', [])
        if craving_scores:
            features['craving_trend'] = float(np.mean(craving_scores[-config.CRAVING_WINDOW_DAYS:]))
        else:
            features['craving_trend'] = 0.0
        
        # Feature 3: Sleep deviation (standard deviation of sleep hours)
        sleep_hours = data.get('sleep_hours', [])
        if len(sleep_hours) > 1:
            features['sleep_deviation'] = float(np.std(sleep_hours[-config.SLEEP_WINDOW_DAYS:]))
        else:
            features['sleep_deviation'] = 0.0
        
        # Feature 4: Trigger count (sum of weekly triggers)
        trigger_events = data.get('trigger_events', [])
        if trigger_events:
            features['trigger_count'] = float(len([t for t in trigger_events 
                                                   if t.get('days_ago', 999) <= config.TRIGGER_WINDOW_DAYS]))
        else:
            features['trigger_count'] = 0.0
        
        # Feature 5: Support sessions (count of therapy/support meetings)
        features['support_sessions'] = float(data.get('support_sessions', 0))
        
        # Feature 6: Medication adherence (percentage)
        adherence_data = data.get('medication_adherence', {})
        doses_taken = adherence_data.get('doses_taken', 0)
        doses_prescribed = adherence_data.get('doses_prescribed', 1)
        features['medication_adherence'] = float((doses_taken / doses_prescribed) * 100) if doses_prescribed > 0 else 0.0
        
        return features
    
    @staticmethod
    def validate_features(features: Dict[str, float]) -> tuple[bool, str]:
        """
        Validate engineered features.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_features = [
            'days_clean',
            'craving_trend',
            'sleep_deviation',
            'trigger_count',
            'support_sessions',
            'medication_adherence'
        ]
        
        # Check all required features present
        missing = [f for f in required_features if f not in features]
        if missing:
            return False, f"Missing features: {', '.join(missing)}"
        
        # Check for NaN or infinite values
        for name, value in features.items():
            if not np.isfinite(value):
                return False, f"Invalid value for {name}: {value}"
        
        # Check ranges
        if features['days_clean'] < 0:
            return False, "days_clean cannot be negative"
        
        if features['medication_adherence'] < 0 or features['medication_adherence'] > 100:
            return False, "medication_adherence must be between 0 and 100"
        
        return True, ""
    
    @staticmethod
    def features_to_array(features: Dict[str, float]) -> np.ndarray:
        """
        Convert features dictionary to numpy array.
        
        Args:
            features: Dictionary of features
            
        Returns:
            Numpy array in correct order
        """
        feature_order = [
            'days_clean',
            'craving_trend',
            'sleep_deviation',
            'trigger_count',
            'support_sessions',
            'medication_adherence'
        ]
        
        return np.array([[features[f] for f in feature_order]])
    
    @staticmethod
    def create_sample_data(n_samples: int = 100) -> pd.DataFrame:
        """
        Create synthetic training data for model development.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            DataFrame with features and target
        """
        np.random.seed(config.RANDOM_STATE)
        
        # Generate features
        days_clean = np.random.randint(0, 180, n_samples)
        craving_trend = np.random.uniform(0, 10, n_samples)
        sleep_deviation = np.random.uniform(0, 3, n_samples)
        trigger_count = np.random.randint(0, 20, n_samples)
        support_sessions = np.random.randint(0, 8, n_samples)
        medication_adherence = np.random.uniform(0, 100, n_samples)
        
        # Generate target (relapse_time_days) based on features
        # More days clean, more support sessions, better adherence -> longer relapse time
        # More cravings, sleep issues, triggers -> shorter relapse time
        relapse_time_days = (
            days_clean * 0.3 +
            (10 - craving_trend) * 5 +
            (3 - sleep_deviation) * 10 +
            (20 - trigger_count) * 2 +
            support_sessions * 8 +
            medication_adherence * 0.5 +
            np.random.normal(0, 15, n_samples)
        )
        
        # Ensure non-negative
        relapse_time_days = np.maximum(relapse_time_days, 1)
        
        df = pd.DataFrame({
            'days_clean': days_clean,
            'craving_trend': craving_trend,
            'sleep_deviation': sleep_deviation,
            'trigger_count': trigger_count,
            'support_sessions': support_sessions,
            'medication_adherence': medication_adherence,
            'relapse_time_days': relapse_time_days
        })
        
        return df
