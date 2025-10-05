#!/usr/bin/env python3
"""
重新创建数据库表
"""

from app import create_app
from app.models import db

def recreate_database():
    """重新创建数据库"""
    app = create_app('development')
    
    with app.app_context():
        print("🗑️  删除所有表...")
        db.drop_all()
        
        print("🆕 创建所有表...")
        db.create_all()
        
        print("✅ 数据库重新创建完成！")

if __name__ == "__main__":
    recreate_database()