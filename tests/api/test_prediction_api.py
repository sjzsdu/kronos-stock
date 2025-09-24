import pytest
import json
from app.models.prediction import PredictionRecord
from app.models import db

class TestPredictionAPI:
    """Test prediction API endpoints."""
    
    def test_get_prediction_detail_success(self, client, sample_prediction):
        """Test getting prediction detail modal HTML."""
        response = client.get(f'/api/predictions/{sample_prediction.id}')
        
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        
        # Check if HTML contains required elements
        assert 'prediction_results' in html
        assert 'loadPredictionChart' in html
        assert 'Plotly' in html
        assert sample_prediction.stock_code in html
        assert len(html) > 10000  # Ensure substantial content
    
    def test_get_prediction_detail_not_found(self, client):
        """Test getting prediction detail for non-existent record."""
        response = client.get('/api/predictions/999')
        assert response.status_code == 404
    
    def test_get_chart_data_success(self, client, sample_prediction):
        """Test getting chart data for prediction."""
        response = client.get(f'/api/predictions/{sample_prediction.id}/chart-data')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check data structure
        assert data['stock_code'] == sample_prediction.stock_code
        assert 'prediction_data' in data
        assert 'historical_data' in data
        assert 'actual_data' in data
        
        # Check prediction data
        prediction_data = data['prediction_data']
        assert len(prediction_data) == 3
        
        for item in prediction_data:
            assert 'date' in item
            assert 'predicted_price' in item
            assert isinstance(item['predicted_price'], (int, float))
    
    def test_get_chart_data_not_found(self, client):
        """Test getting chart data for non-existent record."""
        response = client.get('/api/predictions/999/chart-data')
        assert response.status_code == 404
    
    def test_get_chart_data_failed_prediction(self, client, failed_prediction):
        """Test getting chart data for failed prediction."""
        response = client.get(f'/api/predictions/{failed_prediction.id}/chart-data')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

class TestPredictionHistory:
    """Test prediction history endpoints."""
    
    def test_get_prediction_history(self, client, sample_prediction):
        """Test getting prediction history."""
        response = client.get('/api/predictions/history')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'predictions' in data
        assert len(data['predictions']) >= 1
        
        # Check first prediction structure
        first_prediction = data['predictions'][0]
        assert 'id' in first_prediction
        assert 'stock_code' in first_prediction
        assert 'status' in first_prediction
    
    def test_get_prediction_record_detail(self, client, sample_prediction):
        """Test getting specific prediction record detail."""
        response = client.get(f'/api/predictions/history/{sample_prediction.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['success'] is True
        record_data = data['data']
        
        assert record_data['id'] == sample_prediction.id
        assert record_data['stock_code'] == sample_prediction.stock_code
        assert record_data['status'] == 'completed'
        assert 'prediction_data' in record_data