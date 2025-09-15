"""
数据库迁移脚本 - 创建完整的数据库结构
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import os
import uuid
from datetime import datetime, timedelta

# 创建Flask应用实例用于数据库迁移
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///kronos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

def init_database():
    """初始化数据库"""
    with app.app_context():
        try:
            print("🚀 开始创建数据库表结构...")
            
            # 先删除所有表（开发环境）
            db.drop_all()
            print("📋 已清理现有表结构")
            
            # 使用原生SQL创建表结构（兼容SQLite）
            create_tables_sqlite()
            
            # 插入示例数据（仅开发环境）
            if os.getenv('FLASK_ENV', 'development') == 'development':
                insert_sample_data()
                print("✅ 示例数据插入完成")
            
            print("🎉 数据库初始化完成！")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            import traceback
            traceback.print_exc()

def create_tables_sqlite():
    """创建SQLite数据库表结构"""
    
    # 用户表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            subscription_tier TEXT DEFAULT 'free',
            subscription_expires DATETIME,
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME
        )
    """))
    
    # 用户配置表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id TEXT PRIMARY KEY,
            display_name TEXT,
            avatar_url TEXT,
            risk_tolerance TEXT DEFAULT 'medium',
            investment_experience TEXT DEFAULT 'beginner',
            preferred_sectors TEXT,
            notification_preferences TEXT,
            total_predictions INTEGER DEFAULT 0,
            successful_predictions INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 预测记录表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            stock_name TEXT,
            model_type TEXT NOT NULL,
            prediction_days INTEGER NOT NULL,
            current_price REAL NOT NULL,
            predicted_price REAL NOT NULL,
            confidence REAL NOT NULL,
            prediction_data TEXT,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 预测结果验证表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS prediction_results (
            prediction_id TEXT PRIMARY KEY,
            actual_price REAL,
            accuracy_score REAL,
            verified_at DATETIME,
            FOREIGN KEY (prediction_id) REFERENCES predictions(id) ON DELETE CASCADE
        )
    """))
    
    # 订阅记录表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            plan TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            start_date DATETIME NOT NULL,
            end_date DATETIME,
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'CNY',
            payment_method TEXT,
            payment_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 使用记录表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS usage_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            resource_id TEXT,
            cost INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 股票数据表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS stock_data (
            symbol TEXT,
            date DATE,
            open_price REAL,
            close_price REAL,
            high_price REAL,
            low_price REAL,
            volume INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (symbol, date)
        )
    """))
    
    # 社区帖子表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            prediction_id TEXT,
            likes_count INTEGER DEFAULT 0,
            comments_count INTEGER DEFAULT 0,
            is_featured BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (prediction_id) REFERENCES predictions(id)
        )
    """))
    
    # 评论表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            post_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            content TEXT NOT NULL,
            parent_comment_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (parent_comment_id) REFERENCES comments(id)
        )
    """))
    
    # 点赞表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS likes (
            user_id TEXT,
            post_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, post_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """))
    
    # 关注列表表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS watchlists (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            stock_name TEXT,
            alert_price_high REAL,
            alert_price_low REAL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 价格预警表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS price_alerts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            stock_symbol TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            target_price REAL,
            change_percent REAL,
            is_active BOOLEAN DEFAULT 1,
            triggered_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 通知表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            data TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """))
    
    # 系统配置表
    db.session.execute(text("""
        CREATE TABLE IF NOT EXISTS system_configs (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # 创建索引
    create_indexes()
    
    db.session.commit()
    print("✅ 数据库表结构创建完成")

def create_indexes():
    """创建数据库索引"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_subscription ON users(subscription_tier, subscription_expires)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_symbol ON predictions(stock_symbol, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions(status, expires_at)",
        "CREATE INDEX IF NOT EXISTS idx_usage_records_user_date ON usage_records(user_id, action_type, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_stock_data_symbol_date ON stock_data(symbol, date)",
        "CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_posts_user ON posts(user_id, created_at)",
        "CREATE INDEX IF NOT EXISTS idx_watchlists_user ON watchlists(user_id, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_alerts_user_active ON price_alerts(user_id, is_active)",
        "CREATE INDEX IF NOT EXISTS idx_notifications_user_read ON notifications(user_id, is_read, created_at)"
    ]
    
    for index_sql in indexes:
        db.session.execute(text(index_sql))
    
    print("✅ 数据库索引创建完成")

def insert_sample_data():
    """插入示例数据"""
    
    # 插入系统配置
    configs = [
        ('app_version', '1.0.0', '应用版本号'),
        ('maintenance_mode', 'false', '维护模式开关'),
        ('max_free_predictions', '3', '免费用户每日预测次数'),
        ('max_basic_predictions', '50', '基础版用户每日预测次数'),
        ('max_pro_predictions', '500', '专业版用户每日预测次数'),
        ('prediction_accuracy_threshold', '70.0', '预测成功阈值百分比'),
        ('model_update_interval', '3600', '模型更新间隔（秒）'),
        ('stock_data_retention_days', '365', '股票数据保留天数'),
        ('notification_retention_days', '30', '通知保留天数')
    ]
    
    for key, value, desc in configs:
        db.session.execute(text(
            "INSERT OR REPLACE INTO system_configs (key, value, description) VALUES (:key, :value, :desc)"
        ), {"key": key, "value": value, "desc": desc})
    
    # 插入示例用户
    demo_users = [
        ('demo-user-1', 'demo@kronos.app', 'pbkdf2:sha256:260000$demo$hash', 'pro', True),
        ('demo-user-2', 'test@kronos.app', 'pbkdf2:sha256:260000$test$hash', 'basic', True),
        ('demo-user-3', 'free@kronos.app', 'pbkdf2:sha256:260000$free$hash', 'free', True)
    ]
    
    for user_id, email, password_hash, tier, verified in demo_users:
        db.session.execute(text(
            "INSERT OR REPLACE INTO users (id, email, password_hash, subscription_tier, is_verified) VALUES (:id, :email, :password, :tier, :verified)"
        ), {"id": user_id, "email": email, "password": password_hash, "tier": tier, "verified": verified})
    
    # 插入用户配置
    profiles = [
        ('demo-user-1', '演示用户专业版', 'high', 'expert'),
        ('demo-user-2', '演示用户基础版', 'medium', 'intermediate'),
        ('demo-user-3', '演示用户免费版', 'low', 'beginner')
    ]
    
    for user_id, name, risk, experience in profiles:
        db.session.execute(text(
            "INSERT OR REPLACE INTO user_profiles (user_id, display_name, risk_tolerance, investment_experience) VALUES (:user_id, :name, :risk, :experience)"
        ), {"user_id": user_id, "name": name, "risk": risk, "experience": experience})
    
    # 插入股票数据
    stock_data = [
        ('000001', '2024-01-01', 12.50, 12.75, 12.80, 12.45, 1000000),
        ('000002', '2024-01-01', 18.75, 18.90, 19.00, 18.60, 800000),
        ('600519', '2024-01-01', 1680.00, 1695.50, 1700.00, 1675.00, 50000)
    ]
    
    for symbol, date, open_p, close_p, high_p, low_p, volume in stock_data:
        db.session.execute(text(
            "INSERT OR REPLACE INTO stock_data (symbol, date, open_price, close_price, high_price, low_price, volume) VALUES (:symbol, :date, :open_p, :close_p, :high_p, :low_p, :volume)"
        ), {"symbol": symbol, "date": date, "open_p": open_p, "close_p": close_p, "high_p": high_p, "low_p": low_p, "volume": volume})
    
    # 插入预测记录
    predictions = [
        ('pred-1', 'demo-user-1', '000001', '平安银行', 'kronos-base', 5, 12.75, 13.20, 85.5, 'active', '2024-01-01 10:00:00', '2024-01-06 10:00:00'),
        ('pred-2', 'demo-user-1', '600519', '贵州茅台', 'kronos-pro', 10, 1695.50, 1750.00, 78.2, 'active', '2024-01-01 11:00:00', '2024-01-11 11:00:00')
    ]
    
    for pred in predictions:
        db.session.execute(text(
            "INSERT OR REPLACE INTO predictions (id, user_id, stock_symbol, stock_name, model_type, prediction_days, current_price, predicted_price, confidence, status, created_at, expires_at) VALUES (:id, :user_id, :symbol, :name, :model, :days, :current, :predicted, :confidence, :status, :created, :expires)"
        ), {
            "id": pred[0], "user_id": pred[1], "symbol": pred[2], "name": pred[3], 
            "model": pred[4], "days": pred[5], "current": pred[6], "predicted": pred[7], 
            "confidence": pred[8], "status": pred[9], "created": pred[10], "expires": pred[11]
        })
    
    # 插入社区帖子
    posts = [
        ('post-1', 'demo-user-1', '平安银行短期看涨分析', '基于技术面分析，平安银行有望在未来5天内上涨至13.20元...', 'pred-1', 15, 3),
        ('post-2', 'demo-user-1', '贵州茅台中期投资机会', '从基本面看，贵州茅台具备长期投资价值...', 'pred-2', 28, 7)
    ]
    
    for post in posts:
        db.session.execute(text(
            "INSERT OR REPLACE INTO posts (id, user_id, title, content, prediction_id, likes_count, comments_count) VALUES (:id, :user_id, :title, :content, :pred_id, :likes, :comments)"
        ), {
            "id": post[0], "user_id": post[1], "title": post[2], "content": post[3], 
            "pred_id": post[4], "likes": post[5], "comments": post[6]
        })
    
    db.session.commit()

if __name__ == '__main__':
    init_database()