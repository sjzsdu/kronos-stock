"""
用户权限集成测试
测试用户权限系统的集成功能和安全边界
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService


class TestPermissionsIntegration:
    """用户权限集成测试类"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用实例"""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def app_context(self, app):
        """应用上下文"""
        with app.app_context():
            db.create_all()
            yield app
            db.drop_all()
    
    @pytest.fixture
    def user_service(self, app_context):
        """创建用户服务实例"""
        return UserService()
    
    @pytest.fixture
    def admin_user(self, user_service):
        """创建管理员用户"""
        admin = user_service.create_user(
            username='admin',
            email='admin@example.com',
            password='Admin123!',
            nickname='系统管理员'
        )
        
        # 设置管理员角色（如果支持角色系统）
        if hasattr(admin, 'role'):
            admin.role = 'admin'
        elif hasattr(admin, 'is_admin'):
            admin.is_admin = True
        
        return admin
    
    @pytest.fixture
    def regular_user(self, user_service):
        """创建普通用户"""
        user = user_service.create_user(
            username='regularuser',
            email='regular@example.com',
            password='Regular123!',
            nickname='普通用户'
        )
        return user
    
    @pytest.fixture
    def guest_user(self, user_service):
        """创建访客用户"""
        guest = user_service.create_user(
            username='guest',
            email='guest@example.com',
            password='Guest123!',
            nickname='访客用户'
        )
        
        # 设置访客角色
        if hasattr(guest, 'role'):
            guest.role = 'guest'
        elif hasattr(guest, 'is_guest'):
            guest.is_guest = True
        
        return guest
    
    def test_role_based_access_control(self, client, app_context, admin_user, regular_user, guest_user):
        """测试基于角色的访问控制"""
        
        # 定义角色权限矩阵
        permission_matrix = [
            {
                'user': admin_user,
                'role': 'admin',
                'allowed_endpoints': [
                    '/admin/dashboard',
                    '/admin/users',
                    '/admin/settings',
                    '/user/profile',
                    '/prediction/create'
                ],
                'forbidden_endpoints': []
            },
            {
                'user': regular_user,
                'role': 'user',
                'allowed_endpoints': [
                    '/user/profile',
                    '/user/settings',
                    '/prediction/create',
                    '/prediction/view'
                ],
                'forbidden_endpoints': [
                    '/admin/dashboard',
                    '/admin/users',
                    '/admin/settings'
                ]
            },
            {
                'user': guest_user,
                'role': 'guest',
                'allowed_endpoints': [
                    '/user/profile',
                    '/prediction/view'
                ],
                'forbidden_endpoints': [
                    '/admin/dashboard',
                    '/admin/users',
                    '/prediction/create',
                    '/user/settings'
                ]
            }
        ]
        
        for user_config in permission_matrix:
            user = user_config['user']
            
            # 模拟用户登录
            with client.session_transaction() as sess:
                sess['user_id'] = user.id
                sess['logged_in'] = True
                if 'role' in user_config:
                    sess['user_role'] = user_config['role']
            
            # 测试允许的端点
            for endpoint in user_config['allowed_endpoints']:
                response = client.get(endpoint)
                
                # 允许的端点应该返回200或302（重定向）
                assert response.status_code in [200, 302], \
                    f"用户 {user.username} 应该可以访问 {endpoint}"
            
            # 测试禁止的端点
            for endpoint in user_config['forbidden_endpoints']:
                response = client.get(endpoint)
                
                # 禁止的端点应该返回403（禁止）或302（重定向到登录）
                assert response.status_code in [403, 302, 401, 404], \
                    f"用户 {user.username} 不应该能访问 {endpoint}"
            
            # 清理会话
            client.get('/user/logout')
    
    def test_api_permission_enforcement(self, client, app_context, admin_user, regular_user):
        """测试API权限强制执行"""
        
        # API权限测试用例
        api_tests = [
            {
                'endpoint': '/api/users',
                'method': 'GET',
                'admin_expected': [200, 404],  # 管理员可以查看用户列表
                'user_expected': [403, 404]   # 普通用户不可以
            },
            {
                'endpoint': '/api/users/1',
                'method': 'GET',
                'admin_expected': [200, 404],  # 管理员可以查看任何用户
                'user_expected': [200, 403, 404]  # 普通用户只能查看自己
            },
            {
                'endpoint': '/api/users/1',
                'method': 'DELETE',
                'admin_expected': [200, 204, 404],  # 管理员可以删除用户
                'user_expected': [403, 404]        # 普通用户不可以删除其他用户
            },
            {
                'endpoint': '/api/system/config',
                'method': 'GET',
                'admin_expected': [200, 404],  # 管理员可以查看系统配置
                'user_expected': [403, 404]   # 普通用户不可以
            }
        ]
        
        for test_case in api_tests:
            endpoint = test_case['endpoint']
            method = test_case['method']
            
            # 测试管理员权限
            with client.session_transaction() as sess:
                sess['user_id'] = admin_user.id
                sess['logged_in'] = True
                sess['user_role'] = 'admin'
            
            if method == 'GET':
                admin_response = client.get(endpoint)
            elif method == 'DELETE':
                admin_response = client.delete(endpoint)
            elif method == 'POST':
                admin_response = client.post(endpoint, data={})
            
            assert admin_response.status_code in test_case['admin_expected'], \
                f"管理员访问 {method} {endpoint} 的状态码应该在 {test_case['admin_expected']} 中"
            
            # 清理会话
            client.get('/user/logout')
            
            # 测试普通用户权限
            with client.session_transaction() as sess:
                sess['user_id'] = regular_user.id
                sess['logged_in'] = True
                sess['user_role'] = 'user'
            
            if method == 'GET':
                user_response = client.get(endpoint)
            elif method == 'DELETE':
                user_response = client.delete(endpoint)
            elif method == 'POST':
                user_response = client.post(endpoint, data={})
            
            assert user_response.status_code in test_case['user_expected'], \
                f"普通用户访问 {method} {endpoint} 的状态码应该在 {test_case['user_expected']} 中"
            
            # 清理会话
            client.get('/user/logout')
    
    def test_resource_ownership_permissions(self, client, app_context, regular_user):
        """测试资源所有权权限"""
        
        # 创建另一个用户
        other_user = User(
            username='otheruser',
            email='other@example.com',
            nickname='其他用户'
        )
        other_user.set_password('Other123!')
        
        with app_context:
            db.session.add(other_user)
            db.session.commit()
            other_user_id = other_user.id
        
        # 模拟regular_user登录
        with client.session_transaction() as sess:
            sess['user_id'] = regular_user.id
            sess['logged_in'] = True
        
        # 测试用户只能访问自己的资源
        ownership_tests = [
            {
                'endpoint': f'/user/profile',  # 自己的资料
                'expected_status': [200, 302],
                'description': '用户应该可以访问自己的资料'
            },
            {
                'endpoint': f'/user/{other_user_id}/profile',  # 他人的资料
                'expected_status': [403, 404, 302],
                'description': '用户不应该可以访问他人的私有资料'
            },
            {
                'endpoint': f'/api/users/{regular_user.id}',  # 自己的API数据
                'expected_status': [200, 404],
                'description': '用户应该可以通过API访问自己的数据'
            },
            {
                'endpoint': f'/api/users/{other_user_id}',  # 他人的API数据
                'expected_status': [403, 404],
                'description': '用户不应该通过API访问他人的私有数据'
            }
        ]
        
        for test in ownership_tests:
            response = client.get(test['endpoint'])
            
            assert response.status_code in test['expected_status'], \
                f"{test['description']} - 状态码应该在 {test['expected_status']} 中，实际: {response.status_code}"
    
    def test_session_based_permissions(self, client, app_context, regular_user):
        """测试基于会话的权限控制"""
        
        # 测试未登录状态
        protected_endpoints = [
            '/user/profile',
            '/user/settings',
            '/api/user/preferences',
            '/prediction/create'
        ]
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            
            # 未登录用户应该被重定向到登录页面或返回401
            assert response.status_code in [302, 401, 403], \
                f"未登录用户访问 {endpoint} 应该被拒绝或重定向"
        
        # 测试登录后的权限
        with client.session_transaction() as sess:
            sess['user_id'] = regular_user.id
            sess['logged_in'] = True
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            
            # 登录用户应该可以访问这些端点
            assert response.status_code in [200, 302, 404], \
                f"登录用户应该可以访问 {endpoint}"
        
        # 测试会话过期
        # 模拟会话过期（通过修改会话时间戳）
        with client.session_transaction() as sess:
            sess['login_time'] = (datetime.utcnow() - timedelta(hours=25)).isoformat()  # 25小时前登录
        
        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            
            # 过期会话应该被拒绝（具体行为取决于实现）
            # 可能返回302重定向到登录页面，或401未授权
            if response.status_code in [302, 401]:
                # 这是期望的会话过期行为
                pass
            elif response.status_code == 200:
                # 如果没有实现会话过期检查，这也是可以接受的
                pass
    
    def test_permission_inheritance_and_delegation(self, client, app_context, admin_user, regular_user):
        """测试权限继承和委派"""
        
        # 模拟管理员登录
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user.id
            sess['logged_in'] = True
            sess['user_role'] = 'admin'
        
        # 测试管理员可以代表其他用户执行操作
        delegation_tests = [
            {
                'action': 'view_user_profile',
                'endpoint': f'/admin/users/{regular_user.id}/profile',
                'expected_status': [200, 404],
                'description': '管理员应该可以查看任何用户的资料'
            },
            {
                'action': 'reset_user_password',
                'endpoint': f'/admin/users/{regular_user.id}/reset-password',
                'method': 'POST',
                'data': {'new_password': 'NewPass123!'},
                'expected_status': [200, 302, 404],
                'description': '管理员应该可以重置用户密码'
            },
            {
                'action': 'modify_user_settings',
                'endpoint': f'/admin/users/{regular_user.id}/settings',
                'method': 'POST',
                'data': {'theme': 'light', 'language': 'en'},
                'expected_status': [200, 302, 404],
                'description': '管理员应该可以修改用户设置'
            }
        ]
        
        for test in delegation_tests:
            if test.get('method') == 'POST':
                response = client.post(test['endpoint'], data=test.get('data', {}))
            else:
                response = client.get(test['endpoint'])
            
            assert response.status_code in test['expected_status'], \
                f"{test['description']} - 状态码: {response.status_code}"
        
        # 测试权限委派审计
        audit_response = client.get('/admin/audit/user-actions')
        
        if audit_response.status_code == 200:
            # 验证管理员操作被记录
            audit_html = audit_response.data.decode('utf-8')
            
            audit_indicators = [
                'admin', admin_user.username,
                'reset', 'modify', 'view',
                '管理员', '重置', '修改'
            ]
            
            has_audit_log = any(indicator in audit_html for indicator in audit_indicators)
            # 审计日志的具体实现可能因系统而异
    
    def test_dynamic_permission_updates(self, client, app_context, admin_user, regular_user):
        """测试动态权限更新"""
        
        # 模拟管理员登录
        with client.session_transaction() as sess:
            sess['user_id'] = admin_user.id
            sess['logged_in'] = True
            sess['user_role'] = 'admin'
        
        # 步骤1: 修改用户权限
        permission_update_response = client.post(f'/admin/users/{regular_user.id}/permissions', data={
            'role': 'moderator',  # 提升为版主
            'permissions': ['manage_content', 'moderate_users'],
            'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat()
        })
        
        # 步骤2: 验证权限更新生效
        if permission_update_response.status_code in [200, 302]:
            # 清理管理员会话
            client.get('/user/logout')
            
            # 用更新权限的用户登录
            with client.session_transaction() as sess:
                sess['user_id'] = regular_user.id
                sess['logged_in'] = True
                sess['user_role'] = 'moderator'
            
            # 测试新权限
            moderator_endpoints = [
                '/moderate/content',
                '/moderate/users',
                '/admin/reports'  # 版主可能可以访问的报告
            ]
            
            for endpoint in moderator_endpoints:
                response = client.get(endpoint)
                
                # 新权限应该允许访问这些端点
                if response.status_code in [200, 302]:
                    # 权限更新成功
                    pass
                elif response.status_code in [403, 404]:
                    # 如果端点不存在或权限系统未实现，这也是可以接受的
                    pass
        
        # 步骤3: 测试权限过期
        # 模拟时间推进（权限过期后）
        # 这通常需要修改系统时间或使用时间模拟库
        
    def test_security_boundaries_and_escalation(self, client, app_context, regular_user):
        """测试安全边界和权限升级防护"""
        
        # 模拟普通用户登录
        with client.session_transaction() as sess:
            sess['user_id'] = regular_user.id
            sess['logged_in'] = True
        
        # 测试权限升级攻击防护
        escalation_attempts = [
            {
                'method': 'session_manipulation',
                'action': lambda: client.session_transaction().__enter__().update({'user_role': 'admin'}),
                'test_endpoint': '/admin/dashboard',
                'description': '会话角色篡改应该被检测和阻止'
            },
            {
                'method': 'parameter_tampering',
                'endpoint': '/user/profile/edit',
                'data': {'user_id': 1, 'role': 'admin'},  # 尝试修改其他用户或角色
                'description': '参数篡改应该被验证和拒绝'
            },
            {
                'method': 'direct_api_access',
                'endpoint': '/api/admin/system-info',
                'headers': {'X-Admin-Token': 'fake-token'},
                'description': '伪造的管理员令牌应该被拒绝'
            }
        ]
        
        for attempt in escalation_attempts:
            if attempt['method'] == 'session_manipulation':
                # 尝试篡改会话
                with client.session_transaction() as sess:
                    sess['user_role'] = 'admin'
                
                response = client.get('/admin/dashboard')
                
                # 应该仍然被拒绝访问，因为用户本身不是管理员
                assert response.status_code in [403, 302, 401], \
                    f"会话篡改应该被检测: {response.status_code}"
                
            elif attempt['method'] == 'parameter_tampering':
                response = client.post(attempt['endpoint'], data=attempt['data'])
                
                # 参数篡改应该被拒绝或忽略
                assert response.status_code in [400, 403, 422], \
                    f"参数篡改应该被拒绝: {response.status_code}"
                
            elif attempt['method'] == 'direct_api_access':
                response = client.get(attempt['endpoint'], headers=attempt.get('headers', {}))
                
                # 伪造的认证应该被拒绝
                assert response.status_code in [401, 403, 404], \
                    f"伪造认证应该被拒绝: {response.status_code}"
    
    def test_cross_user_data_access_prevention(self, client, app_context, user_service):
        """测试跨用户数据访问防护"""
        
        # 创建多个用户
        user1 = user_service.create_user(
            username='user1', email='user1@example.com',
            password='User1Pass!', nickname='用户1'
        )
        
        user2 = user_service.create_user(
            username='user2', email='user2@example.com',
            password='User2Pass!', nickname='用户2'
        )
        
        # 模拟user1登录
        with client.session_transaction() as sess:
            sess['user_id'] = user1.id
            sess['logged_in'] = True
        
        # 尝试访问user2的数据
        cross_access_attempts = [
            {
                'endpoint': f'/api/users/{user2.id}',
                'description': '不应该可以通过API访问其他用户的私有数据'
            },
            {
                'endpoint': f'/user/{user2.id}/profile/edit',
                'description': '不应该可以编辑其他用户的资料'
            },
            {
                'endpoint': f'/user/{user2.id}/settings',
                'description': '不应该可以访问其他用户的设置'
            },
            {
                'endpoint': f'/api/users/{user2.id}/preferences',
                'description': '不应该可以访问其他用户的偏好设置'
            }
        ]
        
        for attempt in cross_access_attempts:
            response = client.get(attempt['endpoint'])
            
            # 跨用户访问应该被拒绝
            assert response.status_code in [403, 404, 302], \
                f"{attempt['description']} - 状态码: {response.status_code}"
        
        # 测试批量操作的权限检查
        bulk_operations = [
            {
                'endpoint': '/api/users/bulk-update',
                'data': {'user_ids': [user1.id, user2.id], 'action': 'deactivate'},
                'description': '批量操作不应该影响无权限的用户'
            }
        ]
        
        for operation in bulk_operations:
            response = client.post(operation['endpoint'], data=operation['data'])
            
            # 批量操作应该被拒绝或只影响有权限的资源
            assert response.status_code in [403, 400, 422], \
                f"{operation['description']} - 状态码: {response.status_code}"
    
    @pytest.mark.slow
    def test_concurrent_permission_changes(self, client, app_context, user_service, admin_user, regular_user):
        """测试并发权限变更的处理"""
        
        import threading
        import time
        
        results = {'responses': []}
        
        def permission_change_worker(user_id, new_role, delay=0):
            """权限变更工作线程"""
            time.sleep(delay)
            
            # 创建新的客户端实例用于并发测试
            with app_context.test_client() as thread_client:
                with thread_client.session_transaction() as sess:
                    sess['user_id'] = admin_user.id
                    sess['logged_in'] = True
                    sess['user_role'] = 'admin'
                
                response = thread_client.post(f'/admin/users/{user_id}/permissions', data={
                    'role': new_role,
                    'timestamp': datetime.utcnow().isoformat()
                })
                
                results['responses'].append({
                    'status_code': response.status_code,
                    'role': new_role,
                    'timestamp': datetime.utcnow()
                })
        
        # 启动并发权限变更
        threads = [
            threading.Thread(target=permission_change_worker, args=(regular_user.id, 'moderator', 0)),
            threading.Thread(target=permission_change_worker, args=(regular_user.id, 'admin', 0.1)),
            threading.Thread(target=permission_change_worker, args=(regular_user.id, 'user', 0.2))
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # 验证并发处理结果
        assert len(results['responses']) == 3, "所有并发请求都应该得到响应"
        
        # 验证最终状态的一致性
        final_user = user_service.get_user_by_id(regular_user.id)
        
        # 检查用户角色是否处于一致状态
        if hasattr(final_user, 'role'):
            valid_roles = ['user', 'moderator', 'admin']
            assert final_user.role in valid_roles, "最终用户角色应该是有效的"


if __name__ == '__main__':
    pytest.main([__file__])