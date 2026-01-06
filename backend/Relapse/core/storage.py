"""
Model versioning and storage management.
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from Relapse import config


class ModelStorage:
    """Manage model versions and metadata."""
    
    def __init__(self):
        self.version_file = config.MODEL_VERSION_FILE
        os.makedirs(os.path.dirname(self.version_file), exist_ok=True)
    
    def save_version(self, metrics: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Save model version information.
        
        Args:
            metrics: Model performance metrics
            
        Returns:
            Version information
        """
        # Get current version number
        version_history = self._load_version_history()
        new_version = len(version_history) + 1
        
        version_info = {
            'version': f'v{new_version}',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'metrics': metrics or {},
            'model_type': 'XGBoostRegressor',
            'config': {
                'n_estimators': config.N_ESTIMATORS,
                'max_depth': config.MAX_DEPTH,
                'learning_rate': config.LEARNING_RATE
            }
        }
        
        # Append to history
        version_history.append(version_info)
        
        # Save to file
        with open(self.version_file, 'w') as f:
            json.dump(version_history, f, indent=2)
        
        return version_info
    
    def get_latest_version(self) -> Dict[str, Any]:
        """
        Get latest model version information.
        
        Returns:
            Latest version info or empty dict
        """
        version_history = self._load_version_history()
        if version_history:
            return version_history[-1]
        return {}
    
    def get_version_history(self) -> list[Dict[str, Any]]:
        """
        Get complete version history.
        
        Returns:
            List of all versions
        """
        return self._load_version_history()
    
    def _load_version_history(self) -> list[Dict[str, Any]]:
        """Load version history from file."""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []
