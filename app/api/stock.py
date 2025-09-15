from flask import jsonify, request
from . import api_bp
from app.services import stock_service

@api_bp.route('/stock/data', methods=['GET'])
def get_stock_data():
    """Get stock data for a given stock code"""
    try:
        stock_code = request.args.get('code')
        period = request.args.get('period', '1y')
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock code is required'
            }), 400
        
        # Validate stock code
        valid, validated_code = stock_service.validate_stock_code(stock_code)
        if not valid:
            return jsonify({
                'success': False,
                'error': f'Invalid stock code: {validated_code}'
            }), 400
        
        # Get stock data
        success, df, message = stock_service.get_stock_data(validated_code, period)
        
        if not success:
            return jsonify({
                'success': False,
                'error': message
            }), 400
        
        # Format data for API response
        data = []
        for i, (dt, row) in enumerate(df.iterrows()):
            if i == 0:
                change_pct = 0
                prev_close = row['close']
            else:
                prev_close = df.iloc[i-1]['close']
                change_pct = (row['close'] - prev_close) / prev_close * 100
            
            data.append({
                'date': dt.strftime('%Y-%m-%d') if hasattr(dt, 'strftime') else str(dt),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row.get('volume', 0)),
                'change_pct': float(change_pct)
            })
        
        return jsonify({
            'success': True,
            'data': {
                'stock_code': validated_code,
                'period': period,
                'data_points': len(data),
                'data': data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/info', methods=['GET'])
def get_stock_info():
    """Get basic stock information"""
    try:
        stock_code = request.args.get('code')
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock code is required'
            }), 400
        
        # Validate stock code
        valid, validated_code = stock_service.validate_stock_code(stock_code)
        if not valid:
            return jsonify({
                'success': False,
                'error': f'Invalid stock code: {validated_code}'
            }), 400
        
        # Get stock info
        info = stock_service.get_stock_info(validated_code)
        
        return jsonify({
            'success': True,
            'data': info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/stock/validate', methods=['POST'])
def validate_stock_code():
    """Validate stock code format"""
    try:
        data = request.get_json()
        stock_code = data.get('code')
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock code is required'
            }), 400
        
        valid, result = stock_service.validate_stock_code(stock_code)
        
        if valid:
            return jsonify({
                'success': True,
                'data': {
                    'valid': True,
                    'validated_code': result
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'valid': False,
                    'error': result
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500