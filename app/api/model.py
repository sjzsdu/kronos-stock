from flask import jsonify, request
from . import api_bp
from app.services import model_service

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Basic health check - ensure the service is running
        return jsonify({
            'status': 'healthy',
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'service': 'kronos-stock-prediction'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Get available models"""
    try:
        status = model_service.get_model_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/models/load', methods=['POST'])
def load_model():
    """Load a specific model"""
    try:
        data = request.get_json()
        model_name = data.get('model_name')
        
        if not model_name:
            return jsonify({
                'success': False,
                'error': 'model_name is required'
            }), 400
        
        success, message = model_service.load_model(model_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'model_name': model_name
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/models/status', methods=['GET']) 
def get_model_status():
    """Get current model status"""
    try:
        status = model_service.get_model_status()
        return jsonify({
            'success': True,
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api_bp.route('/models/unload', methods=['POST'])
def unload_model():
    """Unload current model"""
    try:
        model_service.unload_model()
        return jsonify({
            'success': True,
            'message': 'Model unloaded successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500