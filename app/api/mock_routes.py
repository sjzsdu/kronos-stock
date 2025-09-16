"""
Mock API路由 - Phase 1 演示版本
使用Mock数据提供完整的API功能
"""

from flask import Blueprint, request, jsonify, render_template
from app.services.mock_service import mock_data, mock_stock, mock_market
import time
import random

# 创建Blueprint
mock_api = Blueprint('mock_api', __name__, url_prefix='/api')

@mock_api.route('/stocks/search')
def search_stocks():
    """股票搜索API"""
    query = request.args.get('q', '')
    results = mock_stock.search_stocks(query)
    
    # 模拟网络延迟
    time.sleep(random.uniform(0.1, 0.3))
    
    # 返回HTML片段供HTMX使用
    if request.headers.get('HX-Request'):
        if not results:
            return '<div class="no-results">未找到相关股票</div>'
        
        html = '<div class="stock-suggestions">'
        for stock in results[:5]:
            trend_class = 'text-success' if stock['change_percent'] > 0 else 'text-danger'
            html += f'''
            <div class="suggestion-item" onclick="selectStock('{stock['symbol']}', '{stock['name']}')">
                <div class="stock-basic">
                    <span class="stock-code">{stock['symbol']}</span>
                    <span class="stock-name">{stock['name']}</span>
                </div>
                <div class="stock-price">
                    <span class="price">¥{stock['current_price']}</span>
                    <span class="change {trend_class}">
                        {'+' if stock['change_percent'] > 0 else ''}{stock['change_percent']:.2f}%
                    </span>
                </div>
            </div>
            '''
        html += '</div>'
        return html
    
    return jsonify(results)

@mock_api.route('/stocks/<symbol>')
def get_stock_detail(symbol):
    """获取股票详细信息"""
    stock = mock_stock.get_stock_detail(symbol)
    
    if request.headers.get('HX-Request'):
        return render_template('components/stock_detail.html', stock=stock)
    
    return jsonify(stock)

@mock_api.route('/predictions', methods=['POST'])
def create_prediction():
    """创建预测"""
    data = request.get_json() or request.form.to_dict()
    
    # 验证必要参数
    required_fields = ['stock_symbol', 'model_type', 'prediction_days']
    for field in required_fields:
        if not data.get(field):
            if request.headers.get('HX-Request'):
                return f'<div class="alert alert-danger">参数 {field} 不能为空</div>', 400
            return jsonify({'error': f'参数 {field} 不能为空'}), 400
    
    try:
        # 获取股票信息
        stock_symbol = data['stock_symbol'].upper()
        stock_detail = mock_stock.get_stock_detail(stock_symbol)
        
        # 模拟预测计算时间
        time.sleep(random.uniform(1.0, 3.0))
        
        # 生成预测结果
        prediction = mock_data.generate_prediction(
            stock_symbol=stock_symbol,
            stock_name=stock_detail['name'],
            prediction_days=int(data['prediction_days']),
            model_type=data['model_type']
        )
        
        if request.headers.get('HX-Request'):
            return render_template('components/mock_prediction_result.html', prediction=prediction)
        
        return jsonify({
            'message': '预测创建成功',
            'prediction': prediction
        }), 201
        
    except Exception as e:
        error_msg = f'预测生成失败: {str(e)}'
        if request.headers.get('HX-Request'):
            return f'<div class="alert alert-danger">{error_msg}</div>', 500
        return jsonify({'error': error_msg}), 500

@mock_api.route('/predictions')
def get_predictions():
    """获取预测历史"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    result = mock_data.get_prediction_history(page=page, per_page=per_page)
    
    if request.headers.get('HX-Request'):
        return render_template('components/prediction_history.html', **result)
    
    return jsonify(result)

@mock_api.route('/users/profile')
def get_user_profile():
    """获取用户资料"""
    user = mock_data.get_mock_user()
    
    if request.headers.get('HX-Request'):
        return render_template('components/user_profile.html', user=user)
    
    return jsonify(user)

@mock_api.route('/users/usage')
def get_user_usage():
    """获取用户使用情况"""
    user = mock_data.get_mock_user()
    usage_data = {
        'usage_today': user['usage_today'],
        'usage_limits': user['usage_limits'],
        'usage_percentage': {
            'predictions': round((user['usage_today']['predictions'] / user['usage_limits']['predictions']) * 100, 1),
            'api_calls': round((user['usage_today']['api_calls'] / user['usage_limits']['api_calls']) * 100, 1)
        }
    }
    
    if request.headers.get('HX-Request'):
        return render_template('components/usage_stats.html', **usage_data)
    
    return jsonify(usage_data)

@mock_api.route('/market/overview')
def get_market_overview():
    """获取市场概览"""
    market_data = mock_market.get_market_overview()
    
    if request.headers.get('HX-Request'):
        return render_template('components/market_overview.html', **market_data)
    
    return jsonify(market_data)

@mock_api.route('/market/hot-stocks')
def get_hot_stocks():
    """获取热门股票"""
    hot_stocks = mock_data.get_hot_stocks()
    
    if request.headers.get('HX-Request'):
        return render_template('components/hot_stocks.html', stocks=hot_stocks)
    
    return jsonify(hot_stocks)

@mock_api.route('/predictions/<prediction_id>/chart')
def get_prediction_chart(prediction_id):
    """获取预测图表数据"""
    # 模拟根据ID获取预测数据
    # 实际中会从数据库获取
    stock = random.choice(mock_data.get_hot_stocks())
    model = random.choice(['kronos-base', 'kronos-mini', 'kronos-small'])
    
    prediction = mock_data.generate_prediction(
        stock['symbol'], stock['name'], 5, model
    )
    
    chart_data = prediction['chart_data']
    
    if request.headers.get('HX-Request'):
        return render_template('components/prediction_chart.html', 
                             chart_data=chart_data, 
                             prediction_id=prediction_id)
    
    return jsonify(chart_data)

# 错误处理
@mock_api.errorhandler(404)
def not_found(error):
    if request.headers.get('HX-Request'):
        return '<div class="alert alert-warning">请求的资源未找到</div>', 404
    return jsonify({'error': '请求的资源未找到'}), 404

@mock_api.errorhandler(500)
def internal_error(error):
    if request.headers.get('HX-Request'):
        return '<div class="alert alert-danger">服务器内部错误，请稍后重试</div>', 500
    return jsonify({'error': '服务器内部错误'}), 500