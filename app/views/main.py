from flask import render_template, jsonify
from . import views_bp
from app.services import model_service
from datetime import datetime, timedelta
import random

@views_bp.route('/')
def index():
    """Modern main page with enhanced UI"""
    model_status = model_service.get_model_status()
    return render_template('pages/modern_index.html', model_status=model_status)

@views_bp.route('/modern')
def modern_index():
    """Modern index page"""
    model_status = model_service.get_model_status()
    return render_template('pages/modern_index.html', model_status=model_status)

@views_bp.route('/dashboard')
def dashboard():
    """Advanced dashboard page"""
    model_status = model_service.get_model_status()
    return render_template('pages/dashboard.html', model_status=model_status)

@views_bp.route('/community')
def community():
    """Investment community page"""
    model_status = model_service.get_model_status()
    return render_template('pages/community.html', model_status=model_status)

@views_bp.route('/learning')
def learning():
    """Learning center page"""
    model_status = model_service.get_model_status()
    return render_template('pages/learning.html', model_status=model_status)

@views_bp.route('/stock-search')
def stock_search():
    """Stock search page"""
    model_status = model_service.get_model_status()
    return render_template('pages/stock_search.html', model_status=model_status)

@views_bp.route('/monitoring')
def monitoring():
    """Stock monitoring page"""
    model_status = model_service.get_model_status()
    return render_template('pages/monitoring.html', model_status=model_status)

@views_bp.route('/prediction')
def prediction():
    """AI prediction page"""
    model_status = model_service.get_model_status()
    return render_template('pages/prediction.html', model_status=model_status)

@views_bp.route('/portfolio')
def portfolio():
    """Investment portfolio page"""
    model_status = model_service.get_model_status()
    return render_template('pages/portfolio.html', model_status=model_status)

@views_bp.route('/history')
def history():
    """Prediction history page"""
    model_status = model_service.get_model_status()
    return render_template('pages/history.html', model_status=model_status)

@views_bp.route('/watchlist')
def watchlist():
    """User watchlist page"""
    model_status = model_service.get_model_status()
    return render_template('pages/watchlist.html', model_status=model_status)

@views_bp.route('/alerts')
def alerts():
    """Price alerts page"""
    model_status = model_service.get_model_status()
    return render_template('pages/alerts.html', model_status=model_status)

@views_bp.route('/model-comparison')
def model_comparison():
    """AI model comparison page"""
    model_status = model_service.get_model_status()
    return render_template('pages/model_comparison.html', model_status=model_status)

@views_bp.route('/technical-analysis')
def technical_analysis():
    """Technical analysis page"""
    model_status = model_service.get_model_status()
    return render_template('pages/technical_analysis.html', model_status=model_status)

@views_bp.route('/market-news')
def market_news():
    """Market news page"""
    model_status = model_service.get_model_status()
    return render_template('pages/market_news.html', model_status=model_status)

@views_bp.route('/profile')
def profile():
    """User profile page"""
    model_status = model_service.get_model_status()
    return render_template('pages/profile.html', model_status=model_status)

@views_bp.route('/subscription')
def subscription():
    """Subscription management page"""
    model_status = model_service.get_model_status()
    return render_template('pages/subscription.html', model_status=model_status)

@views_bp.route('/settings')
def settings():
    """System settings page"""
    model_status = model_service.get_model_status()
    return render_template('pages/settings.html', model_status=model_status)

@views_bp.route('/test')
def test():
    """System test page"""
    return render_template('pages/test.html')

@views_bp.route('/menu-test')
def menu_test():
    """Menu system test page"""
    return render_template('pages/menu_test.html')

