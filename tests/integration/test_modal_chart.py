import pytest
import json

def test_modal_and_chart(app, sample_prediction):
    """Test both the modal rendering and chart data API"""
    with app.app_context():
        client = app.test_client()
        
        # Test prediction detail modal endpoint
        modal_response = client.get(f'/prediction/detail/{sample_prediction.id}')
        assert modal_response.status_code == 200
        
        html_content = modal_response.get_data(as_text=True)
        
        # Check if the modal contains expected elements
        assert 'predictionChart' in html_content
        assert sample_prediction.stock_code in html_content
        
        # Test chart data API endpoint
        chart_response = client.get(f'/api/prediction/{sample_prediction.id}/chart')
        assert chart_response.status_code == 200
        
        chart_data = chart_response.get_json()
        assert isinstance(chart_data, dict)
        assert 'prediction_results' in chart_data
        assert 'stock_code' in chart_data
        assert chart_data['stock_code'] == sample_prediction.stock_code
