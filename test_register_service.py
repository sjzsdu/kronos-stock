#!/usr/bin/env python3
"""
简化的注册API测试
"""

from app import create_app
from app.services.auth_service import AuthService

def test_register_service():
    """直接测试注册服务"""
    app = create_app('development')
    
    with app.app_context():
        print("🔍 测试AuthService.register_user方法...")
        
        # 测试数据
        email = 'test_direct@example.com'
        password = 'Test@123'
        full_name = '测试用户'
        nickname = 'testuser'
        
        try:
            result = AuthService.register_user(email, password, full_name, nickname)
            print(f"注册结果: {result}")
            print(f"返回值数量: {len(result)}")
            
            if len(result) == 3:
                success, message, user = result
                print(f"成功: {success}")
                print(f"消息: {message}")
                print(f"用户: {user}")
            else:
                print(f"返回值数量异常: {len(result)}")
        except Exception as e:
            print(f"注册服务异常: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_register_service()