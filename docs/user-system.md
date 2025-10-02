# Kronos Stock 用户系统使用指南

## 概述

Kronos Stock 用户系统为股票预测平台提供完整的用户管理功能，包括用户注册、登录认证、档案管理、股票关注列表等核心功能。本文档面向系统管理员和开发者，详细介绍用户系统的架构、功能和使用方法。

## 系统架构

### 技术栈

- **后端框架**: Flask + Flask-Login + Flask-Migrate
- **数据库**: SQLite (开发) / MySQL (生产)
- **认证方式**: JWT (API) + Session (Web页面)
- **密码加密**: bcrypt (12轮加密)
- **前端技术**: HTMX + TailwindCSS
- **缓存系统**: 内存缓存 / Redis (可选)

### 模块组织

```
app/
├── models/                 # 数据模型
│   ├── user.py            # 用户模型
│   ├── user_profile.py    # 用户档案模型
│   ├── user_session.py    # 用户会话模型
│   └── watchlist.py       # 关注列表模型
├── services/              # 业务逻辑层
│   ├── auth_service.py    # 认证服务
│   ├── user_service.py    # 用户管理服务
│   └── password_service.py # 密码服务
├── api/                   # REST API端点
│   ├── auth.py           # 认证API
│   └── user.py           # 用户API
├── views/                 # Web视图控制器
│   ├── auth.py           # 认证页面
│   └── user.py           # 用户页面
├── templates/             # 模板文件
│   ├── auth/             # 认证相关页面
│   └── user/             # 用户相关页面
├── middleware/            # 中间件
│   ├── auth_middleware.py # 认证中间件
│   └── session_middleware.py # 会话中间件
└── utils/                 # 工具函数
    └── validators.py      # 数据验证器
```

## 核心功能

### 1. 用户注册与认证

#### 用户注册流程

1. **数据验证**: 验证用户名、邮箱、密码等字段
2. **重复性检查**: 确保用户名和邮箱的唯一性
3. **密码加密**: 使用bcrypt进行密码哈希
4. **账户创建**: 创建用户记录和默认档案
5. **邮箱验证**: (可选) 发送验证邮件

```python
# 用户注册示例
from app.services.user_service import UserService

user_service = UserService()
result = user_service.create_user(
    username='newuser',
    email='user@example.com',
    password='SecurePassword123!',
    nickname='新用户'
)

if result['success']:
    print(f"用户创建成功: {result['user'].username}")
else:
    print(f"创建失败: {result['message']}")
```

#### 登录认证机制

系统支持两种认证方式：

**1. Web会话认证 (用于页面)**
```python
# 使用Flask会话进行认证
from flask import session
from app.decorators import login_required

@login_required
def dashboard():
    user_id = session['user_id']
    return render_template('user/dashboard.html')
```

**2. JWT令牌认证 (用于API)**
```python
# 使用JWT令牌进行API认证
from app.decorators import token_required

@token_required
def api_get_profile(user_id):
    user = User.query.get(user_id)
    return jsonify(user.to_dict())
```

### 2. 用户档案管理

#### 档案字段说明

用户档案包含以下信息：

- **基础信息**: 真实姓名、手机号、性别、生日、地址
- **投资偏好**: 投资经验、风险承受能力、投资目标
- **个人简介**: 自我介绍和备注信息

```python
# 更新用户档案
from app.services.user_service import UserService

user_service = UserService()
profile_data = {
    'real_name': '张三',
    'phone': '13812345678',
    'gender': 'male',
    'investment_experience': '中级',
    'risk_tolerance': '稳健'
}

result = user_service.update_user_profile(user_id=1, profile_data=profile_data)
```

### 3. 股票关注列表

#### 功能特性

- **添加关注**: 支持通过股票代码添加关注
- **批量管理**: 支持批量添加和删除
- **实时同步**: 关注状态实时更新
- **分组管理**: 支持自定义分组 (未来功能)

```python
# 管理关注列表
from app.services.user_service import UserService

user_service = UserService()

# 添加股票到关注列表
result = user_service.add_to_watchlist(
    user_id=1,
    stock_code='000001',
    stock_name='平安银行'
)

# 获取用户关注列表
watchlist = user_service.get_user_watchlist(user_id=1)
```

