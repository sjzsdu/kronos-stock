# Kronos 智能投资平台 - 技术实现指南

## 🎯 架构实现路线图（功能优先策略）

### Phase 1: 核心功能演示版本 (当前阶段)
- [x] Flask应用基础架构
- [x] HTMX前端框架集成
- [x] 现代化UI/UX设计
- [x] 数据库结构完整设计
- [ ] **核心功能Mock版本** - 使用虚拟数据展示完整功能流程
- [ ] **AI模型集成对接** - 将现有模型与前端界面连通
- [ ] **数据可视化增强** - 完善预测结果的图表展示

### Phase 2: 用户系统与数据持久化
- [ ] 用户认证系统 (注册/登录)
- [ ] 用户数据持久化
- [ ] 预测历史记录管理
- [ ] 个人中心功能

### Phase 3: 商业化功能
- [ ] 计费与订阅系统
- [ ] 支付系统集成
- [ ] 使用限制管理
- [ ] 会员权益系统

### Phase 4: 高级功能与优化
- [ ] 社区功能开发
- [ ] 实时监控预警
- [ ] 移动端适配
- [ ] 性能优化与生产部署

## 🚀 Phase 1 详细实现计划（功能优先）

### 目标：让整个网站完整跑起来，展示所有核心功能

#### 1.1 创建Mock数据服务
首先建立一个Mock数据层，模拟所有真实数据：

