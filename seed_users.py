#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户系统种子数据脚本
创建测试用户、档案和示例数据
"""

import sys
import os
from datetime import datetime, timezone, timedelta, date

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.user import User, UserProfile, UserSession, UserPrediction, Watchlist


def create_seed_data():
    """创建种子数据"""
    print("🌱 开始创建用户系统种子数据...")
    
    # 创建应用上下文
    app = create_app('development')
    
    with app.app_context():
        # 清理现有数据（谨慎操作）
        print("🧹 清理现有用户数据...")
        UserPrediction.query.delete()
        Watchlist.query.delete()
        UserSession.query.delete()
        UserProfile.query.delete()
        User.query.delete()
        db.session.commit()
        
        # 创建管理员用户
        print("👑 创建管理员用户...")
        admin_user = User(
            email="admin@kronos.com",
            full_name="系统管理员",
            role="admin"
        )
        admin_user.set_password("admin123!")
        admin_user.email_verified = True
        db.session.add(admin_user)
        db.session.flush()
        
        # 创建管理员档案
        admin_profile = UserProfile(
            user_id=admin_user.id,
            nickname="Kronos管理员",
            bio="Kronos股票预测系统管理员",
            investment_experience="专业",
            risk_preference="平衡型",
            subscription_tier="enterprise"
        )
        admin_profile.set_preferences({
            "theme": "dark",
            "language": "zh-cn",
            "auto_refresh": True,
            "default_model": "kronos-base",
            "chart_style": "candlestick"
        })
        admin_profile.set_notification_settings({
            "email_notifications": True,
            "prediction_alerts": True,
            "market_updates": True,
            "weekly_summary": True
        })
        db.session.add(admin_profile)
        
        # 创建测试用户
        print("👤 创建测试用户...")
        test_users = [
            {
                "email": "demo@example.com",
                "full_name": "演示用户",
                "nickname": "股市新手",
                "bio": "刚入股市的投资新手",
                "experience": "新手",
                "risk": "保守型",
                "tier": "free"
            },
            {
                "email": "trader@example.com", 
                "full_name": "资深交易员",
                "nickname": "股神小李",
                "bio": "十年交易经验的资深投资者",
                "experience": "高级",
                "risk": "积极型",
                "tier": "premium"
            },
            {
                "email": "analyst@example.com",
                "full_name": "金融分析师",
                "nickname": "数据达人",
                "bio": "专业金融分析师，擅长技术分析",
                "experience": "专业", 
                "risk": "平衡型",
                "tier": "premium"
            }
        ]
        
        created_users = []
        for user_data in test_users:
            user = User(
                email=user_data["email"],
                full_name=user_data["full_name"],
                role="user"
            )
            user.set_password("test123!")
            user.email_verified = True
            user.last_login = datetime.now(timezone.utc) - timedelta(days=1)
            db.session.add(user)
            db.session.flush()
            
            # 创建用户档案
            profile = UserProfile(
                user_id=user.id,
                nickname=user_data["nickname"],
                bio=user_data["bio"],
                location="上海市",
                birth_date=date(1990, 1, 1),
                gender="不愿透露",
                investment_experience=user_data["experience"],
                risk_preference=user_data["risk"],
                subscription_tier=user_data["tier"]
            )
            
            if user_data["tier"] == "premium":
                profile.subscription_expires = datetime.now(timezone.utc) + timedelta(days=365)
            
            # 设置偏好
            profile.set_preferences({
                "theme": "light",
                "language": "zh-cn", 
                "auto_refresh": False,
                "default_model": "kronos-mini" if user_data["tier"] == "free" else "kronos-small",
                "chart_style": "line" if user_data["experience"] == "新手" else "candlestick"
            })
            
            profile.set_notification_settings({
                "email_notifications": True,
                "prediction_alerts": user_data["tier"] != "free",
                "market_updates": False,
                "weekly_summary": user_data["tier"] == "premium"
            })
            
            db.session.add(profile)
            created_users.append(user)
        
        db.session.commit()
        print(f"✅ 已创建 {len(created_users) + 1} 个用户（包括管理员）")
        
        # 创建关注列表数据
        print("⭐ 创建关注列表数据...")
        popular_stocks = [
            {"code": "000001", "name": "平安银行"},
            {"code": "000002", "name": "万科A"},
            {"code": "000858", "name": "五粮液"},
            {"code": "002415", "name": "海康威视"},
            {"code": "600036", "name": "招商银行"},
            {"code": "600519", "name": "贵州茅台"},
            {"code": "600887", "name": "伊利股份"},
            {"code": "000858", "name": "五粮液"}
        ]
        
        for i, user in enumerate(created_users):
            # 每个用户关注不同数量的股票
            stocks_to_add = popular_stocks[:3 + i]
            
            for j, stock in enumerate(stocks_to_add):
                watchlist_item = Watchlist(
                    user_id=user.id,
                    stock_code=stock["code"],
                    stock_name=stock["name"],
                    notes=f"关注{stock['name']}的表现",
                    sort_order=j + 1,
                    is_active=True
                )
                
                # 设置一些提醒阈值
                watchlist_item.set_alert_thresholds({
                    "price_change_percent": 5.0,
                    "volume_change_percent": 20.0,
                    "enable_alerts": True
                })
                
                db.session.add(watchlist_item)
        
        # 管理员也添加一些关注
        for j, stock in enumerate(popular_stocks[:5]):
            admin_watchlist = Watchlist(
                user_id=admin_user.id,
                stock_code=stock["code"],
                stock_name=stock["name"],
                notes=f"管理员关注：{stock['name']}",
                sort_order=j + 1,
                is_active=True
            )
            db.session.add(admin_watchlist)
        
        db.session.commit()
        print("✅ 已创建关注列表数据")
        
        # 创建历史预测记录
        print("📊 创建历史预测记录...")
        models = ["kronos-mini", "kronos-small", "kronos-base"]
        prediction_types = ["price", "trend", "volatility"]
        
        for i, user in enumerate(created_users + [admin_user]):
            # 为每个用户创建一些历史预测记录
            for j in range(5):
                stock_code = popular_stocks[j % len(popular_stocks)]["code"]
                model_type = models[j % len(models)]
                pred_type = prediction_types[j % len(prediction_types)]
                
                prediction = UserPrediction(
                    user_id=user.id,
                    stock_code=stock_code,
                    model_type=model_type,
                    prediction_type=pred_type,
                    is_favorite=(j % 3 == 0),  # 每三个标为收藏
                    notes=f"使用{model_type}模型预测{stock_code}"
                )
                
                # 模拟预测结果
                if pred_type == "price":
                    result = {
                        "forecast": [100 + i for i in range(5)],
                        "confidence": 0.75 + (j * 0.05),
                        "trend": "上涨" if j % 2 == 0 else "下跌"
                    }
                elif pred_type == "trend":
                    result = {
                        "direction": "上涨" if j % 2 == 0 else "下跌",
                        "strength": ["弱", "中", "强"][j % 3],
                        "confidence": 0.8
                    }
                else:  # volatility
                    result = {
                        "volatility_level": ["低", "中", "高"][j % 3],
                        "risk_score": 0.3 + (j * 0.1),
                        "confidence": 0.85
                    }
                
                prediction.set_prediction_result(result)
                prediction.set_metadata({
                    "model_version": "1.0",
                    "prediction_time": (datetime.now(timezone.utc) - timedelta(days=j)).isoformat(),
                    "data_quality": "good",
                    "market_conditions": "normal"
                })
                
                # 调整创建时间
                prediction.created_at = datetime.now(timezone.utc) - timedelta(days=j)
                
                db.session.add(prediction)
        
        db.session.commit()
        print("✅ 已创建历史预测记录")
        
        # 输出统计信息
        print("\n📈 种子数据统计:")
        print(f"  - 用户总数: {User.query.count()}")
        print(f"  - 用户档案: {UserProfile.query.count()}")
        print(f"  - 关注列表项: {Watchlist.query.count()}")
        print(f"  - 预测记录: {UserPrediction.query.count()}")
        
        # 输出登录信息
        print("\n🔑 测试账户登录信息:")
        print("  管理员账户:")
        print("    邮箱: admin@kronos.com")
        print("    密码: admin123!")
        print("\n  测试用户账户:")
        for user_data in test_users:
            print(f"    邮箱: {user_data['email']}")
            print(f"    密码: test123!")
        
        print("\n🎉 种子数据创建完成！")
        return True


if __name__ == "__main__":
    try:
        success = create_seed_data()
        if success:
            print("\n✅ 种子数据创建成功")
            sys.exit(0)
        else:
            print("\n❌ 种子数据创建失败")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 种子数据创建过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)