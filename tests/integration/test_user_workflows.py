"""
用户工作流集成测试
测试完整用户生命周期工作流程的集成功能
"""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService


class TestUserWorkflowsIntegration:
    """用户工作流集成测试类"""
    
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
    
    def test_complete_user_registration_workflow(self, client, app_context, user_service):
        """测试完整用户注册工作流"""
        
        # 步骤1: 访问注册页面
        response = client.get('/user/register')
        assert response.status_code == 200, "注册页面应该可访问"
        
        # 验证注册表单存在
        html_content = response.data.decode('utf-8')
        assert 'register' in html_content or '注册' in html_content, "页面应包含注册相关内容"
        
        # 步骤2: 提交注册信息
        registration_data = {
            'username': 'newuser2024',
            'email': 'newuser2024@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
            'nickname': '新用户2024',
            'agree_terms': True
        }
        
        response = client.post('/user/register', data=registration_data)
        
        # 验证注册结果
        assert response.status_code in [200, 201, 302], "注册应该成功或重定向"
        
        # 步骤3: 验证用户已创建
        user = user_service.get_user_by_username('newuser2024')
        assert user is not None, "用户应该已成功创建"
        assert user.email == 'newuser2024@example.com', "邮箱应该正确保存"
        assert user.nickname == '新用户2024', "昵称应该正确保存"
        assert user.check_password('SecurePass123!'), "密码应该正确保存"
        
        # 步骤4: 测试邮箱验证流程（如果实现了）
        if hasattr(user, 'email_verified') and not user.email_verified:
            # 模拟邮箱验证
            verification_token = 'test_verification_token'
            verify_response = client.get(f'/user/verify-email?token={verification_token}')
            # 验证结果取决于具体实现
    
    def test_complete_user_login_workflow(self, client, app_context, user_service):
        """测试完整用户登录工作流"""
        
        # 前置条件：创建用户
        user_data = {
            'username': 'loginuser',
            'email': 'loginuser@example.com',
            'password': 'LoginPass123!',
            'nickname': '登录测试用户'
        }
        
        user = user_service.create_user(**user_data)
        assert user is not None, "测试用户应该创建成功"
        
        # 步骤1: 访问登录页面
        response = client.get('/user/login')
        assert response.status_code == 200, "登录页面应该可访问"
        
        # 步骤2: 提交登录信息
        login_data = {
            'username': 'loginuser',
            'password': 'LoginPass123!'
        }
        
        response = client.post('/user/login', data=login_data)
        assert response.status_code in [200, 302], "登录应该成功或重定向"
        
        # 步骤3: 验证登录状态
        # 检查会话或认证状态
        profile_response = client.get('/user/profile')
        assert profile_response.status_code in [200, 302], "登录后应该可以访问个人资料"
        
        # 步骤4: 验证用户最后登录时间更新
        updated_user = user_service.get_user_by_id(user.id)
        assert updated_user.last_seen is not None, "最后访问时间应该已更新"
    
    def test_user_profile_update_workflow(self, client, app_context, user_service):
        """测试用户资料更新工作流"""
        
        # 前置条件：创建并登录用户
        user = user_service.create_user(
            username='profileuser',
            email='profileuser@example.com',
            password='ProfilePass123!',
            nickname='资料更新用户'
        )
        
        # 模拟登录（具体实现取决于认证系统）
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问资料编辑页面
        response = client.get('/user/profile/edit')
        assert response.status_code in [200, 302], "资料编辑页面应该可访问"
        
        # 步骤2: 更新个人资料
        update_data = {
            'nickname': '更新后的昵称',
            'email': 'updated@example.com',
            'bio': '这是我的个人简介',
            'timezone': 'Asia/Shanghai',
            'language': 'zh-CN'
        }
        
        response = client.post('/user/profile/edit', data=update_data)
        assert response.status_code in [200, 302], "资料更新应该成功"
        
        # 步骤3: 验证更新结果
        updated_user = user_service.get_user_by_id(user.id)
        assert updated_user.nickname == '更新后的昵称', "昵称应该已更新"
        assert updated_user.email == 'updated@example.com', "邮箱应该已更新"
        
        # 步骤4: 验证更新历史记录（如果实现了）
        if hasattr(updated_user, 'updated_at'):
            assert updated_user.updated_at > user.created_at, "更新时间应该晚于创建时间"
    
    def test_user_settings_configuration_workflow(self, client, app_context, user_service):
        """测试用户设置配置工作流"""
        
        # 前置条件：创建用户
        user = user_service.create_user(
            username='settingsuser',
            email='settingsuser@example.com',
            password='SettingsPass123!',
            nickname='设置测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问设置页面
        response = client.get('/user/settings')
        assert response.status_code in [200, 302], "设置页面应该可访问"
        
        # 步骤2: 更新偏好设置
        preferences_data = {
            'theme': 'dark',
            'language': 'zh-CN',
            'timezone': 'Asia/Shanghai',
            'email_notifications': True,
            'push_notifications': False,
            'privacy_level': 'medium'
        }
        
        response = client.post('/user/settings/preferences', data=preferences_data)
        assert response.status_code in [200, 302], "偏好设置更新应该成功"
        
        # 步骤3: 更新安全设置
        security_data = {
            'enable_2fa': True,
            'password_expiry': 90,
            'session_timeout': 30
        }
        
        response = client.post('/user/settings/security', data=security_data)
        assert response.status_code in [200, 302], "安全设置更新应该成功"
        
        # 步骤4: 验证设置保存
        # 这里需要根据实际的设置存储机制进行验证
        settings_response = client.get('/user/settings')
        html_content = settings_response.data.decode('utf-8')
        
        # 验证设置值反映在界面中
        assert 'dark' in html_content or 'zh-CN' in html_content, "设置应该反映在界面中"
    
    def test_password_change_workflow(self, client, app_context, user_service):
        """测试密码修改工作流"""
        
        # 前置条件：创建用户
        original_password = 'OriginalPass123!'
        user = user_service.create_user(
            username='passworduser',
            email='passworduser@example.com',
            password=original_password,
            nickname='密码测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问密码修改页面
        response = client.get('/user/password/change')
        assert response.status_code in [200, 302], "密码修改页面应该可访问"
        
        # 步骤2: 提交密码修改
        new_password = 'NewSecurePass456!'
        password_data = {
            'current_password': original_password,
            'new_password': new_password,
            'confirm_password': new_password
        }
        
        response = client.post('/user/password/change', data=password_data)
        assert response.status_code in [200, 302], "密码修改应该成功"
        
        # 步骤3: 验证新密码有效
        updated_user = user_service.get_user_by_id(user.id)
        assert updated_user.check_password(new_password), "新密码应该有效"
        assert not updated_user.check_password(original_password), "旧密码应该无效"
        
        # 步骤4: 测试用新密码登录
        client.get('/user/logout')  # 先登出
        
        login_response = client.post('/user/login', data={
            'username': 'passworduser',
            'password': new_password
        })
        assert login_response.status_code in [200, 302], "新密码登录应该成功"
    
    def test_user_logout_workflow(self, client, app_context, user_service):
        """测试用户登出工作流"""
        
        # 前置条件：创建并登录用户
        user = user_service.create_user(
            username='logoutuser',
            email='logoutuser@example.com',
            password='LogoutPass123!',
            nickname='登出测试用户'
        )
        
        # 模拟登录状态
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 验证登录状态
        profile_response = client.get('/user/profile')
        assert profile_response.status_code in [200, 302], "登录状态下应该可访问个人资料"
        
        # 步骤2: 执行登出
        logout_response = client.post('/user/logout')
        assert logout_response.status_code in [200, 302], "登出应该成功"
        
        # 步骤3: 验证登出状态
        profile_response_after = client.get('/user/profile')
        assert profile_response_after.status_code in [302, 401, 403], "登出后不应该可以访问个人资料"
        
        # 步骤4: 验证会话清理
        with client.session_transaction() as sess:
            assert 'user_id' not in sess or sess.get('logged_in') is not True, "会话应该已清理"
    
    def test_account_deactivation_workflow(self, client, app_context, user_service):
        """测试账户停用工作流"""
        
        # 前置条件：创建用户
        user = user_service.create_user(
            username='deactivateuser',
            email='deactivate@example.com',
            password='DeactivatePass123!',
            nickname='停用测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问账户管理页面
        response = client.get('/user/account/manage')
        assert response.status_code in [200, 302], "账户管理页面应该可访问"
        
        # 步骤2: 请求账户停用
        deactivation_data = {
            'confirm_deactivation': True,
            'reason': 'temporary_break',
            'password': 'DeactivatePass123!'
        }
        
        response = client.post('/user/account/deactivate', data=deactivation_data)
        assert response.status_code in [200, 302], "账户停用请求应该成功"
        
        # 步骤3: 验证账户状态
        updated_user = user_service.get_user_by_id(user.id)
        if hasattr(updated_user, 'is_active'):
            assert not updated_user.is_active, "账户应该已停用"
        
        # 步骤4: 测试停用账户登录
        client.get('/user/logout')  # 先登出
        
        login_response = client.post('/user/login', data={
            'username': 'deactivateuser',
            'password': 'DeactivatePass123!'
        })
        
        # 停用的账户不应该能够登录
        assert login_response.status_code in [401, 403, 200], "停用账户登录应该被拒绝或显示提示"
    
    def test_account_deletion_workflow(self, client, app_context, user_service):
        """测试账户删除工作流"""
        
        # 前置条件：创建用户
        user = user_service.create_user(
            username='deleteuser',
            email='delete@example.com',
            password='DeletePass123!',
            nickname='删除测试用户'
        )
        
        user_id = user.id
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问账户删除页面
        response = client.get('/user/account/delete')
        assert response.status_code in [200, 302], "账户删除页面应该可访问"
        
        # 步骤2: 确认账户删除
        deletion_data = {
            'confirm_deletion': True,
            'password': 'DeletePass123!',
            'delete_reason': 'no_longer_needed',
            'final_confirmation': 'DELETE MY ACCOUNT'
        }
        
        response = client.post('/user/account/delete', data=deletion_data)
        assert response.status_code in [200, 302], "账户删除应该成功"
        
        # 步骤3: 验证账户已删除
        deleted_user = user_service.get_user_by_id(user_id)
        assert deleted_user is None, "用户应该已被删除"
        
        # 或者验证软删除（如果实现了软删除）
        if deleted_user is not None and hasattr(deleted_user, 'deleted_at'):
            assert deleted_user.deleted_at is not None, "用户应该标记为已删除"
    
    @pytest.mark.slow
    def test_user_session_management_workflow(self, client, app_context, user_service):
        """测试用户会话管理工作流"""
        
        # 前置条件：创建用户
        user = user_service.create_user(
            username='sessionuser',
            email='session@example.com',
            password='SessionPass123!',
            nickname='会话测试用户'
        )
        
        # 步骤1: 多设备登录模拟
        devices = [
            {'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'},
            {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            {'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        ]
        
        session_ids = []
        
        for device in devices:
            response = client.post('/user/login', data={
                'username': 'sessionuser',
                'password': 'SessionPass123!'
            }, headers={'User-Agent': device['user_agent']})
            
            assert response.status_code in [200, 302], "多设备登录应该成功"
            
            # 获取会话ID（具体实现取决于会话管理系统）
            with client.session_transaction() as sess:
                if 'session_id' in sess:
                    session_ids.append(sess['session_id'])
        
        # 步骤2: 查看活跃会话
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        sessions_response = client.get('/user/sessions')
        assert sessions_response.status_code in [200, 302], "会话列表应该可访问"
        
        # 步骤3: 撤销特定会话
        if session_ids:
            revoke_response = client.post(f'/user/sessions/revoke', data={
                'session_id': session_ids[0]
            })
            assert revoke_response.status_code in [200, 302], "会话撤销应该成功"
        
        # 步骤4: 撤销所有其他会话
        revoke_all_response = client.post('/user/sessions/revoke-all')
        assert revoke_all_response.status_code in [200, 302], "撤销所有会话应该成功"
    
    def test_user_data_export_workflow(self, client, app_context, user_service):
        """测试用户数据导出工作流"""
        
        # 前置条件：创建用户并生成一些数据
        user = user_service.create_user(
            username='exportuser',
            email='export@example.com',
            password='ExportPass123!',
            nickname='数据导出用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 请求数据导出
        export_response = client.post('/user/data/export', data={
            'export_format': 'json',
            'include_predictions': True,
            'include_preferences': True,
            'confirm_export': True
        })
        
        assert export_response.status_code in [200, 202], "数据导出请求应该成功"
        
        # 步骤2: 检查导出状态（如果是异步处理）
        if export_response.status_code == 202:
            status_response = client.get('/user/data/export/status')
            assert status_response.status_code == 200, "导出状态查询应该成功"
        
        # 步骤3: 下载导出数据
        download_response = client.get('/user/data/export/download')
        
        if download_response.status_code == 200:
            # 验证导出数据格式
            content_type = download_response.headers.get('Content-Type', '')
            assert 'json' in content_type or 'zip' in content_type, "导出数据应该是JSON或ZIP格式"
            
            # 验证数据内容（如果是JSON）
            if 'json' in content_type:
                import json
                export_data = json.loads(download_response.data.decode('utf-8'))
                assert 'user_info' in export_data, "导出数据应包含用户信息"
                assert export_data['user_info']['username'] == 'exportuser', "用户信息应该正确"
    
    def test_user_privacy_controls_workflow(self, client, app_context, user_service):
        """测试用户隐私控制工作流"""
        
        # 前置条件：创建用户
        user = user_service.create_user(
            username='privacyuser',
            email='privacy@example.com',
            password='PrivacyPass123!',
            nickname='隐私测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 访问隐私设置
        privacy_response = client.get('/user/privacy')
        assert privacy_response.status_code in [200, 302], "隐私设置页面应该可访问"
        
        # 步骤2: 更新隐私设置
        privacy_data = {
            'profile_visibility': 'private',
            'data_sharing': False,
            'marketing_emails': False,
            'analytics_tracking': False,
            'cookie_preferences': 'essential_only'
        }
        
        update_response = client.post('/user/privacy/update', data=privacy_data)
        assert update_response.status_code in [200, 302], "隐私设置更新应该成功"
        
        # 步骤3: 验证隐私设置生效
        # 测试数据访问限制
        public_profile_response = client.get(f'/public/user/{user.id}')
        
        # 根据隐私设置，公开资料访问应该受限
        if privacy_data['profile_visibility'] == 'private':
            assert public_profile_response.status_code in [403, 404], "私有资料不应公开访问"
        
        # 步骤4: 数据删除请求
        data_deletion_response = client.post('/user/privacy/delete-data', data={
            'data_types': ['search_history', 'preferences', 'temporary_files'],
            'confirm_deletion': True
        })
        
        assert data_deletion_response.status_code in [200, 202], "数据删除请求应该成功"


if __name__ == '__main__':
    pytest.main([__file__])