```python
# app/services/mock_service.py
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
                'market_cap': '2465.8亿'
            },
            {
                'symbol': '000002',
                'name': '万科A',
                'current_price': 18.90,
                'change_percent': -1.56,
                'volume': 980000,
                'market_cap': '2089.4亿'
            },
            {
                'symbol': '600519',
                'name': '贵州茅台',
                'current_price': 1695.50,
                'change_percent': 0.89,
                'volume': 45000,
                'market_cap': '2.13万亿'
            },
            {
                'symbol': '600036',
                'name': '招商银行',
                'current_price': 35.20,
                'change_percent': 1.78,
                'volume': 890000,
                'market_cap': '9876.5亿'
            },
            {
                'symbol': '000858',
                'name': '五粮液',
                'current_price': 128.45,
                'change_percent': -0.67,
                'volume': 320000,
                'market_cap': '4987.6亿'
            }
        ]
    
    @staticmethod
    def generate_prediction(stock_symbol, stock_name, prediction_days, model_type):
        """生成模拟预测结果"""
        # 模拟当前价格
        current_price = random.uniform(10.0, 200.0)
        
        # 模拟预测价格（根据不同模型有不同的变化范围）
        model_volatility = {
            'kronos-base': 0.15,    # 15%波动
            'kronos-mini': 0.08,    # 8%波动  
            'kronos-small': 0.12    # 12%波动
        }
        
        volatility = model_volatility.get(model_type, 0.10)
        change_factor = random.uniform(-volatility, volatility)
        predicted_price = current_price * (1 + change_factor)
        
        # 模拟置信度（不同模型有不同的置信度范围）
        confidence_range = {
            'kronos-base': (75, 90),
            'kronos-mini': (60, 80),
            'kronos-small': (70, 85)
        }
        
        conf_min, conf_max = confidence_range.get(model_type, (65, 85))
        confidence = random.uniform(conf_min, conf_max)
        
        # 生成图表数据
        chart_data = MockDataService._generate_chart_data(
            current_price, predicted_price, prediction_days
        )
        
        return {
            'id': str(uuid.uuid4()),
            'stock_symbol': stock_symbol,
            'stock_name': stock_name,
            'model_type': model_type,
            'prediction_days': prediction_days,
            'current_price': round(current_price, 2),
            'predicted_price': round(predicted_price, 2),
            'confidence': round(confidence, 1),
            'prediction_change_percent': round(((predicted_price - current_price) / current_price) * 100, 2),
            'is_bullish': predicted_price > current_price,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=prediction_days)).isoformat(),
            'chart_data': chart_data
        }
    
    @staticmethod
    def _generate_chart_data(current_price, predicted_price, days):
        """生成预测图表数据"""
        data_points = []
        
        # 历史数据点（过去7天）
        for i in range(7, 0, -1):
            date = datetime.now() - timedelta(days=i)
            # 生成历史价格（围绕当前价格波动）
            price = current_price * random.uniform(0.95, 1.05)
            data_points.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(price, 2),
                'type': 'historical'
            })
        
        # 当前价格点
        data_points.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'price': current_price,
            'type': 'current'
        })
        
        # 预测数据点
        for i in range(1, days + 1):
            date = datetime.now() + timedelta(days=i)
            # 生成预测价格曲线（逐渐趋向预测价格）
            progress = i / days
            price = current_price + (predicted_price - current_price) * progress
            # 添加一些随机波动
            price *= random.uniform(0.98, 1.02)
            data_points.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': round(price, 2),
                'type': 'predicted'
            })
        
        return data_points
    
    @staticmethod
    def get_mock_user():
        """获取模拟用户信息"""
        return {
            'id': 'demo-user',
            'email': 'demo@kronos.app',
            'display_name': '演示用户',
            'subscription_tier': 'pro',
            'is_verified': True,
            'usage_today': {
                'predictions': 3,
                'api_calls': 15
            },
            'usage_limits': {
                'predictions': 500,
                'api_calls': 1000
            },
            'stats': {
                'total_predictions': 127,
                'successful_predictions': 89,
                'success_rate': 70.1
            }
        }
    
    @staticmethod
    def get_prediction_history(page=1, per_page=10):
        """获取模拟预测历史"""
        # 生成一些历史预测数据
        predictions = []
        for i in range(per_page):
            stock = random.choice(MockDataService.get_hot_stocks())
            model = random.choice(['kronos-base', 'kronos-mini', 'kronos-small'])
            days = random.choice([1, 3, 5, 10])
            
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
                prediction['actual_price'] = prediction['predicted_price'] * random.uniform(0.95, 1.05)
                prediction['accuracy'] = random.uniform(60, 95)
            
            predictions.append(prediction)
        
        return {
            'predictions': predictions,
            'total': 127,  # 模拟总数
            'pages': 13,   # 模拟总页数
            'current_page': page
        }

class MockStockService:
    """Mock股票数据服务"""
    
    @staticmethod
    def search_stocks(query):
        """股票搜索"""
        all_stocks = MockDataService.get_hot_stocks()
        
        # 模拟搜索逻辑
        if not query:
            return all_stocks[:3]
        
        results = []
        query = query.lower()
        
        for stock in all_stocks:
            if (query in stock['symbol'].lower() or 
                query in stock['name'].lower()):
                results.append(stock)
        
        # 如果没找到，返回一些相似的
        if not results and len(query) >= 2:
            results = all_stocks[:2]
        
        return results
    
    @staticmethod
    def get_stock_detail(symbol):
        """获取股票详细信息"""
        stocks = MockDataService.get_hot_stocks()
        for stock in stocks:
            if stock['symbol'] == symbol:
                # 添加更多详细信息
                stock.update({
                    'industry': '金融业',
                    'pe_ratio': round(random.uniform(8, 25), 2),
                    'pb_ratio': round(random.uniform(0.8, 3.5), 2),
                    'dividend_yield': round(random.uniform(1.5, 6.0), 2),
                    'recent_news': [
                        {'title': '公司发布Q3财报，营收同比增长15%', 'time': '2小时前'},
                        {'title': '获得新的业务合作伙伴', 'time': '1天前'},
                        {'title': '股东大会决议通过分红方案', 'time': '3天前'}
                    ]
                })
                return stock
        
        # 如果没找到，返回一个默认的
        return {
            'symbol': symbol,
            'name': '未知股票',
            'current_price': random.uniform(10, 100),
            'change_percent': random.uniform(-5, 5),
            'volume': random.randint(10000, 1000000),
            'market_cap': f'{random.randint(10, 1000)}亿'
        }
```

#### 1.2 完善预测功能路由

