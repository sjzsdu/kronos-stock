from flask import Blueprint, jsonify, request
from app.utils.exceptions import UIServiceError, ValidationError, NotFoundError
from datetime import datetime
import traceback

# Create API blueprint
api_bp = Blueprint('api', __name__)

# Import existing API routes
from . import model
from . import stock
from . import prediction
from . import market

# Import user system API routes
from . import auth
from . import user

# Import UI enhancement API routes
from . import ui_components
from . import user_preferences
from . import performance
from . import usage_tracking


# Error handlers should be defined before blueprint registration
@api_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """处理验证错误"""
    return jsonify({
        'success': False,
        'error': str(error),
        'error_type': 'ValidationError',
        'timestamp': datetime.now().isoformat()
    }), 400

@api_bp.errorhandler(NotFoundError)
def handle_not_found_error(error):
    """处理未找到错误"""
    return jsonify({
        'success': False,
        'error': str(error),
        'error_type': 'NotFoundError',
        'timestamp': datetime.now().isoformat()
    }), 404

@api_bp.errorhandler(UIServiceError)
def handle_ui_service_error(error):
    """处理UI服务错误"""
    return jsonify({
        'success': False,
        'error': str(error),
        'error_type': 'UIServiceError',
        'timestamp': datetime.now().isoformat()
    }), 409

@api_bp.errorhandler(Exception)
def handle_general_error(error):
    """处理通用错误"""
    error_detail = {
        'success': False,
        'error': '服务器内部错误',
        'error_type': 'InternalError',
        'timestamp': datetime.now().isoformat()
    }
    
    # 在开发环境中提供详细错误信息
    try:
        from flask import current_app
        if current_app.debug:
            error_detail['debug_info'] = {
                'message': str(error),
                'traceback': traceback.format_exc()
            }
    except:
        pass
    
    return jsonify(error_detail), 500

@api_bp.before_request
def log_request_info():
    """记录请求信息"""
    # 这里可以添加请求日志记录逻辑
    pass

@api_bp.after_request
def after_request(response):
    """请求后处理"""
    # 添加CORS头部
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    
    # 添加API版本头部
    response.headers.add('X-API-Version', '1.0.0')
    
    return response