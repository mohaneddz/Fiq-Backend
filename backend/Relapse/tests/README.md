# Relapse Service Tests

Comprehensive test suite for the Relapse prediction service covering all endpoints, features, and ML functionality.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures and configuration
├── test_routes.py           # All API endpoint tests
├── test_features.py         # Feature engineering tests
└── test_model.py            # ML model tests
```

## Running Tests

### Run All Tests
```bash
cd Relapse
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_routes.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_routes.py::TestPredictEndpoint -v
```

### Run Specific Test
```bash
pytest tests/test_features.py::TestFeatureEngineer::test_all_six_features_present -v
```

### Run with Coverage
```bash
pytest tests/ --cov=Relapse --cov-report=html
```

## Test Coverage

### Endpoints Tested (test_routes.py)
- ✅ GET `/health` - Health check
- ✅ POST `/relapse/predict` - Relapse time prediction
  - Valid data handling
  - Missing field validation
  - High-risk scenario detection
  - Trigger event integration
- ✅ POST `/relapse/features` - Feature extraction debug
- ✅ POST `/relapse/train` - Model training
- ✅ GET `/relapse/model/info` - Model metadata
- ✅ GET `/relapse/logs/tail` - Log retrieval

### Feature Engineering (test_features.py)
- ✅ All 6 features extracted:
  - `days_clean`: Days since last relapse
  - `craving_trend`: Rolling average craving score
  - `sleep_deviation`: Sleep pattern irregularity
  - `trigger_count`: Weekly trigger exposures
  - `support_sessions`: Therapy attendance
  - `medication_adherence`: Medication compliance %
- ✅ Edge case handling:
  - Empty arrays
  - Zero division protection
  - NaN handling
- ✅ Feature array conversion

### Model Functionality (test_model.py)
- ✅ Model initialization
- ✅ Training with synthetic data
- ✅ Single sample prediction
- ✅ Batch prediction
- ✅ Model persistence (save/load)
- ✅ Feature importance extraction
- ✅ Risk level classification:
  - Low (>30 days)
  - Moderate (14-30 days)
  - High (7-14 days)
  - Critical (<7 days)

## Prerequisites

### Install Test Dependencies
```bash
pip install pytest pytest-cov numpy scikit-learn xgboost
```

### Model Training
Train the model before running prediction tests:
```bash
curl -X POST http://localhost:5002/relapse/train
```

Or use the test training endpoint.

## Test Data

Tests use:
- Synthetic feature vectors (NumPy arrays)
- Mock prediction inputs with realistic values
- Edge case data (empty arrays, zeros, extremes)

## Expected Test Behavior

### Prediction Tests
- May fail if model not trained yet
- Should handle missing model gracefully
- Risk levels should match input severity

### Feature Tests
- All 6 features must be present
- Values should be numeric (no NaN)
- Calculations should match expected formulas

### Model Tests
- Training requires sufficient data
- Predictions should be positive integers
- Saved models should be loadable

## Sample Test Inputs

### Low Risk Profile
```python
{
  "days_clean": 45,
  "craving_scores": [1, 2, 1, 2, 1],
  "sleep_hours": [7.5, 8, 7, 8, 7.5],
  "trigger_events": [],
  "support_sessions": 4,
  "medication_adherence": {"doses_taken": 10, "doses_prescribed": 10}
}
```

### High Risk Profile
```python
{
  "days_clean": 5,
  "craving_scores": [8, 9, 7, 8, 9],
  "sleep_hours": [3, 4, 3, 5, 4],
  "trigger_events": [{"days_ago": 1}, {"days_ago": 2}],
  "support_sessions": 0,
  "medication_adherence": {"doses_taken": 2, "doses_prescribed": 10}
}
```

## CI/CD Integration

Add to GitHub Actions:
```yaml
- name: Run Relapse tests
  run: |
    cd backend/Relapse
    pytest tests/ -v --cov=Relapse
```

## Writing New Tests

Follow this pattern:
```python
class TestNewFeature:
    """Test description."""
    
    @pytest.fixture
    def setup_data(self):
        """Fixture for test data."""
        return np.random.rand(10, 6)
    
    def test_feature_behavior(self, model, setup_data):
        """Test specific behavior."""
        result = model.predict(setup_data)
        assert len(result) == 10
```

## Coverage Goals

- Endpoint coverage: 100%
- Feature engineering: >95%
- Model functionality: >85%
- Edge cases: >80%

## Troubleshooting

**Model not found errors:**
- Train model first using `/relapse/train` endpoint
- Check `models/` directory exists

**Feature calculation errors:**
- Verify input data has required fields
- Check for NaN or infinite values

**Prediction errors:**
- Ensure model is trained
- Verify feature count matches (6 features)
- Check input data ranges

**Import errors:**
- Ensure `sys.path` includes backend directory
- Install all required packages: `pip install -r requirements.txt`

## Performance Benchmarks

Expected performance:
- Feature extraction: <10ms
- Single prediction: <50ms
- Batch prediction (100): <200ms
- Model training: <5s

## Notes

- Tests use `np.random.seed(42)` for reproducibility
- Model metrics may vary with synthetic data
- Risk levels are approximate for testing purposes