#### 1.1 用户管理模型
```python
# app/models/user.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """用户模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # 订阅信息
    subscription_tier = db.Column(db.String(20), default='free')
    subscription_expires = db.Column(db.DateTime, nullable=True)
    
    # 状态字段
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # 关系
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    predictions = db.relationship('Prediction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    usage_records = db.relationship('UsageRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_usage_limits(self):
        """获取用户使用限制"""
        limits = {
            'free': {'predictions': 3, 'api_calls': 10},
            'basic': {'predictions': 50, 'api_calls': 100},
            'pro': {'predictions': 500, 'api_calls': 1000},
            'enterprise': {'predictions': -1, 'api_calls': 10000}
        }
        return limits.get(self.subscription_tier, limits['free'])
    
    def is_subscription_active(self):
        """检查订阅是否有效"""
        if self.subscription_tier == 'free':
            return True
        if self.subscription_expires is None:
            return False
        return self.subscription_expires > datetime.utcnow()

class UserProfile(db.Model):
    """用户资料模型"""
    __tablename__ = 'user_profiles'
    
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), primary_key=True)
    display_name = db.Column(db.String(100), nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # 投资偏好
    risk_tolerance = db.Column(db.String(20), default='medium')  # low, medium, high
    investment_experience = db.Column(db.String(20), default='beginner')  # beginner, intermediate, expert
    preferred_sectors = db.Column(db.JSON, default=list)
    
    # 通知设置
    notification_preferences = db.Column(db.JSON, default=dict)
    
    # 统计信息
    total_predictions = db.Column(db.Integer, default=0)
    successful_predictions = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def success_rate(self):
        """预测成功率"""
        if self.total_predictions == 0:
            return 0.0
        return (self.successful_predictions / self.total_predictions) * 100
```

#### 1.2 预测管理模型
```python
# app/models/prediction.py
from datetime import datetime
import uuid
from app.models.user import db

class Prediction(db.Model):
    """预测记录模型"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 预测参数
    stock_symbol = db.Column(db.String(10), nullable=False, index=True)
    stock_name = db.Column(db.String(100), nullable=True)
    model_type = db.Column(db.String(20), nullable=False)
    prediction_days = db.Column(db.Integer, nullable=False)
    
    # 价格信息
    current_price = db.Column(db.Numeric(10, 2), nullable=False)
    predicted_price = db.Column(db.Numeric(10, 2), nullable=False)
    confidence = db.Column(db.Numeric(5, 2), nullable=False)
    
    # 预测详细数据
    prediction_data = db.Column(db.JSON, nullable=True)  # 存储图表数据等
    
    # 状态信息
    status = db.Column(db.String(20), default='active')  # active, expired, verified
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # 关系
    result = db.relationship('PredictionResult', backref='prediction', uselist=False, cascade='all, delete-orphan')
    
    @property
    def prediction_change_percent(self):
        """预测涨跌幅百分比"""
        if self.current_price == 0:
            return 0.0
        return ((self.predicted_price - self.current_price) / self.current_price) * 100
    
    @property
    def is_bullish(self):
        """是否看涨"""
        return self.predicted_price > self.current_price
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'stock_symbol': self.stock_symbol,
            'stock_name': self.stock_name,
            'model_type': self.model_type,
            'prediction_days': self.prediction_days,
            'current_price': float(self.current_price),
            'predicted_price': float(self.predicted_price),
            'confidence': float(self.confidence),
            'prediction_change_percent': self.prediction_change_percent,
            'is_bullish': self.is_bullish,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat()
        }

class PredictionResult(db.Model):
    """预测结果验证模型"""
    __tablename__ = 'prediction_results'
    
    prediction_id = db.Column(db.String(36), db.ForeignKey('predictions.id'), primary_key=True)
    actual_price = db.Column(db.Numeric(10, 2), nullable=True)
    accuracy_score = db.Column(db.Numeric(5, 2), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    @property
    def is_successful(self):
        """判断预测是否成功"""
        if self.accuracy_score is None:
            return None
        return self.accuracy_score >= 70.0  # 70%以上认为成功
```

