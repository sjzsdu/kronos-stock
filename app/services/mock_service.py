"""
Mock数据服务 - Phase 1 功能演示版本
提供完整的虚拟数据，让网站功能完整运行
"""

from datetime import datetime, timedelta
import random
import uuid

class MockDataService:
    """Mock数据服务 - 提供演示用的虚拟数据"""
    
    @staticmethod
    def get_hot_stocks():
        """获取热门股票列表"""
        return [
            {
                'symbol': '000001',
                'name': '平安银行',
                'current_price': 12.75,
                'change_percent': 2.34,
                'volume': 1250000,
                'market_cap': '2465.8亿',
                'industry': '银行业'
            },
            {
                'symbol': '000002',
                'name': '万科A',
                'current_price': 18.90,
                'change_percent': -1.56,
                'volume': 980000,
                'market_cap': '2089.4亿',
                'industry': '房地产'
            },
            {
                'symbol': '600519',
                'name': '贵州茅台',
                'current_price': 1695.50,
                'change_percent': 0.89,
                'volume': 45000,
                'market_cap': '2.13万亿',
                'industry': '食品饮料'
            },
            {
                'symbol': '600036',
                'name': '招商银行',
                'current_price': 35.20,
                'change_percent': 1.78,
                'volume': 890000,
                'market_cap': '9876.5亿',
                'industry': '银行业'
            },
            {
                'symbol': '000858',
                'name': '五粮液',
                'current_price': 128.45,
                'change_percent': -0.67,
                'volume': 320000,
                'market_cap': '4987.6亿',
                'industry': '食品饮料'
            },
            {
                'symbol': '600031',
                'name': '三一重工',
                'current_price': 18.76,
                'change_percent': 3.45,
                'volume': 750000,
                'market_cap': '1543.2亿',
                'industry': '机械设备'
            },
            {
                'symbol': '000063',
                'name': '中兴通讯',
                'current_price': 32.18,
                'change_percent': -2.11,
                'volume': 1100000,
                'market_cap': '1876.3亿',
                'industry': '通信设备'
            }
        ]
    
    @staticmethod
    def generate_prediction(stock_symbol, stock_name, prediction_days, model_type):
        """生成模拟预测结果"""
        # 获取当前股票信息
        stocks = MockDataService.get_hot_stocks()
        current_stock = next((s for s in stocks if s['symbol'] == stock_symbol), None)
        
        if current_stock:
            current_price = current_stock['current_price']
        else:
            current_price = random.uniform(10.0, 200.0)
        
        # 模拟预测价格（根据不同模型有不同的变化范围）
        model_config = {
            'kronos-base': {
                'volatility': 0.15,
                'confidence_range': (75, 90),
                'description': '平衡型模型，综合技术面和基本面分析'
            },
            'kronos-mini': {
                'volatility': 0.08,
                'confidence_range': (60, 80),
                'description': '快速型模型，适合短期预测'
            },
            'kronos-small': {
                'volatility': 0.12,
                'confidence_range': (70, 85),
                'description': '精准型模型，深度学习算法'
            }
        }
        
        config = model_config.get(model_type, model_config['kronos-base'])
        
        # 根据预测天数调整波动性
        days_factor = min(prediction_days / 30.0, 1.0)  # 长期预测波动更大
        volatility = config['volatility'] * (0.5 + days_factor)
        
        change_factor = random.uniform(-volatility, volatility)
        predicted_price = current_price * (1 + change_factor)
        
        # 模拟置信度
        conf_min, conf_max = config['confidence_range']
        base_confidence = random.uniform(conf_min, conf_max)
        
        # 短期预测置信度稍高
        if prediction_days <= 3:
            base_confidence += random.uniform(0, 5)
        elif prediction_days >= 20:
            base_confidence -= random.uniform(0, 10)
        
        confidence = max(50, min(95, base_confidence))  # 限制在50-95之间
        
        # 生成图表数据
        chart_data = MockDataService._generate_chart_data(
            current_price, predicted_price, prediction_days
        )
        
        # 生成预测因素分析
        prediction_factors = MockDataService._generate_prediction_factors(model_type)
        
        return {
            'id': str(uuid.uuid4()),
            'stock_symbol': stock_symbol,
            'stock_name': stock_name,
            'model_type': model_type,
            'model_description': config['description'],
            'prediction_days': prediction_days,
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'confidence': round(confidence, 1),
            'prediction_change_percent': round(((predicted_price - current_price) / current_price) * 100, 2),
            'is_bullish': predicted_price > current_price,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=prediction_days)).isoformat(),
            'chart_data': chart_data,
            'prediction_factors': prediction_factors
        }
    
    @staticmethod
    def _generate_chart_data(current_price, predicted_price, days):
        """生成预测图表数据"""
        data_points = []
        
        # 历史数据点（过去7天）
        base_price = current_price
        for i in range(7, 0, -1):
            date = datetime.now() - timedelta(days=i)
            # 生成历史价格（围绕当前价格波动）
            daily_change = random.uniform(-0.03, 0.03)  # 每日3%内波动
            base_price *= (1 + daily_change)
            data_points.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(base_price, 2),
                'type': 'historical',
                'volume': random.randint(50000, 500000)
            })
        
        # 当前价格点
        data_points.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'price': current_price,
            'type': 'current',
            'volume': random.randint(100000, 800000)
        })
        
        # 预测数据点
        for i in range(1, days + 1):
            date = datetime.now() + timedelta(days=i)
            # 生成预测价格曲线（逐渐趋向预测价格）
            progress = i / days
            # 使用S曲线让变化更自然
            smooth_progress = 3 * progress**2 - 2 * progress**3
            price = current_price + (predicted_price - current_price) * smooth_progress
            
            # 添加一些随机波动
            daily_volatility = 0.02 * (1 - progress * 0.5)  # 后期波动减少
            price *= (1 + random.uniform(-daily_volatility, daily_volatility))
            
            data_points.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(price, 2),
                'type': 'predicted',
                'confidence_lower': round(price * 0.95, 2),
                'confidence_upper': round(price * 1.05, 2)
            })
        
        return data_points
    
    @staticmethod
    def _generate_prediction_factors(model_type):
        """生成预测因素分析"""
        base_factors = [
            {'name': '技术指标', 'weight': random.randint(15, 35), 'trend': random.choice(['positive', 'negative', 'neutral'])},
            {'name': '基本面分析', 'weight': random.randint(20, 40), 'trend': random.choice(['positive', 'negative', 'neutral'])},
            {'name': '市场情绪', 'weight': random.randint(10, 25), 'trend': random.choice(['positive', 'negative', 'neutral'])},
            {'name': '行业趋势', 'weight': random.randint(5, 20), 'trend': random.choice(['positive', 'negative', 'neutral'])},
            {'name': '资金流向', 'weight': random.randint(5, 15), 'trend': random.choice(['positive', 'negative', 'neutral'])}
        ]
        
        # 确保权重总和为100
        total_weight = sum(f['weight'] for f in base_factors)
        for factor in base_factors:
            factor['weight'] = round((factor['weight'] / total_weight) * 100, 1)
        
        return base_factors
    
    @staticmethod
    def get_mock_user():
        """获取模拟用户信息"""
        return {
            'id': 'demo-user',
            'email': 'demo@kronos.app',
            'display_name': '演示用户',
            'subscription_tier': 'pro',
            'is_verified': True,
            'avatar_url': None,
            'created_at': (datetime.now() - timedelta(days=30)).isoformat(),
            'usage_today': {
                'predictions': random.randint(3, 8),
                'api_calls': random.randint(15, 45)
            },
            'usage_limits': {
                'predictions': 500,
                'api_calls': 1000
            },
            'stats': {
                'total_predictions': 127,
                'successful_predictions': 89,
                'success_rate': 70.1,
                'total_earned': 15678.90,
                'best_prediction': 28.5
            }
        }
    
    @staticmethod
    def get_prediction_history(page=1, per_page=10):
        """获取模拟预测历史"""
        predictions = []
        for i in range(per_page):
            stock = random.choice(MockDataService.get_hot_stocks())
            model = random.choice(['kronos-base', 'kronos-mini', 'kronos-small'])
            days = random.choice([1, 3, 5, 10, 30])
            
            prediction = MockDataService.generate_prediction(
                stock['symbol'], stock['name'], days, model
            )
            
            # 模拟一些历史预测（已过期的）
            created_time = datetime.now() - timedelta(days=random.randint(1, 30))
            prediction['created_at'] = created_time.isoformat()
            prediction['expires_at'] = (created_time + timedelta(days=days)).isoformat()
            
            # 随机设置一些为已验证状态
            if random.random() < 0.6:  # 60%概率已验证
                prediction['status'] = 'verified'
                # 模拟实际价格
                accuracy = random.uniform(60, 95)
                prediction['actual_price'] = prediction['predicted_price'] * random.uniform(0.95, 1.05)
                prediction['accuracy'] = round(accuracy, 1)
                prediction['profit_loss'] = round(random.uniform(-500, 1200), 2)
            elif created_time + timedelta(days=days) < datetime.now():
                prediction['status'] = 'expired'
            
            predictions.append(prediction)
        
        # 按创建时间倒序排列
        predictions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            'predictions': predictions,
            'total': 127,  # 模拟总数
            'pages': 13,   # 模拟总页数
            'current_page': page,
            'has_next': page < 13,
            'has_prev': page > 1
        }

