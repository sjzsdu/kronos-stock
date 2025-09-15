"""
数据库连接测试脚本
"""

import sqlite3
import os
from datetime import datetime

def test_database():
    """测试数据库连接和数据"""
    
    # 数据库文件路径
    db_path = "instance/kronos.db"
    
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在！")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔗 数据库连接成功！")
        print(f"📁 数据库位置: {os.path.abspath(db_path)}")
        print(f"📊 数据库大小: {os.path.getsize(db_path)} bytes")
        
        # 检查表数量
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 数据库表数量: {len(tables)}")
        
        # 检查各表的数据量
        print("\n📈 各表数据统计:")
        table_stats = []
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            table_stats.append((table_name, count))
            print(f"  {table_name}: {count} 条记录")
        
        # 测试用户查询
        print("\n👥 示例用户:")
        cursor.execute("SELECT id, email, subscription_tier, is_verified FROM users")
        users = cursor.fetchall()
        for user in users:
            print(f"  用户ID: {user[0]}, 邮箱: {user[1]}, 套餐: {user[2]}, 已验证: {'是' if user[3] else '否'}")
        
        # 测试预测查询
        print("\n🔮 示例预测:")
        cursor.execute("""
            SELECT p.stock_symbol, p.stock_name, p.model_type, p.current_price, 
                   p.predicted_price, p.confidence, p.status 
            FROM predictions p
        """)
        predictions = cursor.fetchall()
        for pred in predictions:
            print(f"  股票: {pred[0]} ({pred[1]}), 模型: {pred[2]}")
            print(f"    当前价格: ¥{pred[3]}, 预测价格: ¥{pred[4]}, 置信度: {pred[5]}%, 状态: {pred[6]}")
        
        # 测试系统配置
        print("\n⚙️  系统配置:")
        cursor.execute("SELECT key, value, description FROM system_configs WHERE key LIKE 'max_%'")
        configs = cursor.fetchall()
        for config in configs:
            print(f"  {config[2]}: {config[1]}")
        
        conn.close()
        print("\n✅ 数据库测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_write_operation():
    """测试数据库写操作"""
    
    db_path = "instance/kronos.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 测试插入一个新用户
        test_user_id = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_email = f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com"
        
        cursor.execute("""
            INSERT INTO users (id, email, password_hash, subscription_tier, is_verified)
            VALUES (?, ?, ?, ?, ?)
        """, (test_user_id, test_email, "test_hash", "free", 0))
        
        # 查询确认插入成功
        cursor.execute("SELECT email, subscription_tier FROM users WHERE id = ?", (test_user_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ 写操作测试成功！插入用户: {result[0]}, 套餐: {result[1]}")
            
            # 清理测试数据
            cursor.execute("DELETE FROM users WHERE id = ?", (test_user_id,))
            conn.commit()
            print("🧹 测试数据已清理")
        else:
            print("❌ 写操作测试失败！")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 写操作测试失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 开始数据库测试...\n")
    
    # 基础连接测试
    if test_database():
        print("\n" + "="*50)
        # 写操作测试
        test_write_operation()
    
    print("\n🎉 数据库测试完成！")