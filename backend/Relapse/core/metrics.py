"""
Metrics calculation for model evaluation.
"""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict


class ModelMetrics:
    """Calculate and format model performance metrics."""
    
    @staticmethod
    def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate regression metrics.
        
        Args:
            y_true: True values
            y_pred: Predicted values
            
        Returns:
            Dictionary of metrics
        """
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_true, y_pred)
        
        # Mean Absolute Percentage Error
        mape = np.mean(np.abs((y_true - y_pred) / np.maximum(y_true, 1))) * 100
        
        return {
            'mae': float(mae),
            'mse': float(mse),
            'rmse': float(rmse),
            'r2': float(r2),
            'mape': float(mape)
        }
    
    @staticmethod
    def format_metrics(metrics: Dict[str, float]) -> str:
        """
        Format metrics for display.
        
        Args:
            metrics: Dictionary of metrics
            
        Returns:
            Formatted string
        """
        return f"""
Model Performance Metrics:
- MAE (Mean Absolute Error): {metrics.get('mae', 0):.2f} days
- RMSE (Root Mean Squared Error): {metrics.get('rmse', 0):.2f} days
- R² Score: {metrics.get('r2', 0):.4f}
- MAPE (Mean Absolute Percentage Error): {metrics.get('mape', 0):.2f}%
"""