class MockStockService:
    """Mock股票数据服务"""
    
    @staticmethod
    def search_stocks(query):
        """股票搜索"""
        all_stocks = MockDataService.get_hot_stocks()
        
        # 模拟搜索逻辑
        if not query or len(query.strip()) < 1:
            return all_stocks[:5]
        
        results = []
        query = query.lower().strip()
        
        for stock in all_stocks:
            if (query in stock['symbol'].lower() or 
                query in stock['name'].lower() or
                stock['symbol'].startswith(query.upper())):
                results.append(stock)
        
        # 如果没找到完全匹配的，返回一些相似的
        if not results and len(query) >= 2:
            for stock in all_stocks:
                if any(char in stock['name'].lower() for char in query):
                    results.append(stock)
        
        return results[:8]  # 最多返回8个结果
    
    @staticmethod
    def get_stock_detail(symbol):
        """获取股票详细信息"""
        stocks = MockDataService.get_hot_stocks()
        for stock in stocks:
            if stock['symbol'] == symbol:
                # 添加更多详细信息
                stock.update({
                    'pe_ratio': round(random.uniform(8, 25), 2),
                    'pb_ratio': round(random.uniform(0.8, 3.5), 2),
                    'dividend_yield': round(random.uniform(1.5, 6.0), 2),
                    'roe': round(random.uniform(8, 25), 2),
                    'debt_ratio': round(random.uniform(20, 60), 2),
                    'recent_news': [
                        {
                            'title': '公司发布Q3财报，营收同比增长15%',
                            'time': '2小时前',
                            'impact': 'positive'
                        },
                        {
                            'title': '获得新的业务合作伙伴',
                            'time': '1天前',
                            'impact': 'positive'
                        },
                        {
                            'title': '股东大会决议通过分红方案',
                            'time': '3天前',
                            'impact': 'neutral'
                        }
                    ],
                    'analyst_rating': {
                        'buy': random.randint(5, 15),
                        'hold': random.randint(3, 10),
                        'sell': random.randint(0, 5)
                    }
                })
                return stock
        
        # 如果没找到，返回一个默认的
        return {
            'symbol': symbol,
            'name': f'股票{symbol}',
            'current_price': round(random.uniform(10, 100), 2),
            'change_percent': round(random.uniform(-5, 5), 2),
            'volume': random.randint(10000, 1000000),
            'market_cap': f'{random.randint(10, 1000)}亿',
            'industry': '未知行业'
        }