### 4. 会话管理

#### 会话生命周期

- **创建**: 登录成功后创建会话记录
- **验证**: 每次请求时验证会话有效性
- **更新**: 定期更新最后访问时间
- **清理**: 自动清理过期会话

```python
# 会话管理示例
from app.services.auth_service import AuthService

auth_service = AuthService()

# 生成访问令牌
token = auth_service.generate_token(user_id=1)

# 验证令牌
verification = auth_service.verify_token(token)
if verification['valid']:
    print(f"用户ID: {verification['user_id']}")

# 撤销令牌
auth_service.revoke_token(token)
```

## 安全特性

### 1. 密码安全

- **强度要求**: 至少8位，包含大小写字母、数字和特殊字符
- **哈希算法**: bcrypt with 12 rounds
- **常见密码检测**: 防止使用常见弱密码
- **历史密码**: 防止重复使用近期密码 (可选)

```python
# 密码验证示例
from app.services.password_service import PasswordService

password_service = PasswordService()

# 验证密码强度
validation = password_service.validate_password_strength('NewPassword123!')
if validation['valid']:
    # 密码符合要求
    hashed = password_service.hash_password('NewPassword123!')
else:
    print(f"密码不符合要求: {validation['errors']}")
```

### 2. 认证保护

- **速率限制**: 登录尝试频率限制 (5次/分钟)
- **会话管理**: 自动会话过期和清理
- **令牌安全**: JWT令牌加密和签名验证
- **中间件保护**: 自动认证检查和权限验证

```python
# 使用认证装饰器保护端点
from app.decorators import login_required, admin_required

@login_required
def user_dashboard():
    """需要登录的页面"""
    return render_template('user/dashboard.html')

@admin_required
def admin_panel():
    """需要管理员权限的页面"""
    return render_template('admin/panel.html')
```

### 3. 数据验证

- **输入清理**: 防止XSS和SQL注入
- **字段验证**: 严格的数据格式验证
- **长度限制**: 防止缓冲区溢出攻击
- **类型检查**: 确保数据类型正确性

```python
# 数据验证示例
from app.utils.validators import FormValidator

validator = FormValidator()

# 验证注册表单
form_data = {
    'username': 'newuser',
    'email': 'user@example.com',
    'password': 'SecurePassword123!'
}

validation = validator.validate_registration_form(form_data)
if not validation['valid']:
    print(f"验证错误: {validation['errors']}")
```

## 性能优化

### 1. 缓存策略

系统实现了多层缓存机制：

- **用户信息缓存**: 减少重复的数据库查询
- **会话缓存**: 快速验证用户认证状态
- **档案缓存**: 缓存用户详细资料

```python
# 缓存配置
CACHE_CONFIG = {
    'USER_CACHE_TTL': 300,          # 用户信息缓存5分钟
    'SESSION_CACHE_TTL': 600,       # 会话缓存10分钟
    'PROFILE_CACHE_TTL': 1800,      # 档案缓存30分钟
    'CACHE_TYPE': 'memory'          # 缓存类型: memory/redis
}
```

### 2. 数据库优化

- **索引优化**: 为常用查询字段建立索引
- **查询优化**: 减少N+1查询问题
- **连接池**: 数据库连接复用
- **分页查询**: 大量数据分页加载

```sql
-- 重要的数据库索引
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_sessions_token ON user_sessions(token);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_watchlist_user_stock ON watchlist(user_id, stock_code);
```

### 3. 前端优化

- **HTMX动态加载**: 减少完整页面刷新
- **组件复用**: 模块化的UI组件
- **懒加载**: 按需加载用户数据
- **缓存头设置**: 合理的HTTP缓存策略

## 配置说明

### 1. 环境变量配置

```bash
# 数据库配置
DATABASE_URL=sqlite:///kronos_stock.db
MYSQL_DATABASE_URI=mysql://user:password@localhost/kronos_stock

# 认证配置
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# 邮件配置 (用于密码重置)
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password

# 缓存配置
REDIS_URL=redis://localhost:6379/0
USER_CACHE_TYPE=memory

# 安全配置
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
PERMANENT_SESSION_LIFETIME=86400
```

