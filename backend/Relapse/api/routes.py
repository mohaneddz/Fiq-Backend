"""
API routes for Relapse service.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from flask import Blueprint, request, jsonify, current_app
from time import time
from shared.schemas import APIResponse, generate_request_id
from shared.utils import safe_int
from Relapse.core.model import RelapsePredictor
from Relapse.core.features import FeatureEngineering
from Relapse import prompts

relapse_bp = Blueprint('relapse', __name__)

# Initialize predictor
_predictor = None


def get_predictor():
    """Lazy initialize predictor."""
    global _predictor
    if _predictor is None:
        _predictor = RelapsePredictor()
    return _predictor


@relapse_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    request_id = generate_request_id()
    return jsonify(APIResponse.success(
        data={"status": "healthy", "service": "relapse"},
        request_id=request_id
    ).to_dict())


@relapse_bp.route('/relapse/predict', methods=['POST'])
def predict():
    """Predict relapse time endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        
        # Get predictor and predict
        predictor = get_predictor()
        result = predictor.predict(data)
        
        if result.get('status') == 'error':
            latency_ms = (time() - start_time) * 1000
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint="/relapse/predict",
                status="error",
                latency_ms=latency_ms,
                error=result.get('error')
            )
            return jsonify(APIResponse.error(
                result.get('error'),
                request_id=request_id
            ).to_dict()), 400
        
        # Add disclaimer
        result['disclaimer'] = prompts.PREDICTION_DISCLAIMER
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/predict",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/predict",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@relapse_bp.route('/relapse/features', methods=['POST'])
def debug_features():
    """Debug engineered features endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        data = request.get_json()
        
        # Engineer features
        feature_eng = FeatureEngineering()
        features = feature_eng.engineer_features(data)
        
        # Validate
        is_valid, error_msg = feature_eng.validate_features(features)
        
        # Add explanations
        result = {
            'features': features,
            'valid': is_valid,
            'error': error_msg if not is_valid else None,
            'explanations': prompts.FEATURE_EXPLANATIONS
        }
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/features",
            status="success",
            latency_ms=latency_ms
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/features",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@relapse_bp.route('/relapse/train', methods=['POST'])
def train():
    """Train/update model endpoint."""
    request_id = generate_request_id()
    start_time = time()
    
    try:
        # Get optional training data
        data = request.get_json() if request.is_json else None
        training_data = data.get('training_data') if data else None
        
        # Train model
        predictor = get_predictor()
        result = predictor.train(training_data)
        
        if result.get('status') == 'error':
            latency_ms = (time() - start_time) * 1000
            current_app.logger_instance.log_request(
                request_id=request_id,
                endpoint="/relapse/train",
                status="error",
                latency_ms=latency_ms,
                error=result.get('error')
            )
            return jsonify(APIResponse.error(
                result.get('error'),
                request_id=request_id
            ).to_dict()), 500
        
        # Log request
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/train",
            status="success",
            latency_ms=latency_ms,
            metadata={'samples_trained': result.get('samples_trained')}
        )
        
        return jsonify(APIResponse.success(
            data=result,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        latency_ms = (time() - start_time) * 1000
        current_app.logger_instance.log_request(
            request_id=request_id,
            endpoint="/relapse/train",
            status="error",
            latency_ms=latency_ms,
            error=str(e)
        )
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@relapse_bp.route('/relapse/model/info', methods=['GET'])
def model_info():
    """Get model version and metrics endpoint."""
    request_id = generate_request_id()
    
    try:
        predictor = get_predictor()
        info = predictor.get_model_info()
        
        return jsonify(APIResponse.success(
            data=info,
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500


@relapse_bp.route('/relapse/logs/tail', methods=['GET'])
def tail_logs():
    """Tail log file endpoint."""
    request_id = generate_request_id()
    
    try:
        n = safe_int(request.args.get('n', 200))
        logs = current_app.logger_instance.tail_logs(n)
        
        return jsonify(APIResponse.success(
            data={"logs": logs, "count": len(logs)},
            request_id=request_id
        ).to_dict())
    
    except Exception as e:
        return jsonify(APIResponse.error(
            str(e),
            request_id=request_id
        ).to_dict()), 500
