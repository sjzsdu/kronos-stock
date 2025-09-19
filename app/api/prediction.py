from flask import Blueprint, request, jsonify
from app.services import model_service
from app.services.prediction_service import prediction_service

prediction_api = Blueprint('prediction_api', __name__)

@prediction_api.route('/predict', methods=['POST'])
def predict():
    """Predict stock prices"""
    try:
        data = request.get_json()
        
        # Extract parameters from frontend form
        stock_code = data.get('stock_code')
        prediction_days = data.get('prediction_days', 7)  # Frontend parameter
        model_type = data.get('model_type', 'kronos-base')  # Frontend parameter
        
        # Map to backend parameters
        lookback = 30  # Default lookback period
        pred_len = int(prediction_days)  # Map prediction_days to pred_len
        temperature = 0.7  # Default temperature
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock_code is required'
            }), 400
        
        # Validate parameters
        try:
            pred_len = int(pred_len)
            temperature = float(temperature)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid parameter types'
            }), 400
        
        if not (1 <= pred_len <= 30):
            return jsonify({
                'success': False,
                'error': 'prediction_days must be between 1 and 30 days'
            }), 400
        
        if not (0.1 <= temperature <= 2.0):
            return jsonify({
                'success': False,
                'error': 'temperature must be between 0.1 and 2.0'
            }), 400
        
        # Make prediction
        success, result = prediction_service.predict_stock(stock_code, lookback, pred_len, temperature)
        
        if success:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Prediction failed')
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prediction_api.route('/notifications/check', methods=['GET'])
def check_notifications():
    return jsonify({
        'success': True,
        'notifications': []
    })

@prediction_api.route('/model/load', methods=['POST'])
def load_model():
    """Load a specific model"""
    try:
        data = request.get_json()
        model_name = data.get('model_name', 'kronos-mini')
        
        success, message = model_service.load_model(model_name)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prediction_api.route('/model/status', methods=['GET'])
def model_status():
    """Get current model status"""
    try:
        status = model_service.get_model_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500