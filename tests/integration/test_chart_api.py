import pytest
import json

def test_chart_data_api(app, sample_prediction):
    """Test the chart data API for a specific prediction record"""
    with app.app_context():
        client = app.test_client()
        
        # Test chart data API endpoint
        chart_response = client.get(f'/api/prediction/{sample_prediction.id}/chart')
        
        assert chart_response.status_code == 200
        
        chart_data = chart_response.get_json()
        assert isinstance(chart_data, dict)
        assert 'prediction_results' in chart_data
        assert 'stock_code' in chart_data
        assert chart_data['stock_code'] == sample_prediction.stock_code
        
        # Test prediction detail modal endpoint
        modal_response = client.get(f'/prediction/detail/{sample_prediction.id}')
        assert modal_response.status_code == 200
        
        html_content = modal_response.get_data(as_text=True)
        assert 'predictionChart' in html_content
