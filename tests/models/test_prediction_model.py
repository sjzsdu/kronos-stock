import pytest
import json
from datetime import datetime
from app.models.prediction import PredictionRecord
from app.models import db

class TestPredictionRecord:
    """Test PredictionRecord model."""
    
    def test_create_prediction_record(self, app):
        """Test creating a prediction record."""
        with app.app_context():
            record = PredictionRecord(
                stock_code='601688',
                prediction_days=7,
                model_type='kronos-mini',
                status='pending'
            )
            
            db.session.add(record)
            db.session.commit()
            
            assert record.id is not None
            assert record.stock_code == '601688'
            assert record.prediction_days == 7
            assert record.model_type == 'kronos-mini'
            assert record.status == 'pending'
            assert record.created_at is not None
    
    def test_prediction_data_serialization(self, app, sample_prediction_data):
        """Test prediction data JSON serialization."""
        with app.app_context():
            record = PredictionRecord(
                stock_code='601688',
                prediction_days=3,
                model_type='kronos-mini',
                status='completed',
                lookback=30,
                temperature=0.7
            )
            
            # Set prediction data
            record.set_prediction_data(sample_prediction_data)
            db.session.add(record)
            db.session.commit()
            
            # Retrieve and verify
            retrieved = PredictionRecord.query.get(record.id)
            prediction_data = retrieved.get_prediction_data()
            
            assert prediction_data is not None
            assert prediction_data['stock_code'] == '601688'
            assert 'prediction_results' in prediction_data
            assert len(prediction_data['prediction_results']) == 3
    
    def test_to_dict_method(self, app, sample_prediction):
        """Test the to_dict method."""
        with app.app_context():
            data = sample_prediction.to_dict()
            
            assert data['id'] == sample_prediction.id
            assert data['stock_code'] == sample_prediction.stock_code
            assert data['status'] == sample_prediction.status
            assert 'prediction_data' in data
            assert 'created_at' in data
    
    def test_prediction_record_representation(self, app):
        """Test the string representation of prediction record."""
        with app.app_context():
            record = PredictionRecord(
                stock_code='601688',
                prediction_days=7,
                model_type='kronos-mini',
                lookback=30,
                temperature=0.7
            )
            db.session.add(record)
            db.session.commit()
            
            repr_str = repr(record)
            assert '601688' in repr_str
            assert 'kronos-mini' in repr_str
    
    def test_failed_prediction_record(self, app, failed_prediction):
        """Test failed prediction record."""
        with app.app_context():
            assert failed_prediction.status == 'failed'
            assert failed_prediction.error_message == 'Stock not found'
            assert failed_prediction.prediction_data is None
            
            data = failed_prediction.to_dict()
            assert data['error_message'] == 'Stock not found'
    
    def test_query_by_status(self, app, sample_prediction, failed_prediction):
        """Test querying records by status."""
        with app.app_context():
            completed_records = PredictionRecord.query.filter_by(status='completed').all()
            failed_records = PredictionRecord.query.filter_by(status='failed').all()
            
            assert len(completed_records) >= 1
            assert len(failed_records) >= 1
            
            # Check that completed record has prediction data
            completed_record = next(r for r in completed_records if r.id == sample_prediction.id)
            assert completed_record.get_prediction_data() is not None
    
    def test_query_by_stock_code(self, app, sample_prediction):
        """Test querying records by stock code."""
        with app.app_context():
            records = PredictionRecord.query.filter_by(stock_code=sample_prediction.stock_code).all()
            
            assert len(records) >= 1
            assert any(r.id == sample_prediction.id for r in records)