#### 1.3 计费管理模型
```python
# app/models/billing.py
from datetime import datetime
import uuid
from app.models.user import db

class Subscription(db.Model):
    """订阅记录模型"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    plan = db.Column(db.String(20), nullable=False)  # basic, pro, enterprise
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired
    
    # 时间和金额
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='CNY')
    
    # 支付信息
    payment_method = db.Column(db.String(50), nullable=True)
    payment_id = db.Column(db.String(100), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UsageRecord(db.Model):
    """使用记录模型"""
    __tablename__ = 'usage_records'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    action_type = db.Column(db.String(20), nullable=False, index=True)  # prediction, api_call
    resource_id = db.Column(db.String(36), nullable=True)  # 关联的预测ID等
    
    # 计费信息
    cost = db.Column(db.Integer, default=1)  # 消耗的点数
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
```

### 2. 服务层重构

#### 2.1 用户服务增强
```python
# app/services/user_service.py
from flask import current_app
from app.models.user import User, UserProfile, db
from app.utils.email import send_verification_email
from app.utils.security import generate_verification_token
import jwt
from datetime import datetime, timedelta

class UserService:
    @staticmethod
    def register_user(email, password, phone=None):
        """用户注册"""
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError("邮箱已被注册")
        
        # 创建用户
        user = User(email=email, phone=phone)
        user.set_password(password)
        
        db.session.add(user)
        db.session.flush()  # 获取用户ID
        
        # 创建用户资料
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        
        db.session.commit()
        
        # 发送验证邮件
        token = generate_verification_token(user.id)
        send_verification_email(user.email, token)
        
        return user
    
    @staticmethod
    def authenticate_user(email, password):
        """用户认证"""
        user = User.query.filter_by(email=email, is_active=True).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            return user
        return None
    
    @staticmethod
    def generate_jwt_token(user):
        """生成JWT令牌"""
        payload = {
            'user_id': user.id,
            'email': user.email,
            'subscription_tier': user.subscription_tier,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def get_user_stats(user_id):
        """获取用户统计信息"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        # 获取今日使用统计
        today = datetime.utcnow().date()
        today_usage = UsageRecord.query.filter(
            UsageRecord.user_id == user_id,
            db.func.date(UsageRecord.created_at) == today
        ).all()
        
        usage_stats = {}
        for record in today_usage:
            action = record.action_type
            usage_stats[action] = usage_stats.get(action, 0) + record.cost
        
        limits = user.get_usage_limits()
        
        return {
            'usage': usage_stats,
            'limits': limits,
            'subscription_tier': user.subscription_tier,
            'subscription_active': user.is_subscription_active()
        }
```

