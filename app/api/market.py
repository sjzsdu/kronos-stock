"""
Market data API endpoints
"""

from flask import Blueprint, request, jsonify
from app.services.market_data_service import market_data_service
import logging

logger = logging.getLogger(__name__)

market_api = Blueprint('market_api', __name__)

@market_api.route('/market/top-list')
def get_top_list():
    """Get dragon tiger list data"""
    try:
        # Get query parameters
        date = request.args.get('date')
        exchange = request.args.get('exchange')
        
        # Get data from service
        result = market_data_service.get_top_list_data(date=date, exchange=exchange)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'message': result['message']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['message']
            }), 500
            
    except Exception as e:
        logger.error(f"Error in get_top_list API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@market_api.route('/market/margin')
def get_margin_data():
    """Get margin trading data"""
    try:
        date = request.args.get('date')
        exchange = request.args.get('exchange')
        
        result = market_data_service.get_margin_data(date=date, exchange=exchange)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'message': result.get('message', 'Data retrieved successfully')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', result.get('message', 'Unknown error'))
            }), 400
            
    except Exception as e:
        logger.error(f"Error in get_margin_data API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500

@market_api.route('/market/northbound')
def get_northbound_data():
    """Get northbound funds data"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        result = market_data_service.get_northbound_data(start_date=start_date, end_date=end_date)
        
        if result['success']:
            return jsonify({
                'success': True,
                'data': result['data'],
                'message': result.get('message', 'Data retrieved successfully')
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', result.get('message', 'Unknown error'))
            }), 400
            
    except Exception as e:
        logger.error(f"Error in get_northbound_data API: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500