# Component routes for HTMX
@views_bp.route('/components/market-news')
def market_news_component():
    """Market news component for HTMX"""
    # Mock market news data
    news_items = [
        {
            "id": 1,
            "title": "A股三大指数集体上涨，新能源板块领涨",
            "summary": "今日A股市场表现强劲，上证指数涨1.2%，深证成指涨0.8%，创业板指涨1.5%。新能源汽车、光伏等板块领涨。",
            "content": "今日A股三大指数集体上涨，市场情绪回暖。新能源板块表现突出，比亚迪涨幅超过3%，宁德时代、隆基绿能等个股均有不错表现。分析师认为，随着政策利好不断释放，新能源行业有望迎来新一轮上涨周期。",
            "source": "财经日报",
            "published_at": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
            "category": "市场动态",
            "impact": "positive",
            "tags": ["A股", "新能源", "上涨"]
        },
        {
            "id": 2,
            "title": "央行宣布降准0.25个百分点，释放流动性约5000亿元",
            "summary": "中国人民银行决定于近期下调金融机构存款准备金率0.25个百分点，预计释放长期流动性约5000亿元。",
            "content": "为了保持流动性合理充裕，支持实体经济发展，中国人民银行决定下调金融机构存款准备金率0.25个百分点。此次降准将释放长期流动性约5000亿元，有助于降低银行资金成本，促进银行加大对实体经济的支持力度。",
            "source": "央行公告",
            "published_at": (datetime.now() - timedelta(hours=4)).strftime('%Y-%m-%d %H:%M'),
            "category": "货币政策",
            "impact": "positive",
            "tags": ["央行", "降准", "流动性"]
        },
        {
            "id": 3,
            "title": "美联储官员暗示可能暂停加息，全球股市普涨",
            "summary": "美联储官员在最新讲话中暗示可能暂停加息步伐，市场对此反应积极，全球主要股指均收涨。",
            "content": "美联储多位官员近期表态暗示加息周期可能接近尾声，市场对此反应积极。美股三大指数收涨，欧洲股市也普遍上涨。投资者认为，美联储政策立场的转变将有利于风险资产表现，新兴市场也有望受益。",
            "source": "路透社",
            "published_at": (datetime.now() - timedelta(hours=6)).strftime('%Y-%m-%d %H:%M'),
            "category": "国际市场",
            "impact": "positive",
            "tags": ["美联储", "加息", "全球股市"]
        },
        {
            "id": 4,
            "title": "科技股财报季来临，投资者关注AI概念股表现",
            "summary": "随着财报季到来，投资者将重点关注科技公司业绩，特别是AI相关业务的发展情况。",
            "content": "本周将迎来科技股密集发布财报的时期，投资者特别关注人工智能相关业务的发展情况。分析师预计，AI技术的快速发展将为科技公司带来新的增长机遇。相关概念股有望在财报发布后迎来新一轮估值重构。",
            "source": "科技财经",
            "published_at": (datetime.now() - timedelta(hours=8)).strftime('%Y-%m-%d %H:%M'),
            "category": "科技股",
            "impact": "neutral",
            "tags": ["科技股", "财报", "AI概念"]
        },
        {
            "id": 5,
            "title": "房地产板块分化明显，一线城市成交量回升",
            "summary": "房地产市场出现分化，一线城市成交量有所回升，但三四线城市仍面临调整压力。",
            "content": "近期房地产市场呈现明显分化态势。一线城市在政策支持下成交量有所回升，但价格仍相对平稳。而三四线城市则继续面临去库存压力。分析师认为，房地产行业正在经历结构性调整，优质房企有望在行业整合中获得更多机会。",
            "source": "地产周刊",
            "published_at": (datetime.now() - timedelta(hours=10)).strftime('%Y-%m-%d %H:%M'),
            "category": "房地产",
            "impact": "neutral",
            "tags": ["房地产", "分化", "一线城市"]
        }
    ]
    
    # Select random news items to simulate dynamic content
    selected_news = random.sample(news_items, min(len(news_items), random.randint(3, 5)))
    
    # Sort by published date (newest first)
    selected_news.sort(key=lambda x: x['published_at'], reverse=True)
    
    data = {
        "news": selected_news,
        "total": len(selected_news),
        "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M')
    }
    
    return render_template('components/market_news.html', data=data)

@views_bp.route('/components/alerts')
def alerts_component():
    """Alerts component for HTMX"""
    # Import alerts API function to get data
    from app.api.alerts import get_alerts
    
    # Get alerts data from API
    response = get_alerts()
    api_data = response.get_json()
    
    if api_data.get('success'):
        data = api_data.get('data')
        return render_template('components/alerts_list.html', data=data)
    else:
        return render_template('components/alerts_list.html', data=None)