#### 2.2 预测服务增强
```python
# app/services/prediction_service.py
from app.models.prediction import Prediction, PredictionResult, db
from app.models.billing import UsageRecord
from app.services.model_service import ModelService
from app.services.stock_service import StockService
from app.services.billing_service import BillingService
from datetime import datetime, timedelta

class PredictionService:
    def __init__(self):
        self.model_service = ModelService()
        self.stock_service = StockService()
        self.billing_service = BillingService()
    
    def create_prediction(self, user_id, stock_symbol, model_type, prediction_days):
        """创建预测"""
        # 检查使用限制
        if not self.billing_service.check_usage_limit(user_id, 'prediction'):
            raise ValueError("已达到预测次数限制，请升级套餐")
        
        # 获取股票信息
        stock_info = self.stock_service.get_stock_info(stock_symbol)
        if not stock_info:
            raise ValueError("股票代码不存在")
        
        current_price = stock_info['current_price']
        stock_name = stock_info['name']
        
        # 执行预测
        prediction_result = self.model_service.predict(
            stock_symbol, prediction_days, model_type
        )
        
        # 创建预测记录
        prediction = Prediction(
            user_id=user_id,
            stock_symbol=stock_symbol,
            stock_name=stock_name,
            model_type=model_type,
            prediction_days=prediction_days,
            current_price=current_price,
            predicted_price=prediction_result['predicted_price'],
            confidence=prediction_result['confidence'],
            prediction_data=prediction_result['chart_data'],
            expires_at=datetime.utcnow() + timedelta(days=prediction_days)
        )
        
        db.session.add(prediction)
        db.session.commit()
        
        # 记录使用
        self.billing_service.record_usage(user_id, 'prediction', prediction.id)
        
        return prediction
    
    def get_user_predictions(self, user_id, page=1, per_page=20):
        """获取用户预测历史"""
        predictions = Prediction.query.filter_by(user_id=user_id)\
            .order_by(Prediction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'predictions': [p.to_dict() for p in predictions.items],
            'total': predictions.total,
            'pages': predictions.pages,
            'current_page': page
        }
    
    def get_prediction_accuracy(self, user_id):
        """获取用户预测准确率"""
        # 获取已验证的预测
        verified_predictions = db.session.query(Prediction, PredictionResult)\
            .join(PredictionResult)\
            .filter(Prediction.user_id == user_id)\
            .filter(PredictionResult.verified_at.isnot(None))\
            .all()
        
        if not verified_predictions:
            return {'accuracy': 0.0, 'total_verified': 0}
        
        total_accuracy = sum(result.accuracy_score for _, result in verified_predictions)
        average_accuracy = total_accuracy / len(verified_predictions)
        
        return {
            'accuracy': float(average_accuracy),
            'total_verified': len(verified_predictions),
            'successful_predictions': sum(1 for _, result in verified_predictions if result.is_successful)
        }
```

#### 2.3 计费服务实现
```python
# app/services/billing_service.py
from app.models.billing import UsageRecord, Subscription, db
from app.models.user import User
from datetime import datetime, timedelta

class BillingService:
    def check_usage_limit(self, user_id, action_type):
        """检查使用限制"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        limits = user.get_usage_limits()
        limit = limits.get(action_type, 0)
        
        # 无限制
        if limit == -1:
            return True
        
        # 检查今日使用量
        today = datetime.utcnow().date()
        today_usage = UsageRecord.query.filter(
            UsageRecord.user_id == user_id,
            UsageRecord.action_type == action_type,
            db.func.date(UsageRecord.created_at) == today
        ).count()
        
        return today_usage < limit
    
    def record_usage(self, user_id, action_type, resource_id=None, cost=1):
        """记录使用"""
        usage = UsageRecord(
            user_id=user_id,
            action_type=action_type,
            resource_id=resource_id,
            cost=cost
        )
        db.session.add(usage)
        db.session.commit()
        
        return usage
    
    def create_subscription(self, user_id, plan, payment_info):
        """创建订阅"""
        plan_config = {
            'basic': {'price': 29, 'duration_days': 30},
            'pro': {'price': 99, 'duration_days': 30},
            'enterprise': {'price': 299, 'duration_days': 30}
        }
        
        if plan not in plan_config:
            raise ValueError("无效的订阅计划")
        
        config = plan_config[plan]
        
        # 创建订阅记录
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=config['duration_days']),
            amount=config['price'],
            payment_method=payment_info.get('method'),
            payment_id=payment_info.get('payment_id')
        )
        
        db.session.add(subscription)
        
        # 更新用户订阅状态
        user = User.query.get(user_id)
        user.subscription_tier = plan
        user.subscription_expires = subscription.end_date
        
        db.session.commit()
        
        return subscription
```

### 3. API端点实现

#### 3.1 认证API
```python
# app/api/auth.py
from flask import Blueprint, request, jsonify, current_app
from app.services.user_service import UserService
from app.utils.decorators import rate_limit
import jwt

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
@rate_limit(max_requests=5, window=300)  # 5次/5分钟
def register():
    """用户注册"""
    data = request.get_json()
    
    # 验证输入
    required_fields = ['email', 'password']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        user = UserService.register_user(
            email=data['email'],
            password=data['password'],
            phone=data.get('phone')
        )
        
        return jsonify({
            'message': '注册成功，请查收验证邮件',
            'user_id': user.id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
@rate_limit(max_requests=10, window=300)  # 10次/5分钟
def login():
    """用户登录"""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': '邮箱和密码不能为空'}), 400
    
    user = UserService.authenticate_user(email, password)
    if not user:
        return jsonify({'error': '邮箱或密码错误'}), 401
    
    # 生成JWT令牌
    token = UserService.generate_jwt_token(user)
    
    return jsonify({
        'message': '登录成功',
        'token': token,
        'user': {
            'id': user.id,
            'email': user.email,
            'subscription_tier': user.subscription_tier
        }
    })
```

