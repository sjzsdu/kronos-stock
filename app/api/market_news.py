from flask import jsonify
from . import api_bp
from datetime import datetime, timedelta
import random

@api_bp.route('/market-news')
def get_market_news():
    """Get market news data"""
    # Mock market news data for now
    # In a real application, this would fetch from a news API
    
    news_items = [
        {
            "id": 1,
            "title": "A股三大指数集体上涨，新能源板块领涨",
            "summary": "今日A股市场表现强劲，上证指数涨1.2%，深证成指涨0.8%，创业板指涨1.5%。新能源汽车、光伏等板块领涨。",
            "content": "今日A股三大指数集体上涨，市场情绪回暖。新能源板块表现突出，比亚迪涨幅超过3%，宁德时代、隆基绿能等个股均有不错表现。分析师认为，随着政策利好不断释放，新能源行业有望迎来新一轮上涨周期。",
            "source": "财经日报",
            "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
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
            "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
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
            "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
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
            "published_at": (datetime.now() - timedelta(hours=8)).isoformat(),
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
            "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
            "category": "房地产",
            "impact": "neutral",
            "tags": ["房地产", "分化", "一线城市"]
        }
    ]
    
    # Add some randomness to make it feel more real
    selected_news = random.sample(news_items, min(len(news_items), random.randint(3, 5)))
    
    # Sort by published date (newest first)
    selected_news.sort(key=lambda x: x['published_at'], reverse=True)
    
    return jsonify({
        "success": True,
        "data": {
            "news": selected_news,
            "total": len(selected_news),
            "updated_at": datetime.now().isoformat()
        }
    })

@api_bp.route('/market-news/<int:news_id>')
def get_news_detail(news_id):
    """Get detailed news information"""
    # Mock detailed news data
    news_detail = {
        "id": news_id,
        "title": "详细新闻标题",
        "content": "这里是详细的新闻内容...",
        "source": "财经日报",
        "published_at": datetime.now().isoformat(),
        "category": "市场动态",
        "impact": "positive",
        "tags": ["股市", "新闻"],
        "related_stocks": [
            {"code": "000001", "name": "平安银行", "change": "+1.2%"},
            {"code": "000002", "name": "万科A", "change": "-0.5%"}
        ]
    }
    
    return jsonify({
        "success": True,
        "data": news_detail
    })