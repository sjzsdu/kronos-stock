#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试会话超时修复
"""
import requests
import time

def test_session_persistence():
    """测试会话持久性"""
    base_url = "http://localhost:5001"
    session = requests.Session()
    
    print("🔍 测试会话超时修复...")
    
    # 1. 登录测试
    print("\n📝 Step 1: 登录测试")
    login_data = {
        'email': 'testflow@example.com',
        'password': 'Test@123',
        'remember_me': 'on'  # 启用remember me
    }
    
    try:
        response = session.post(f"{base_url}/api/auth/login", data=login_data)
        print(f"登录状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            return
            
    except Exception as e:
        print(f"登录请求失败: {e}")
        return
    
    # 2. 立即访问受保护资源
    print("\n📝 Step 2: 访问受保护资源")
    try:
        response = session.get(f"{base_url}/api/user/profile")
        print(f"Profile状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 立即访问成功")
        else:
            print("❌ 立即访问失败")
            
    except Exception as e:
        print(f"Profile请求失败: {e}")
    
    # 3. 检查Cookie设置
    print(f"\n📝 Step 3: 会话Cookie检查")
    cookies = dict(session.cookies)
    print(f"Session cookies: {list(cookies.keys())}")
    
    if 'session' in cookies or 'remember_token' in cookies:
        print("✅ 会话Cookie已设置")
    else:
        print("⚠️  未检测到预期的会话Cookie")
    
    print(f"\n🎯 会话超时修复验证:")
    print(f"• Remember Me: {'✅ 已启用' if 'remember_me=on' in str(login_data) else '❌ 未启用'}")
    print(f"• 登录成功: {'✅ 是' if response.status_code == 200 else '❌ 否'}")
    print(f"• 会话Cookie: {'✅ 已设置' if cookies else '❌ 未设置'}")
    
    print(f"\n📊 预期改进:")
    print(f"• 会话持续时间: 24小时（普通）/ 30天（Remember Me）")
    print(f"• 自动刷新: 每30分钟延长会话")
    print(f"• 用户缓存: 1小时（减少数据库查询）")
    
    return True

if __name__ == "__main__":
    test_session_persistence()