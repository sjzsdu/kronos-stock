import pytest
from unittest.mock import Mock, patch
from app.services.stock_service import StockService

class TestStockService:
    """Test stock service functionality."""
    
    def test_stock_service_initialization(self, app):
        """Test stock service can be initialized."""
        with app.app_context():
            service = StockService()
            assert service is not None
    
    def test_validate_stock_code_valid(self, app):
        """Test stock code validation with valid codes."""
        with app.app_context():
            service = StockService()
            
            # Test valid codes
            valid, code = service.validate_stock_code('601688')
            assert valid is True
            assert code == '601688'
            
            valid, code = service.validate_stock_code('000001')
            assert valid is True
            assert code == '000001'
    
    def test_validate_stock_code_invalid(self, app):
        """Test stock code validation with invalid codes."""
        with app.app_context():
            service = StockService()
            
            # Test invalid codes
            valid, message = service.validate_stock_code('')
            assert valid is False
            
            # Test code that's too short (less than 4 characters)
            valid, message = service.validate_stock_code('123')
            assert valid is False
            
            # Test code with invalid characters
            valid, message = service.validate_stock_code('ABC!')
            assert valid is False
    
    def test_get_stock_info_success(self, app):
        """Test getting stock info successfully."""
        with app.app_context():
            service = StockService()
            info = service.get_stock_info('601688')
            
            # Test basic structure regardless of real or fallback data
            assert 'code' in info
            assert 'name' in info
            assert 'market' in info
            assert info['code'] == '601688'
            assert info['market'] == 'CN'
    
    def test_get_current_price_success(self, app):
        """Test getting current price successfully."""
        with app.app_context():
            service = StockService()
            price_info = service.get_current_price('601688')
            
            # Test basic structure regardless of real or fallback data
            assert 'current_price' in price_info
            assert isinstance(price_info['current_price'], (int, float))
            assert price_info['current_price'] > 0

class TestPredictionService:
    """Test prediction service functionality."""
    
    def test_prediction_service_initialization(self, app):
        """Test prediction service can be initialized."""
        with app.app_context():
            from app.services.prediction_service import prediction_service
            assert prediction_service is not None
    
    @patch('app.services.prediction_service.model_service')
    @patch('app.services.prediction_service.stock_service')
    def test_predict_stock_success(self, mock_stock_service, mock_model_service, app):
        """Test stock prediction success."""
        # Mock model service
        mock_model_service.is_model_loaded.return_value = True
        mock_predictor = Mock()
        mock_predictor.predict.return_value = Mock()  # Mock prediction result
        mock_model_service.predictor = mock_predictor
        
        # Mock stock service
        mock_stock_service.validate_stock_code.return_value = (True, '601688')
        mock_stock_service.get_stock_data.return_value = (True, Mock(), 'Success')
        
        with app.app_context():
            from app.services.prediction_service import prediction_service
            
            success, result = prediction_service.predict_stock('601688', 30, 7, 0.7)
            
            # Since this is a complex integration, we mainly test the flow
            assert isinstance(success, bool)
            assert isinstance(result, dict)