#### 3.2 预测API
```python
# app/api/predictions.py
from flask import Blueprint, request, jsonify
from app.services.prediction_service import PredictionService
from app.utils.decorators import jwt_required, rate_limit

predictions_bp = Blueprint('predictions', __name__, url_prefix='/api/predictions')
prediction_service = PredictionService()

@predictions_bp.route('/', methods=['POST'])
@jwt_required
@rate_limit(max_requests=20, window=3600)  # 20次/小时
def create_prediction(current_user):
    """创建预测"""
    data = request.get_json()
    
    required_fields = ['stock_symbol', 'model_type', 'prediction_days']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    try:
        prediction = prediction_service.create_prediction(
            user_id=current_user.id,
            stock_symbol=data['stock_symbol'],
            model_type=data['model_type'],
            prediction_days=int(data['prediction_days'])
        )
        
        return jsonify({
            'message': '预测创建成功',
            'prediction': prediction.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@predictions_bp.route('/', methods=['GET'])
@jwt_required
def get_predictions(current_user):
    """获取预测历史"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = prediction_service.get_user_predictions(
        user_id=current_user.id,
        page=page,
        per_page=per_page
    )
    
    return jsonify(result)

@predictions_bp.route('/accuracy', methods=['GET'])
@jwt_required
def get_accuracy(current_user):
    """获取预测准确率"""
    accuracy = prediction_service.get_prediction_accuracy(current_user.id)
    return jsonify(accuracy)
```

### 4. 前端组件增强

#### 4.1 预测表单组件
```html
<!-- app/templates/components/prediction_form.html -->
<div class="prediction-form-container" id="prediction-form">
    <form hx-post="/api/predictions" 
          hx-target="#prediction-results" 
          hx-indicator="#prediction-loading"
          hx-headers='{"Authorization": "Bearer {{ user_token }}"}'>
        
        <div class="form-grid">
            <div class="form-group">
                <label for="stock_symbol">股票代码</label>
                <div class="input-with-search">
                    <input type="text" 
                           id="stock_symbol" 
                           name="stock_symbol" 
                           class="form-control"
                           placeholder="如：000001"
                           hx-get="/api/stocks/search"
                           hx-trigger="keyup changed delay:300ms"
                           hx-target="#stock-suggestions"
                           required>
                    <div id="stock-suggestions" class="suggestions-dropdown"></div>
                </div>
            </div>
            
            <div class="form-group">
                <label for="model_type">AI模型</label>
                <select id="model_type" name="model_type" class="form-control" required>
                    <option value="">选择模型</option>
                    <option value="kronos-base">Kronos Base (平衡型)</option>
                    <option value="kronos-mini">Kronos Mini (快速型)</option>
                    <option value="kronos-small">Kronos Small (精准型)</option>
                </select>
                <div class="model-info">
                    <small class="text-muted">不同模型适用于不同场景</small>
                </div>
            </div>
            
            <div class="form-group">
                <label for="prediction_days">预测周期</label>
                <select id="prediction_days" name="prediction_days" class="form-control" required>
                    <option value="1">1天 (短期)</option>
                    <option value="3">3天 (短期)</option>
                    <option value="5" selected>5天 (中期)</option>
                    <option value="10">10天 (中期)</option>
                    <option value="30">30天 (长期)</option>
                </select>
            </div>
            
            <div class="form-group">
                <button type="submit" class="btn btn-primary btn-predict">
                    <span class="btn-icon">
                        <i class="fas fa-magic"></i>
                    </span>
                    <span class="btn-text">开始预测</span>
                    <div id="prediction-loading" class="btn-spinner htmx-indicator">
                        <i class="fas fa-spinner fa-spin"></i>
                    </div>
                </button>
            </div>
        </div>
        
        <!-- 使用限制提示 -->
        <div class="usage-info">
            <div class="usage-indicator">
                <span class="usage-label">今日预测次数:</span>
                <span class="usage-count" hx-get="/api/users/usage" hx-trigger="load">
                    <span class="usage-current">{{ current_usage }}</span>
                    /
                    <span class="usage-limit">{{ usage_limit }}</span>
                </span>
            </div>
            {% if user.subscription_tier == 'free' %}
            <div class="upgrade-hint">
                <a href="/pricing" class="btn btn-outline-warning btn-sm">
                    <i class="fas fa-crown"></i>
                    升级获得更多预测次数
                </a>
            </div>
            {% endif %}
        </div>
    </form>
</div>
```

