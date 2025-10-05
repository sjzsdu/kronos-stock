#!/usr/bin/env python3
"""
完整的认证流程测试
"""
import requests
import json

def test_complete_auth_flow():
    """测试完整的注册→登录→访问受保护资源流程"""
    base_url = "http://localhost:5001"
    
    # 用于保持会话的session对象
    session = requests.Session()
    
    print("🔍 测试完整认证流程...")
    
    # 1. 测试注册
    print("\n📝 Step 1: 测试注册")
    register_data = {
        'nickname': 'testflow',
        'email': 'testflow@example.com',
        'password': 'Test@123',
        'confirm_password': 'Test@123',
        'agree_terms': 'on'
    }
    
    try:
        response = session.post(
            f"{base_url}/api/auth/register",
            data=register_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f"注册状态码: {response.status_code}")
        print(f"注册响应: {response.text[:200]}...")
        
        if response.status_code in [200, 201]:
            print("✅ 注册成功")
        else:
            print("❌ 注册失败")
            return
            
    except Exception as e:
        print(f"注册请求失败: {e}")
        return
    
    # 2. 测试登录  
    print("\n📝 Step 2: 测试登录")
    login_data = {
        'email': 'testflow@example.com',
        'password': 'Test@123',
        'remember_me': 'on'
    }
    
    try:
        response = session.post(
            f"{base_url}/api/auth/login",
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f"登录状态码: {response.status_code}")
        print(f"登录响应: {response.text[:200]}...")
        print(f"登录Cookies: {dict(session.cookies)}")
        
        if response.status_code == 200:
            print("✅ 登录成功")
        else:
            print("❌ 登录失败")
            return
            
    except Exception as e:
        print(f"登录请求失败: {e}")
        return
    
    # 3. 测试访问受保护的API
    print("\n📝 Step 3: 测试访问受保护资源")
    try:
        response = session.get(f"{base_url}/api/user/profile")
        print(f"Profile状态码: {response.status_code}")
        print(f"Profile响应: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ 访问受保护资源成功")
        else:
            print("❌ 访问受保护资源失败")
            
    except Exception as e:
        print(f"Profile请求失败: {e}")
    
    # 4. 测试访问dashboard页面
    print("\n📝 Step 4: 测试访问dashboard页面")
    try:
        response = session.get(f"{base_url}/dashboard")
        print(f"Dashboard状态码: {response.status_code}")
        print(f"Dashboard重定向: {response.url}")
        
        if response.status_code == 200 and 'dashboard' in response.url:
            print("✅ 访问dashboard成功")
        else:
            print("❌ 访问dashboard失败")
            
    except Exception as e:
        print(f"Dashboard请求失败: {e}")

if __name__ == "__main__":
    test_complete_auth_flow()