"""
Model training and prediction for relapse time series.
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from typing import Dict, Any, Optional
import joblib
from Relapse import config
from Relapse.core.features import FeatureEngineering
from Relapse.core.metrics import ModelMetrics
from Relapse.core.storage import ModelStorage


class RelapsePredictor:
    """Relapse time prediction model."""
    
    def __init__(self):
        self.model: Optional[XGBRegressor] = None
        self.feature_engineer = FeatureEngineering()
        self.storage = ModelStorage()
        self.is_trained = False
        
        # Try to load existing model
        self.load_model()
    
    def train(self, training_data: pd.DataFrame = None) -> Dict[str, Any]:
        """
        Train the relapse prediction model.
        
        Args:
            training_data: DataFrame with features and target. If None, uses synthetic data.
            
        Returns:
            Dictionary with training results and metrics
        """
        try:
            # Use provided data or generate synthetic data
            if training_data is None:
                training_data = self.feature_engineer.create_sample_data(n_samples=200)
            
            # Split features and target
            feature_columns = [
                'days_clean', 'craving_trend', 'sleep_deviation',
                'trigger_count', 'support_sessions', 'medication_adherence'
            ]
            
            X = training_data[feature_columns].values
            y = training_data['relapse_time_days'].values
            
            # Train/test split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=config.TEST_SIZE,
                random_state=config.RANDOM_STATE
            )
            
            # Initialize and train model
            self.model = XGBRegressor(
                n_estimators=config.N_ESTIMATORS,
                max_depth=config.MAX_DEPTH,
                learning_rate=config.LEARNING_RATE,
                random_state=config.RANDOM_STATE,
                objective='reg:squarederror'
            )
            
            self.model.fit(X_train, y_train)
            self.is_trained = True
            
            # Calculate metrics
            y_pred_train = self.model.predict(X_train)
            y_pred_test = self.model.predict(X_test)
            
            metrics = {
                'train': ModelMetrics.calculate_metrics(y_train, y_pred_train),
                'test': ModelMetrics.calculate_metrics(y_test, y_pred_test),
                'feature_importance': dict(zip(
                    feature_columns,
                    self.model.feature_importances_.tolist()
                ))
            }
            
            # Save model
            save_result = self.save_model(metrics)
            
            return {
                'status': 'success',
                'metrics': metrics,
                'samples_trained': len(X_train),
                'samples_tested': len(X_test),
                'model_saved': save_result['success'],
                'model_version': save_result.get('version')
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def predict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict relapse time in days.
        
        Args:
            data: Dictionary with raw behavioral signals
            
        Returns:
            Dictionary with prediction and risk assessment
        """
        if not self.is_trained:
            return {
                'status': 'error',
                'error': 'Model not trained. Please train the model first.'
            }
        
        try:
            # Engineer features
            features = self.feature_engineer.engineer_features(data)
            
            # Validate features
            is_valid, error_msg = self.feature_engineer.validate_features(features)
            if not is_valid:
                return {
                    'status': 'error',
                    'error': f'Invalid features: {error_msg}'
                }
            
            # Convert to array
            X = self.feature_engineer.features_to_array(features)
            
            # Predict
            prediction = self.model.predict(X)[0]
            
            # Calculate risk level
            risk_level = self._assess_risk(prediction, features)
            
            return {
                'status': 'success',
                'prediction': {
                    'relapse_time_days': float(prediction),
                    'risk_level': risk_level,
                    'confidence': 'moderate'  # Could be enhanced with prediction intervals
                },
                'features': features
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _assess_risk(self, predicted_days: float, features: Dict[str, float]) -> str:
        """
        Assess risk level based on prediction and features.
        
        Args:
            predicted_days: Predicted time to relapse
            features: Engineered features
            
        Returns:
            Risk level: "low", "moderate", "high", "critical"
        """
        # Risk based on predicted time
        if predicted_days > 90:
            return "low"
        elif predicted_days > 30:
            return "moderate"
        elif predicted_days > 7:
            return "high"
        else:
            return "critical"
    
    def save_model(self, metrics: Dict = None) -> Dict[str, Any]:
        """Save model to disk."""
        if not self.is_trained:
            return {'success': False, 'error': 'No trained model to save'}
        
        try:
            joblib.dump(self.model, config.MODEL_PATH)
            version_info = self.storage.save_version(metrics)
            return {'success': True, 'version': version_info.get('version')}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def load_model(self) -> bool:
        """Load model from disk."""
        if os.path.exists(config.MODEL_PATH):
            try:
                self.model = joblib.load(config.MODEL_PATH)
                self.is_trained = True
                return True
            except Exception as e:
                print(f"Failed to load model: {e}")
                return False
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and version."""
        if not self.is_trained:
            return {'status': 'not_trained'}
        
        version_info = self.storage.get_latest_version()
        return {
            'status': 'trained',
            'model_type': 'XGBoostRegressor',
            'version': version_info.get('version', 'unknown'),
            'trained_at': version_info.get('timestamp', 'unknown'),
            'metrics': version_info.get('metrics', {})
        }
