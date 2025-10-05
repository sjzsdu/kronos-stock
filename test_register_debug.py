#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试注册API的测试脚本
"""

import requests
import json

def test_register_api():
    """测试注册API"""
    url = "http://localhost:5001/api/auth/register"
    
    # 测试数据
    test_data = {
        'nickname': 'sjzsdu',
        'email': 'juzhong@magicloud.io',
        'password': 'Magic@2025',
        'confirm_password': 'Magic@2025',
        'agree_terms': 'on'
    }
    
    print("🔍 测试注册API...")
    print(f"URL: {url}")
    print(f"Data: {test_data}")
    
    # 测试1: 使用表单数据
    print("\n📝 测试1: 表单数据提交")
    try:
        response = requests.post(
            url, 
            data=test_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试2: 使用JSON数据
    print("\n📝 测试2: JSON数据提交")
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_register_api()