from flask import jsonify, request
from . import api_bp
from app.services import prediction_service

@api_bp.route('/predict', methods=['POST'])
def predict_stock():
    """Predict stock prices"""
    try:
        data = request.get_json()
        
        # Extract parameters
        stock_code = data.get('stock_code')
        lookback = data.get('lookback', 30)
        pred_len = data.get('pred_len', 5)
        temperature = data.get('temperature', 0.7)
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock_code is required'
            }), 400
        
        # Validate parameters
        try:
            lookback = int(lookback)
            pred_len = int(pred_len)
            temperature = float(temperature)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid parameter types'
            }), 400
        
        if not (1 <= lookback <= 252):
            return jsonify({
                'success': False,
                'error': 'lookback must be between 1 and 252 days'
            }), 400
        
        if not (1 <= pred_len <= 30):
            return jsonify({
                'success': False,
                'error': 'pred_len must be between 1 and 30 days'
            }), 400
        
        if not (0.1 <= temperature <= 2.0):
            return jsonify({
                'success': False,
                'error': 'temperature must be between 0.1 and 2.0'
            }), 400
        
        # Make prediction
        success, result = prediction_service.predict_stock(
            stock_code, lookback, pred_len, temperature
        )
        
        if success:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown prediction error')
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/predict/batch', methods=['POST'])
def predict_multiple_stocks():
    """Predict multiple stocks in batch"""
    try:
        data = request.get_json()
        
        stock_codes = data.get('stock_codes', [])
        lookback = data.get('lookback', 30)
        pred_len = data.get('pred_len', 5)
        temperature = data.get('temperature', 0.7)
        
        if not stock_codes or not isinstance(stock_codes, list):
            return jsonify({
                'success': False,
                'error': 'stock_codes must be a non-empty list'
            }), 400
        
        if len(stock_codes) > 10:  # Limit batch size
            return jsonify({
                'success': False,
                'error': 'Maximum 10 stocks allowed per batch'
            }), 400
        
        results = []
        for stock_code in stock_codes:
            success, result = prediction_service.predict_stock(
                stock_code, lookback, pred_len, temperature
            )
            
            if success:
                results.append({
                    'stock_code': stock_code,
                    'success': True,
                    'data': result
                })
            else:
                results.append({
                    'stock_code': stock_code,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                })
        
        return jsonify({
            'success': True,
            'data': {
                'batch_results': results,
                'total_processed': len(results),
                'successful': len([r for r in results if r['success']]),
                'failed': len([r for r in results if not r['success']])
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500