import os
from typing import Dict, Any
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kronos_stock.db'
    
    # 数据库连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': int(os.environ.get('DB_POOL_SIZE', 10)),
        'max_overflow': int(os.environ.get('DB_MAX_OVERFLOW', 20)),
        'pool_timeout': int(os.environ.get('DB_POOL_TIMEOUT', 30)),
        'pool_recycle': int(os.environ.get('DB_POOL_RECYCLE', 3600))
    }
    
    # 用户认证配置
    LOGIN_MANAGER_LOGIN_VIEW = 'auth_views.login_page'
    LOGIN_MANAGER_LOGIN_MESSAGE = '请登录以访问此页面'
    LOGIN_MANAGER_SESSION_PROTECTION = 'strong'
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(seconds=int(os.environ.get('PERMANENT_SESSION_LIFETIME', 86400)))
    
    # 密码安全配置
    BCRYPT_LOG_ROUNDS = 12  # bcrypt 加密轮数
    PASSWORD_MIN_LENGTH = int(os.environ.get('PASSWORD_MIN_LENGTH', 8))
    PASSWORD_REQUIRE_NUMBERS = os.environ.get('PASSWORD_REQUIRE_NUMBERS', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.environ.get('PASSWORD_REQUIRE_SPECIAL', 'True').lower() == 'true'
    
    # 登录安全限制
    MAX_LOGIN_ATTEMPTS = int(os.environ.get('MAX_LOGIN_ATTEMPTS', 5))
    LOGIN_LOCKOUT_DURATION = int(os.environ.get('LOGIN_LOCKOUT_DURATION', 1800))
    
    # JWT 配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时 (秒)
    
    # 邮件服务配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # 文件上传配置
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 5242880))  # 5MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif').split(','))
    
    # Redis配置（可选）
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    USE_REDIS_SESSIONS = os.environ.get('USE_REDIS_SESSIONS', 'False').lower() == 'true'
    
    # 缓存配置
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'logs/app.log')
    LOG_MAX_SIZE = int(os.environ.get('LOG_MAX_SIZE', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # 安全Headers配置
    CONTENT_SECURITY_POLICY = os.environ.get('CONTENT_SECURITY_POLICY', 
        "default-src 'self'; script-src 'self' 'unsafe-inline' https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data: https:;"
    )
    
    # 性能监控配置
    ENABLE_PROFILING = os.environ.get('ENABLE_PROFILING', 'False').lower() == 'true'
    PROFILING_SAMPLE_RATE = float(os.environ.get('PROFILING_SAMPLE_RATE', 0.1))
    
    # 健康检查配置
    HEALTH_CHECK_ENDPOINT = os.environ.get('HEALTH_CHECK_ENDPOINT', '/api/health')
    
    # 第三方服务配置
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID')
    
    # Model configurations
    MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
    EMBEDDED_MODEL_DIR = os.path.join(os.path.dirname(__file__), 'model')
    DEFAULT_MODEL = os.environ.get('DEFAULT_MODEL', 'kronos-mini')
    MODEL_DEVICE = os.environ.get('MODEL_DEVICE', 'cpu')
    MAX_CONCURRENT_PREDICTIONS = int(os.environ.get('MAX_CONCURRENT_PREDICTIONS', 3))
    
    # Available models configuration
    AVAILABLE_MODELS = {
        'kronos-mini': {
            'path': 'kronos-mini',
            'description': 'Lightweight model for fast inference',
            'size': 'Small (~100MB)',
            'performance': 'Fast'
        },
        'kronos-small': {
            'path': 'kronos-small', 
            'description': 'Balanced model for general use',
            'size': 'Medium (~500MB)',
            'performance': 'Balanced'
        },
        'kronos-base': {
            'path': 'kronos-base',
            'description': 'Full-featured model for best accuracy',
            'size': 'Large (~1GB)',
            'performance': 'Best'
        }
    }
    
    # Default prediction parameters
    DEFAULT_PREDICTION_PARAMS = {
        'lookback': 30,
        'pred_len': 5,
        'temperature': float(os.environ.get('DEFAULT_TEMPERATURE', 0.7))
    }
    
    # 股票数据配置
    STOCK_DATA_PROVIDER = os.environ.get('STOCK_DATA_PROVIDER', 'china_stock_data')
    STOCK_DATA_API_KEY = os.environ.get('STOCK_DATA_API_KEY')
    DATA_UPDATE_INTERVAL = int(os.environ.get('DATA_UPDATE_INTERVAL', 15))
    MAX_PREDICTION_DAYS = int(os.environ.get('MAX_PREDICTION_DAYS', 30))
    
    # CORS settings
    CORS_ORIGINS = [origin.strip() for origin in os.environ.get('CORS_ORIGINS', '*').split(',')]
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 开发环境使用 SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///kronos_stock_dev.db'
    
    # SQLite 不使用连接池配置，但需要开启外键约束
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'check_same_thread': False}
    }
    
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    # 生产环境使用 MySQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f"mysql+pymysql://{os.environ.get('DB_USER', 'kronos')}:" \
        f"{os.environ.get('DB_PASSWORD', 'your-secure-password')}@" \
        f"{os.environ.get('DB_HOST', 'localhost')}:" \
        f"{os.environ.get('DB_PORT', '3306')}/" \
        f"{os.environ.get('DB_NAME', 'kronos_stock_prod')}"
    
    # 生产环境安全配置
    BCRYPT_LOG_ROUNDS = 14  # 更高的加密强度
    PERMANENT_SESSION_LIFETIME = 21600  # 6小时 (更短的会话时间)

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 测试环境不使用连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # 测试环境快速配置
    BCRYPT_LOG_ROUNDS = 4  # 更快的测试速度
    WTF_CSRF_ENABLED = False  # 禁用 CSRF 用于测试

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}