#### 4.2 预测结果组件
```html
<!-- app/templates/components/prediction_result.html -->
<div class="prediction-result-card" id="prediction-{{ prediction.id }}">
    <div class="result-header">
        <div class="stock-info">
            <h3 class="stock-name">{{ prediction.stock_name }}</h3>
            <span class="stock-code">{{ prediction.stock_symbol }}</span>
            <span class="model-badge">{{ prediction.model_type }}</span>
        </div>
        <div class="prediction-meta">
            <span class="prediction-time">{{ prediction.created_at | timeago }}</span>
            <span class="prediction-expires">{{ prediction.prediction_days }}天预测</span>
        </div>
    </div>
    
    <div class="result-content">
        <div class="price-comparison">
            <div class="price-item current">
                <label>当前价格</label>
                <span class="price-value">¥{{ "%.2f"|format(prediction.current_price) }}</span>
            </div>
            <div class="price-arrow">
                <i class="fas fa-arrow-right"></i>
            </div>
            <div class="price-item predicted">
                <label>预测价格</label>
                <span class="price-value {% if prediction.is_bullish %}text-success{% else %}text-danger{% endif %}">
                    ¥{{ "%.2f"|format(prediction.predicted_price) }}
                </span>
            </div>
        </div>
        
        <div class="prediction-metrics">
            <div class="metric-item">
                <label>预测涨跌</label>
                <span class="metric-value {% if prediction.is_bullish %}text-success{% else %}text-danger{% endif %}">
                    {% if prediction.is_bullish %}+{% endif %}{{ "%.2f"|format(prediction.prediction_change_percent) }}%
                </span>
            </div>
            <div class="metric-item">
                <label>置信度</label>
                <span class="metric-value">{{ "%.1f"|format(prediction.confidence) }}%</span>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {{ prediction.confidence }}%"></div>
                </div>
            </div>
        </div>
        
        <!-- 预测图表 -->
        <div class="prediction-chart" id="chart-{{ prediction.id }}">
            <div class="chart-loading">
                <i class="fas fa-spinner fa-spin"></i>
                <span>正在生成图表...</span>
            </div>
        </div>
    </div>
    
    <div class="result-actions">
        <button class="btn btn-outline-primary btn-sm" 
                onclick="sharePredicction('{{ prediction.id }}')">
            <i class="fas fa-share"></i>
            分享
        </button>
        <button class="btn btn-outline-secondary btn-sm"
                onclick="addToWatchlist('{{ prediction.stock_symbol }}')">
            <i class="fas fa-star"></i>
            关注
        </button>
        <button class="btn btn-outline-info btn-sm"
                onclick="viewDetails('{{ prediction.id }}')">
            <i class="fas fa-chart-line"></i>
            详情
        </button>
    </div>
</div>

<script>
// 初始化图表
document.addEventListener('DOMContentLoaded', function() {
    const chartData = {{ prediction.prediction_data | tojson }};
    createPredictionChart('chart-{{ prediction.id }}', chartData);
});
</script>
```

这个详细的技术实现指南为Kronos平台的后续开发提供了完整的代码结构和实现细节，确保了系统的可扩展性和可维护性。