### 2. Flask应用配置

```python
# config.py 用户系统相关配置
class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kronos_stock.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 认证配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # 用户系统配置
    USER_REGISTRATION_ENABLED = True
    USER_EMAIL_VERIFICATION_REQUIRED = False
    PASSWORD_RESET_ENABLED = True
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # 速率限制配置
    RATELIMIT_STORAGE_URL = 'memory://'
    LOGIN_RATE_LIMIT = '5 per minute'
    REGISTER_RATE_LIMIT = '3 per hour'
```

## 部署指南

### 1. 开发环境部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 初始化数据库
flask db init
flask db migrate -m "Initial user system migration"
flask db upgrade

# 3. 创建管理员用户 (可选)
python -c "
from app import create_app
from app.services.user_service import UserService
app = create_app()
with app.app_context():
    user_service = UserService()
    result = user_service.create_user(
        username='admin',
        email='admin@example.com',
        password='AdminPassword123!',
        is_admin=True
    )
    print(result['message'])
"

# 4. 启动应用
python run.py
```

### 2. 生产环境部署

```bash
# 1. 设置环境变量
export FLASK_ENV=production
export SECRET_KEY='your-production-secret-key'
export DATABASE_URL='mysql://user:password@localhost/kronos_stock'
export REDIS_URL='redis://localhost:6379/0'

# 2. 安装依赖
pip install -r requirements.txt
pip install gunicorn redis

# 3. 数据库迁移
flask db upgrade

# 4. 使用Gunicorn启动
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### 3. Docker部署

```dockerfile
# Dockerfile 示例
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 创建非root用户
RUN adduser --disabled-password appuser
USER appuser

EXPOSE 5001

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5001", "run:app"]
```

```yaml
# docker-compose.yml 示例
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5001:5001"
    environment:
      - DATABASE_URL=mysql://root:password@db/kronos_stock
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: kronos_stock
    volumes:
      - mysql_data:/var/lib/mysql

  redis:
    image: redis:7-alpine
    
volumes:
  mysql_data:
```

## 测试指南

### 1. 单元测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行用户系统相关测试
python -m pytest tests/unit/test_user_service.py
python -m pytest tests/unit/test_auth_service.py

# 运行集成测试
python -m pytest tests/integration/test_auth_flow.py

# 生成测试覆盖率报告
python -m pytest --cov=app tests/
```

### 2. API测试

```python
# 使用requests进行API测试
import requests

# 测试用户注册
def test_user_registration():
    url = 'http://localhost:5001/api/auth/register'
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!'
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 201
    assert response.json()['success'] == True

# 测试用户登录
def test_user_login():
    url = 'http://localhost:5001/api/auth/login'
    data = {
        'username': 'testuser',
        'password': 'TestPassword123!'
    }
    
    response = requests.post(url, json=data)
    assert response.status_code == 200
    assert 'access_token' in response.json()['data']
```

### 3. 性能测试

```python
# 使用内置的性能测试脚本
python tests/performance/run_performance_tests.py --users 10 --login-workers 3

# 或者使用pytest-benchmark
python -m pytest tests/performance/test_login_performance.py --benchmark-only
```

## 监控和维护

### 1. 日志监控

系统提供详细的日志记录：

```python
# 日志配置
LOGGING_CONFIG = {
    'version': 1,
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'logs/user_system.log',
            'level': 'INFO',
            'formatter': 'detailed'
        }
    },
    'loggers': {
        'app.services.auth_service': {
            'handlers': ['file'],
            'level': 'INFO'
        }
    }
}
```

### 2. 健康检查

```python
# 健康检查端点
@app.route('/api/health/user-system')
def user_system_health():
    checks = {
        'database': check_database_connection(),
        'cache': check_cache_connection(),
        'auth_service': check_auth_service(),
    }
    
    return jsonify({
        'status': 'healthy' if all(checks.values()) else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    })
```

### 3. 定期维护任务

```python
# 定期清理过期会话
from app.services.auth_service import AuthService

