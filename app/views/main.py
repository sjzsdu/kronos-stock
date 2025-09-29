from flask import render_template, jsonify, redirect, url_for
from . import views_bp
from app.services import model_service
from app.services.market_data_service import MarketDataService
from datetime import datetime, timedelta
import random

# Initialize market data service
market_service = MarketDataService()

@views_bp.route('/')
def index():
    """Index page"""
    return render_template('pages/index.html')

@views_bp.route('/prediction')
def prediction():
    """AI prediction page"""
    model_status = model_service.get_model_status()
    return render_template('pages/prediction.html', model_status=model_status)

@views_bp.route('/history')
def history():
    """Prediction history page"""
    model_status = model_service.get_model_status()
    return render_template('pages/history.html', model_status=model_status)

# Market data routes
@views_bp.route('/market/top-list')
def market_top_list():
    """Dragon Tiger List - Large transaction details"""
    return render_template('pages/market/top_list.html', page_title='龙虎榜数据', page_description='大额交易明细')

@views_bp.route('/market/margin')
def market_margin():
    """Margin trading data - Margin balance statistics"""
    return render_template('pages/market/margin.html', page_title='融资融券数据', page_description='融资融券余额统计')

@views_bp.route('/market/northbound')
def market_northbound():
    """Northbound funds data - Foreign capital holdings"""
    return render_template('pages/market/northbound.html', page_title='北向资金数据', page_description='外资持股情况')

@views_bp.route('/market/sse')
def market_sse():
    """Shanghai Stock Exchange data - Market statistics"""
    return render_template('pages/market/sse.html', page_title='上交所数据', page_description='上海证券交易所市场统计')

@views_bp.route('/market/szse')
def market_szse():
    """Shenzhen Stock Exchange data - Market statistics"""
    return render_template('pages/market/szse.html', page_title='深交所数据', page_description='深圳证券交易所市场统计')

@views_bp.route('/market/region-data')
def market_region_data():
    """Region trading data page"""
    return render_template('pages/market/region.html', 
                         page_title='地区成交数据',
                         page_description='按地区分类的交易统计')

# HTMX endpoints for partial HTML rendering
@views_bp.route('/htmx/market/top-list')
def htmx_top_list():
    """HTMX endpoint for top list data"""
    from flask import request
    from app.services.market_data_service import market_data_service
    
    # Get query parameters
    date = request.args.get('date')
    exchange = request.args.get('exchange')
    
    # Get data from service
    result = market_data_service.get_top_list_data(date=date, exchange=exchange)
    
    if result['success']:
        return render_template('components/market/top_list_table.html', 
                             data=result['data'])
    else:
        return render_template('components/market/error.html', 
                             error=result.get('error', result.get('message', 'Unknown error')))

@views_bp.route('/htmx/market/margin')
def htmx_margin():
    """HTMX endpoint for margin data"""
    from flask import request
    from app.services.market_data_service import market_data_service
    
    # Get query parameters
    date = request.args.get('date')
    exchange = request.args.get('exchange')
    
    # Get data from service
    result = market_data_service.get_margin_data(date=date, exchange=exchange)
    
    if result['success']:
        return render_template('components/market/margin_wrapper.html', 
                             data=result['data'])
    else:
        return render_template('components/market/error.html', 
                             error=result.get('error', result.get('message', 'Unknown error')))

@views_bp.route('/htmx/market/northbound')
def htmx_market_northbound():
    """HTMX endpoint for northbound data"""
    try:
        data = market_service.get_northbound_data()
        if data and data.get('success'):
            return render_template('components/market/northbound_wrapper.html', 
                                   data=data.get('data', {}))
        else:
            error_msg = data.get('error', 'No northbound data available') if data else 'Data service unavailable'
            return render_template('components/market/error.html', 
                                   message=error_msg)
    except Exception as e:
        return render_template('components/market/error.html', 
                               message=f'Error loading northbound data: {str(e)}')

@views_bp.route('/htmx/market/sse')
def htmx_market_sse():
    """HTMX endpoint for SSE market data"""
    try:
        data = market_service.get_sse_data()
        if data and data.get('success'):
            return render_template('components/market/sse_wrapper.html', 
                                   data=data.get('data', {}))
        else:
            error_msg = data.get('error', 'No SSE data available') if data else 'Data service unavailable'
            return render_template('components/market/error.html', 
                                   message=error_msg)
    except Exception as e:
        return render_template('components/market/error.html', 
                               message=f'Error loading SSE data: {str(e)}')

@views_bp.route('/htmx/market/szse')
def htmx_market_szse():
    """HTMX endpoint for SZSE market data"""
    try:
        data = market_service.get_szse_data()
        if data and data.get('success'):
            return render_template('components/market/szse_wrapper.html', 
                                   data=data.get('data', {}))
        else:
            error_msg = data.get('error', 'No SZSE data available') if data else 'Data service unavailable'
            return render_template('components/market/error.html', 
                                   message=error_msg)
    except Exception as e:
        return render_template('components/market/error.html', 
                               message=f'Error loading SZSE data: {str(e)}')

@views_bp.route('/market/industry')
def market_industry():
    """Industry trading data - Statistics by industry"""
    return render_template('pages/market/industry.html', page_title='行业成交数据', page_description='按行业分类的交易统计')
