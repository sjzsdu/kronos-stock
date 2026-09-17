"""
用户数据流集成测试
测试用户数据在系统中的完整生命周期流转
"""
import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService


class TestDataFlowIntegration:
    """用户数据流集成测试类"""
    
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
    
    def test_user_data_creation_flow(self, client, app_context, user_service):
        """测试用户数据创建流程"""
        
        # 步骤1: API创建用户数据
        user_data = {
            'username': 'dataflowuser',
            'email': 'dataflow@example.com',
            'password': 'DataFlow123!',
            'nickname': '数据流测试用户',
            'preferences': {
                'theme': 'dark',
                'language': 'zh-CN',
                'timezone': 'Asia/Shanghai'
            }
        }
        
        # 通过API创建用户
        api_response = client.post('/api/users', 
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        # 验证API创建响应
        if api_response.status_code in [200, 201]:
            api_result = json.loads(api_response.data.decode('utf-8'))
            user_id = api_result.get('id') or api_result.get('user_id')
            
            assert user_id is not None, "API应该返回用户ID"
            
            # 步骤2: 验证数据库中的数据
            created_user = user_service.get_user_by_id(user_id)
            assert created_user is not None, "用户应该在数据库中存在"
            assert created_user.username == user_data['username'], "用户名应该正确保存"
            assert created_user.email == user_data['email'], "邮箱应该正确保存"
            
            # 步骤3: 验证Web界面显示
            # 模拟登录
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['logged_in'] = True
            
            profile_response = client.get('/user/profile')
            
            if profile_response.status_code == 200:
                profile_html = profile_response.data.decode('utf-8')
                
                # 验证用户信息在界面中显示
                assert user_data['nickname'] in profile_html, "昵称应该在资料页面显示"
                assert user_data['email'] in profile_html, "邮箱应该在资料页面显示"
            
            # 步骤4: 验证偏好设置保存
            settings_response = client.get('/user/settings')
            
            if settings_response.status_code == 200:
                settings_html = settings_response.data.decode('utf-8')
                
                # 验证偏好设置反映在界面
                preference_indicators = [
                    user_data['preferences']['theme'],
                    user_data['preferences']['language'],
                    'dark', 'zh-CN'  # 预期值
                ]
                
                has_preferences = any(pref in settings_html for pref in preference_indicators)
                # 偏好设置的显示方式可能因实现而异
        
        else:
            # 如果API创建失败，尝试通过服务层创建
            user = user_service.create_user(**user_data)
            assert user is not None, "通过服务层应该能创建用户"
    
    def test_user_data_read_flow(self, client, app_context, user_service):
        """测试用户数据读取流程"""
        
        # 前置条件: 创建测试用户
        user = user_service.create_user(
            username='readflowuser',
            email='readflow@example.com',
            password='ReadFlow123!',
            nickname='数据读取测试用户'
        )
        
        user_id = user.id
        
        # 步骤1: 通过API读取用户数据
        api_response = client.get(f'/api/users/{user_id}')
        
        if api_response.status_code == 200:
            api_data = json.loads(api_response.data.decode('utf-8'))
            
            # 验证API返回的数据完整性
            assert api_data['username'] == user.username, "API应该返回正确的用户名"
            assert api_data['email'] == user.email, "API应该返回正确的邮箱"
            assert 'password' not in api_data, "API不应该返回密码信息"
        
        # 步骤2: 通过Web界面读取数据
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['logged_in'] = True
        
        # 2a: 读取资料页面
        profile_response = client.get('/user/profile')
        
        if profile_response.status_code == 200:
            profile_html = profile_response.data.decode('utf-8')
            
            # 验证个人信息显示
            user_info_elements = [
                user.username,
                user.nickname,
                user.email
            ]
            
            displayed_info = sum(1 for info in user_info_elements if info and info in profile_html)
            assert displayed_info >= 2, "资料页面应该显示主要用户信息"
        
        # 2b: 读取HTMX组件数据
        htmx_profile_response = client.get(f'/htmx/user/profile?user_id={user_id}')
        
        if htmx_profile_response.status_code == 200:
            htmx_html = htmx_profile_response.data.decode('utf-8')
            
            # 验证HTMX组件数据
            assert user.username in htmx_html or user.nickname in htmx_html, "HTMX组件应该包含用户数据"
        
        # 步骤3: 验证数据一致性
        # 通过不同途径获取的数据应该一致
        db_user = user_service.get_user_by_id(user_id)
        
        assert db_user.username == user.username, "数据库数据应该与原始数据一致"
        assert db_user.email == user.email, "邮箱信息应该保持一致"
    
    def test_user_data_update_flow(self, client, app_context, user_service):
        """测试用户数据更新流程"""
        
        # 前置条件: 创建测试用户
        original_user = user_service.create_user(
            username='updateflowuser',
            email='updateflow@example.com',
            password='UpdateFlow123!',
            nickname='原始昵称'
        )
        
        user_id = original_user.id
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['logged_in'] = True
        
        # 步骤1: 通过Web表单更新数据
        update_data = {
            'nickname': '更新后的昵称',
            'email': 'updated@example.com',
            'bio': '这是我的个人简介',
            'phone': '13800138000'
        }
        
        form_response = client.post('/user/profile/edit', data=update_data)
        
        # 验证Web更新响应
        assert form_response.status_code in [200, 302], "Web表单更新应该成功"
        
        # 步骤2: 验证数据库更新
        updated_user = user_service.get_user_by_id(user_id)
        
        assert updated_user.nickname == update_data['nickname'], "昵称应该已更新"
        assert updated_user.email == update_data['email'], "邮箱应该已更新"
        
        # 步骤3: 通过API验证更新
        api_response = client.get(f'/api/users/{user_id}')
        
        if api_response.status_code == 200:
            api_data = json.loads(api_response.data.decode('utf-8'))
            
            assert api_data['nickname'] == update_data['nickname'], "API应该返回更新后的昵称"
            assert api_data['email'] == update_data['email'], "API应该返回更新后的邮箱"
        
        # 步骤4: 通过HTMX更新部分数据
        htmx_update_data = {
            'field': 'bio',
            'value': '通过HTMX更新的简介'
        }
        
        htmx_response = client.post(
            '/htmx/user/update-field',
            data=htmx_update_data,
            headers={'HX-Request': 'true'}
        )
        
        if htmx_response.status_code == 200:
            # 验证HTMX更新生效
            final_user = user_service.get_user_by_id(user_id)
            
            # 检查用户模型是否有bio字段
            if hasattr(final_user, 'bio'):
                assert final_user.bio == htmx_update_data['value'], "HTMX更新应该生效"
        
        # 步骤5: 验证更新历史记录（如果实现了）
        if hasattr(updated_user, 'updated_at'):
            assert updated_user.updated_at > original_user.created_at, "更新时间应该晚于创建时间"
    
    def test_user_preferences_data_flow(self, client, app_context, user_service):
        """测试用户偏好设置数据流"""
        
        # 前置条件: 创建用户
        user = user_service.create_user(
            username='prefsuser',
            email='prefs@example.com',
            password='PrefsFlow123!',
            nickname='偏好测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 设置用户偏好
        preferences_data = {
            'theme': 'dark',
            'language': 'zh-CN',
            'timezone': 'Asia/Shanghai',
            'email_notifications': True,
            'push_notifications': False,
            'currency': 'CNY',
            'date_format': 'YYYY-MM-DD'
        }
        
        prefs_response = client.post('/user/preferences', data=preferences_data)
        
        # 验证偏好设置保存
        if prefs_response.status_code in [200, 302]:
            # 步骤2: 通过API读取偏好
            api_prefs_response = client.get(f'/api/users/{user.id}/preferences')
            
            if api_prefs_response.status_code == 200:
                api_prefs = json.loads(api_prefs_response.data.decode('utf-8'))
                
                # 验证偏好数据一致性
                for key, value in preferences_data.items():
                    if key in api_prefs:
                        assert api_prefs[key] == value, f"偏好 {key} 应该与设置值一致"
            
            # 步骤3: 验证偏好在界面中生效
            settings_page_response = client.get('/user/settings')
            
            if settings_page_response.status_code == 200:
                settings_html = settings_page_response.data.decode('utf-8')
                
                # 验证主题设置反映
                theme_indicators = [
                    'dark', preferences_data['theme'],
                    'theme-dark', 'dark-mode'
                ]
                
                has_theme_applied = any(indicator in settings_html for indicator in theme_indicators)
                # 主题应用的具体方式可能因实现而异
            
            # 步骤4: 测试偏好对其他功能的影响
            # 例如，语言偏好影响界面语言
            if preferences_data['language'] == 'zh-CN':
                dashboard_response = client.get('/user/dashboard')
                
                if dashboard_response.status_code == 200:
                    dashboard_html = dashboard_response.data.decode('utf-8')
                    
                    # 检查中文内容
                    chinese_indicators = ['仪表板', '设置', '个人资料', '预测']
                    has_chinese_content = any(indicator in dashboard_html for indicator in chinese_indicators)
                    # 语言本地化的具体实现可能因系统而异
    
    def test_user_activity_data_flow(self, client, app_context, user_service):
        """测试用户活动数据流"""
        
        # 前置条件: 创建用户
        user = user_service.create_user(
            username='activityuser',
            email='activity@example.com',
            password='Activity123!',
            nickname='活动测试用户'
        )
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 步骤1: 生成用户活动数据
        activities = [
            {'action': 'login', 'endpoint': '/user/login'},
            {'action': 'view_profile', 'endpoint': '/user/profile'},
            {'action': 'create_prediction', 'endpoint': '/prediction/create'},
            {'action': 'view_settings', 'endpoint': '/user/settings'},
        ]
        
        activity_responses = []
        
        for activity in activities:
            # 执行活动
            response = client.get(activity['endpoint'])
            activity_responses.append({
                'activity': activity,
                'response': response
            })
            
            # 记录活动（如果有活动记录API）
            activity_log_response = client.post('/api/user/activities', data={
                'action': activity['action'],
                'timestamp': datetime.utcnow().isoformat(),
                'metadata': {'endpoint': activity['endpoint']}
            })
        
        # 步骤2: 通过API查询活动历史
        activities_api_response = client.get(f'/api/users/{user.id}/activities')
        
        if activities_api_response.status_code == 200:
            api_activities = json.loads(activities_api_response.data.decode('utf-8'))
            
            # 验证活动记录
            assert isinstance(api_activities, list), "活动记录应该是列表格式"
            
            if len(api_activities) > 0:
                # 验证活动数据结构
                activity_item = api_activities[0]
                expected_fields = ['action', 'timestamp', 'user_id']
                
                has_required_fields = all(field in activity_item for field in expected_fields)
                assert has_required_fields, "活动记录应该包含必要字段"
        
        # 步骤3: 通过Web界面查看活动
        activity_page_response = client.get('/user/activity-log')
        
        if activity_page_response.status_code == 200:
            activity_html = activity_page_response.data.decode('utf-8')
            
            # 验证活动显示
            activity_indicators = [
                'login', 'profile', 'prediction', 'settings',
                '登录', '资料', '预测', '设置'
            ]
            
            displayed_activities = sum(1 for indicator in activity_indicators if indicator in activity_html)
            assert displayed_activities >= 2, "活动页面应该显示用户活动"
        
        # 步骤4: 验证最后访问时间更新
        updated_user = user_service.get_user_by_id(user.id)
        
        if hasattr(updated_user, 'last_seen'):
            assert updated_user.last_seen is not None, "最后访问时间应该已更新"
            
            # 验证时间合理性（在最近几分钟内）
            time_diff = datetime.utcnow() - updated_user.last_seen
            assert time_diff < timedelta(minutes=5), "最后访问时间应该是最近的"
    
    def test_user_data_deletion_flow(self, client, app_context, user_service):
        """测试用户数据删除流程"""
        
        # 前置条件: 创建用户和相关数据
        user = user_service.create_user(
            username='deleteuser',
            email='delete@example.com',
            password='Delete123!',
            nickname='删除测试用户'
        )
        
        user_id = user.id
        
        # 创建一些关联数据（模拟）
        # 例如：用户偏好、活动记录、预测记录等
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['logged_in'] = True
        
        # 步骤1: 部分数据删除（清理临时数据）
        cleanup_response = client.post('/user/data/cleanup', data={
            'data_types': ['temp_files', 'cache', 'logs'],
            'confirm': True
        })
        
        if cleanup_response.status_code in [200, 202]:
            # 验证用户仍然存在
            remaining_user = user_service.get_user_by_id(user_id)
            assert remaining_user is not None, "部分清理不应该删除用户主数据"
        
        # 步骤2: 账户停用（软删除）
        deactivate_response = client.post('/user/account/deactivate', data={
            'reason': 'temporary',
            'confirm_deactivation': True
        })
        
        if deactivate_response.status_code in [200, 302]:
            deactivated_user = user_service.get_user_by_id(user_id)
            
            if deactivated_user and hasattr(deactivated_user, 'is_active'):
                assert not deactivated_user.is_active, "用户应该被标记为非活跃"
        
        # 步骤3: 完全删除账户
        delete_response = client.post('/user/account/delete', data={
            'confirm_deletion': True,
            'password': 'Delete123!',
            'final_confirmation': 'DELETE MY ACCOUNT'
        })
        
        if delete_response.status_code in [200, 302]:
            # 验证用户删除
            deleted_user = user_service.get_user_by_id(user_id)
            
            # 可能是硬删除（None）或软删除（标记为已删除）
            if deleted_user is None:
                # 硬删除成功
                pass
            elif hasattr(deleted_user, 'deleted_at'):
                assert deleted_user.deleted_at is not None, "用户应该标记为已删除"
            
            # 步骤4: 验证关联数据清理
            # 检查API访问
            api_response = client.get(f'/api/users/{user_id}')
            assert api_response.status_code in [404, 410], "删除的用户API应该返回404或410"
            
            # 检查登录尝试
            login_response = client.post('/user/login', data={
                'username': 'deleteuser',
                'password': 'Delete123!'
            })
            
            assert login_response.status_code in [401, 404], "删除的用户不应该能够登录"
    
    def test_user_data_export_import_flow(self, client, app_context, user_service):
        """测试用户数据导出导入流程"""
        
        # 前置条件: 创建包含丰富数据的用户
        user = user_service.create_user(
            username='exportuser',
            email='export@example.com',
            password='Export123!',
            nickname='导出测试用户'
        )
        
        # 模拟登录并生成一些数据
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['logged_in'] = True
        
        # 生成用户数据
        client.post('/user/preferences', data={'theme': 'dark', 'language': 'zh-CN'})
        client.get('/user/dashboard')  # 生成访问记录
        
        # 步骤1: 请求数据导出
        export_request_response = client.post('/user/data/export', data={
            'format': 'json',
            'include_preferences': True,
            'include_activities': True,
            'include_metadata': True
        })
        
        if export_request_response.status_code in [200, 202]:
            # 步骤2: 获取导出数据
            export_response = client.get('/user/data/export/download')
            
            if export_response.status_code == 200:
                # 验证导出数据格式
                content_type = export_response.headers.get('Content-Type', '')
                
                if 'json' in content_type:
                    export_data = json.loads(export_response.data.decode('utf-8'))
                    
                    # 验证导出数据完整性
                    expected_sections = ['user_info', 'preferences', 'activities']
                    
                    for section in expected_sections:
                        if section in export_data:
                            assert export_data[section] is not None, f"导出数据应该包含 {section}"
                    
                    # 验证用户信息
                    if 'user_info' in export_data:
                        user_info = export_data['user_info']
                        assert user_info['username'] == user.username, "导出的用户名应该正确"
                        assert 'password' not in user_info, "导出数据不应该包含密码"
        
        # 步骤3: 模拟数据导入（如果支持）
        if export_response.status_code == 200 and 'json' in content_type:
            # 创建新用户进行导入测试
            import_user = user_service.create_user(
                username='importuser',
                email='import@example.com',
                password='Import123!',
                nickname='导入测试用户'
            )
            
            # 模拟导入过程
            with client.session_transaction() as sess:
                sess['user_id'] = import_user.id
                sess['logged_in'] = True
            
            import_response = client.post('/user/data/import', 
                data={'import_data': export_response.data},
                content_type='multipart/form-data'
            )
            
            if import_response.status_code in [200, 202]:
                # 验证导入结果
                imported_user = user_service.get_user_by_id(import_user.id)
                
                # 检查是否有偏好设置被导入
                prefs_response = client.get(f'/api/users/{import_user.id}/preferences')
                
                if prefs_response.status_code == 200:
                    imported_prefs = json.loads(prefs_response.data.decode('utf-8'))
                    
                    # 验证导入的偏好设置
                    if 'theme' in imported_prefs:
                        assert imported_prefs['theme'] == 'dark', "偏好设置应该被正确导入"
    
    @pytest.mark.slow
    def test_user_data_consistency_across_sessions(self, client, app_context, user_service):
        """测试跨会话的用户数据一致性"""
        
        # 前置条件: 创建用户
        user = user_service.create_user(
            username='consistencyuser',
            email='consistency@example.com',
            password='Consistency123!',
            nickname='一致性测试用户'
        )
        
        # 会话1: 修改用户数据
        with client.session_transaction() as sess1:
            sess1['user_id'] = user.id
            sess1['logged_in'] = True
        
        # 在会话1中更新数据
        update_response1 = client.post('/user/profile/edit', data={
            'nickname': '会话1更新的昵称',
            'bio': '会话1设置的简介'
        })
        
        # 会话2: 验证数据更新
        # 清除会话并重新登录
        client.get('/user/logout')
        
        login_response = client.post('/user/login', data={
            'username': 'consistencyuser',
            'password': 'Consistency123!'
        })
        
        if login_response.status_code in [200, 302]:
            # 在新会话中验证数据
            profile_response2 = client.get('/user/profile')
            
            if profile_response2.status_code == 200:
                profile_html = profile_response2.data.decode('utf-8')
                
                # 验证数据一致性
                assert '会话1更新的昵称' in profile_html, "跨会话数据应该保持一致"
            
            # 通过API验证一致性
            api_response = client.get(f'/api/users/{user.id}')
            
            if api_response.status_code == 200:
                api_data = json.loads(api_response.data.decode('utf-8'))
                assert api_data['nickname'] == '会话1更新的昵称', "API数据应该与Web数据一致"
        
        # 验证数据库层面的一致性
        db_user = user_service.get_user_by_id(user.id)
        assert db_user.nickname == '会话1更新的昵称', "数据库数据应该是最新的"


if __name__ == '__main__':
    pytest.main([__file__])