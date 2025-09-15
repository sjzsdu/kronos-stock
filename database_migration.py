"""
数据库迁移脚本 - 创建完整的数据库结构
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

# 创建Flask应用实例用于数据库迁移
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kronos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 数据库表结构定义
def create_tables():
    """创建数据库表结构"""
    
    # 删除现有表（仅在开发环境）
    db.drop_all()
    
    # 创建所有表
    db.create_all()
    
    print("✅ 数据库表结构创建完成")

# SQL创建语句（用于生产环境）
CREATE_TABLES_SQL = """
-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    subscription_tier VARCHAR(20) DEFAULT 'free',
    subscription_expires TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- 用户配置表
CREATE TABLE IF NOT EXISTS user_profiles (
    user_id VARCHAR(36) PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    avatar_url VARCHAR(500),
    risk_tolerance VARCHAR(20) DEFAULT 'medium',
    investment_experience VARCHAR(20) DEFAULT 'beginner',
    preferred_sectors JSON,
    notification_preferences JSON,
    total_predictions INTEGER DEFAULT 0,
    successful_predictions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 预测记录表
CREATE TABLE IF NOT EXISTS predictions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_symbol VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    model_type VARCHAR(20) NOT NULL,
    prediction_days INTEGER NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    predicted_price DECIMAL(10,2) NOT NULL,
    confidence DECIMAL(5,2) NOT NULL,
    prediction_data JSON,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- 预测结果验证表
CREATE TABLE IF NOT EXISTS prediction_results (
    prediction_id VARCHAR(36) PRIMARY KEY REFERENCES predictions(id) ON DELETE CASCADE,
    actual_price DECIMAL(10,2),
    accuracy_score DECIMAL(5,2),
    verified_at TIMESTAMP
);

-- 订阅记录表
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CNY',
    payment_method VARCHAR(50),
    payment_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 使用记录表
CREATE TABLE IF NOT EXISTS usage_records (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    action_type VARCHAR(20) NOT NULL,
    resource_id VARCHAR(36),
    cost INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 股票数据表
CREATE TABLE IF NOT EXISTS stock_data (
    symbol VARCHAR(10),
    date DATE,
    open_price DECIMAL(10,2),
    close_price DECIMAL(10,2),
    high_price DECIMAL(10,2),
    low_price DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (symbol, date)
);

-- 社区帖子表
CREATE TABLE IF NOT EXISTS posts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    content TEXT NOT NULL,
    prediction_id VARCHAR(36) REFERENCES predictions(id),
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 评论表
CREATE TABLE IF NOT EXISTS comments (
    id VARCHAR(36) PRIMARY KEY,
    post_id VARCHAR(36) NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    parent_comment_id VARCHAR(36) REFERENCES comments(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 点赞表
CREATE TABLE IF NOT EXISTS likes (
    user_id VARCHAR(36) REFERENCES users(id) ON DELETE CASCADE,
    post_id VARCHAR(36) REFERENCES posts(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, post_id)
);

-- 关注列表表
CREATE TABLE IF NOT EXISTS watchlists (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_symbol VARCHAR(10) NOT NULL,
    stock_name VARCHAR(100),
    alert_price_high DECIMAL(10,2),
    alert_price_low DECIMAL(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 价格预警表
CREATE TABLE IF NOT EXISTS price_alerts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(20) NOT NULL, -- 'above', 'below', 'change_percent'
    target_price DECIMAL(10,2),
    change_percent DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE,
    triggered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 通知表
CREATE TABLE IF NOT EXISTS notifications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSON,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier, subscription_expires);
CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(stock_symbol, created_at);
CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(status, expires_at);
CREATE INDEX IF NOT EXISTS idx_usage_records_user_date ON usage_records(user_id, action_type, created_at);
CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date);
CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON price_alerts(user_id, is_active);
CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read, created_at);

-- 插入初始数据
INSERT INTO system_configs (key, value, description) VALUES 
('app_version', '1.0.0', '应用版本号'),
('maintenance_mode', 'false', '维护模式开关'),
('max_free_predictions', '3', '免费用户每日预测次数'),
('max_basic_predictions', '50', '基础版用户每日预测次数'),
('max_pro_predictions', '500', '专业版用户每日预测次数'),
('prediction_accuracy_threshold', '70.0', '预测成功阈值百分比'),
('model_update_interval', '3600', '模型更新间隔（秒）'),
('stock_data_retention_days', '365', '股票数据保留天数'),
('notification_retention_days', '30', '通知保留天数');
"""

# 示例数据插入脚本
SAMPLE_DATA_SQL = """
-- 插入示例用户（仅开发环境）
INSERT INTO users (id, email, password_hash, subscription_tier, is_verified) VALUES 
('demo-user-1', 'demo@kronos.app', 'pbkdf2:sha256:260000$demo$hash', 'pro', TRUE),
('demo-user-2', 'test@kronos.app', 'pbkdf2:sha256:260000$test$hash', 'basic', TRUE),
('demo-user-3', 'free@kronos.app', 'pbkdf2:sha256:260000$free$hash', 'free', TRUE);

-- 插入示例用户配置
INSERT INTO user_profiles (user_id, display_name, risk_tolerance, investment_experience) VALUES 
('demo-user-1', '演示用户专业版', 'high', 'expert'),
('demo-user-2', '演示用户基础版', 'medium', 'intermediate'),
('demo-user-3', '演示用户免费版', 'low', 'beginner');

-- 插入示例股票数据
INSERT INTO stock_data (symbol, date, open_price, close_price, high_price, low_price, volume) VALUES 
('000001', '2024-01-01', 12.50, 12.75, 12.80, 12.45, 1000000),
('000002', '2024-01-01', 18.75, 18.90, 19.00, 18.60, 800000),
('600519', '2024-01-01', 1680.00, 1695.50, 1700.00, 1675.00, 50000);

-- 插入示例预测记录
INSERT INTO predictions (id, user_id, stock_symbol, stock_name, model_type, prediction_days, current_price, predicted_price, confidence, status, created_at, expires_at) VALUES 
('pred-1', 'demo-user-1', '000001', '平安银行', 'kronos-base', 5, 12.75, 13.20, 85.5, 'active', '2024-01-01 10:00:00', '2024-01-06 10:00:00'),
('pred-2', 'demo-user-1', '600519', '贵州茅台', 'kronos-pro', 10, 1695.50, 1750.00, 78.2, 'active', '2024-01-01 11:00:00', '2024-01-11 11:00:00');

-- 插入示例社区帖子
INSERT INTO posts (id, user_id, title, content, prediction_id, likes_count, comments_count) VALUES 
('post-1', 'demo-user-1', '平安银行短期看涨分析', '基于技术面分析，平安银行有望在未来5天内上涨至13.20元...', 'pred-1', 15, 3),
('post-2', 'demo-user-1', '贵州茅台中期投资机会', '从基本面看，贵州茅台具备长期投资价值...', 'pred-2', 28, 7);
"""

def init_database():
    """初始化数据库"""
    try:
        # 执行建表语句
        with app.app_context():
            # 先删除所有表
            db.drop_all()
            
            # 执行SQL创建语句
            statements = CREATE_TABLES_SQL.split(';')
            for statement in statements:
                if statement.strip():
                    db.session.execute(statement)
            
            db.session.commit()
            print("✅ 数据库表结构创建完成")
            
            # 插入示例数据（仅开发环境）
            if os.getenv('FLASK_ENV') == 'development':
                sample_statements = SAMPLE_DATA_SQL.split(';')
                for statement in sample_statements:
                    if statement.strip():
                        try:
                            db.session.execute(statement)
                        except Exception as e:
                            print(f"⚠️  示例数据插入失败: {e}")
                
                db.session.commit()
                print("✅ 示例数据插入完成")
            
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        db.session.rollback()

if __name__ == '__main__':
    init_database()