class MockMarketService:
    """Mock市场数据服务"""
    
    @staticmethod
    def get_market_overview():
        """获取市场概览"""
        return {
            'indices': [
                {
                    'name': '上证指数',
                    'code': '000001',
                    'value': 3245.67,
                    'change': 15.23,
                    'change_percent': 0.47
                },
                {
                    'name': '深证成指',
                    'code': '399001',
                    'value': 10876.54,
                    'change': -23.45,
                    'change_percent': -0.22
                },
                {
                    'name': '创业板指',
                    'code': '399006',
                    'value': 2187.89,
                    'change': 8.76,
                    'change_percent': 0.40
                }
            ],
            'market_stats': {
                'total_volume': '4567.8亿',
                'total_value': '5432.1亿',
                'up_count': 2341,
                'down_count': 1876,
                'unchanged_count': 234
            },
            'hot_sectors': [
                {'name': '新能源', 'change_percent': 3.45},
                {'name': '医药生物', 'change_percent': 2.78},
                {'name': '计算机', 'change_percent': 1.89},
                {'name': '电子', 'change_percent': -1.23},
                {'name': '房地产', 'change_percent': -2.34}
            ]
        }

# 全局实例
mock_data = MockDataService()
mock_stock = MockStockService()
mock_market = MockMarketService()