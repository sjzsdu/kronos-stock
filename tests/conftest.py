import pytest
import os
import sys
from flask import Flask

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from app.models.prediction import PredictionRecord

@pytest.fixture(scope='function')
def app():
    """Create application for the tests."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def sample_prediction_data():
    """Sample prediction data for testing."""
    return {
        'stock_code': '601688',
        'prediction_results': [
            {'date': '2025-09-25', 'close': 21.10, 'open': 21.05, 'high': 21.15, 'low': 20.98, 'volume': 1000000},
            {'date': '2025-09-26', 'close': 21.34, 'open': 21.12, 'high': 21.45, 'low': 21.08, 'volume': 1200000},
            {'date': '2025-09-27', 'close': 21.09, 'open': 21.35, 'high': 21.40, 'low': 21.05, 'volume': 980000}
        ],
        'prediction_summary': {
            'current_price': 21.10,
            'target_price': 21.09,
            'total_change_pct': -0.05
        }
    }

@pytest.fixture
def sample_prediction(app, sample_prediction_data):
    """Create a sample prediction record for testing."""
    with app.app_context():
        record = PredictionRecord(
            stock_code=sample_prediction_data['stock_code'],
            prediction_days=3,
            model_type='kronos-mini',
            status='completed',
            lookback=30,
            temperature=0.7
        )
        record.set_prediction_data(sample_prediction_data)
        
        db.session.add(record)
        db.session.commit()
        
        # Refresh the object to maintain session binding
        db.session.refresh(record)
        return record

@pytest.fixture
def failed_prediction(app):
    """Create a failed prediction record for testing."""
    with app.app_context():
        record = PredictionRecord(
            stock_code='999999',
            prediction_days=7,
            model_type='kronos-mini',
            status='failed',
            error_message='Stock not found',
            lookback=30,
            temperature=0.7
        )
        
        db.session.add(record)
        db.session.commit()
        
        # Refresh the object to maintain session binding
        db.session.refresh(record)
        return record