def cleanup_expired_sessions():
    auth_service = AuthService()
    result = auth_service.cleanup_expired_sessions()
    print(f"清理了 {result['cleaned_count']} 个过期会话")

# 可以通过cron job或Celery任务定期执行
```

## 常见问题解决

### 1. 认证问题

**问题**: 用户无法登录
```python
# 检查步骤：
# 1. 验证用户名和密码
# 2. 检查用户状态是否为激活
# 3. 查看错误日志
# 4. 验证数据库连接

# 调试代码
user = User.query.filter_by(username='problematic_user').first()
if user:
    print(f"用户状态: {'激活' if user.is_active else '禁用'}")
    print(f"最后登录: {user.last_login_at}")
```

**问题**: JWT令牌验证失败
```python
# 检查JWT配置
import jwt
from flask import current_app

try:
    payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
    print(f"令牌有效，用户ID: {payload['user_id']}")
except jwt.ExpiredSignatureError:
    print("令牌已过期")
except jwt.InvalidTokenError:
    print("令牌无效")
```

### 2. 性能问题

**问题**: 登录响应慢
```python
# 优化建议：
# 1. 启用用户缓存
# 2. 优化数据库查询
# 3. 检查网络延迟

# 性能分析
import time
from app.services.auth_service import AuthService

start_time = time.time()
auth_service = AuthService()
result = auth_service.authenticate_with_credentials('username', 'password')
end_time = time.time()

print(f"认证耗时: {end_time - start_time:.3f}秒")
```

### 3. 数据库问题

**问题**: 数据迁移失败
```bash
# 解决步骤：
# 1. 检查数据库连接
flask db current

# 2. 查看迁移历史
flask db history

# 3. 手动回滚和重新应用
flask db downgrade
flask db upgrade

# 4. 如果有冲突，解决冲突后重新生成迁移
flask db revision --autogenerate -m "Fix migration conflicts"
```

## 扩展功能

### 1. 社交登录集成

```python
# OAuth2 社交登录示例 (需要额外依赖)
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app)

# 配置微信登录
wechat = oauth.register(
    name='wechat',
    client_id='your_wechat_app_id',
    client_secret='your_wechat_app_secret',
    authorize_url='https://open.weixin.qq.com/connect/oauth2/authorize',
    access_token_url='https://api.weixin.qq.com/sns/oauth2/access_token'
)

@app.route('/auth/wechat')
def wechat_login():
    redirect_uri = url_for('wechat_callback', _external=True)
    return wechat.authorize_redirect(redirect_uri)
```

### 2. 多因素认证 (MFA)

```python
# TOTP 二次验证示例
import pyotp
import qrcode

def setup_mfa(user):
    # 生成密钥
    secret = pyotp.random_base32()
    user.mfa_secret = secret
    
    # 生成二维码
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.username,
        issuer_name="Kronos Stock"
    )
    
    qr = qrcode.QRCode()
    qr.add_data(totp_uri)
    qr.make()
    
    return qr.make_image()

def verify_mfa(user, token):
    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(token)
```

### 3. 审计日志

```python
# 用户操作审计
from datetime import datetime

class UserAuditLog:
    def __init__(self):
        self.logger = logging.getLogger('audit')
    
    def log_login(self, user_id, ip_address, success=True):
        self.logger.info(f"LOGIN {'SUCCESS' if success else 'FAILED'} - "
                        f"User: {user_id}, IP: {ip_address}, "
                        f"Time: {datetime.utcnow()}")
    
    def log_profile_update(self, user_id, fields_changed):
        self.logger.info(f"PROFILE UPDATE - User: {user_id}, "
                        f"Fields: {fields_changed}, "
                        f"Time: {datetime.utcnow()}")
```

## 版本更新记录

### v1.0.0 (2023-12-01)
- 初始版本发布
- 实现基础用户注册和认证功能
- 添加用户档案管理
- 实现股票关注列表功能
- 集成JWT和Session双重认证
- 实现缓存优化和性能测试

### 计划中的功能
- 社交登录集成
- 多因素认证 (MFA)
- 用户权限管理系统
- 高级审计日志
- API访问密钥管理

---

**联系支持**: 如有问题或建议，请通过GitHub Issues或邮件联系开发团队。