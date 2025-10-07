"""
用户偏好PUT合约测试  
测试用户偏好API的PUT端点合约规范
"""
import pytest
import json
from app import create_app
from app.models.user_ui_preferences import UserUIPreferences
from app.models.user import User


class TestUserPreferencesPutContract:
    """用户偏好PUT API合约测试类"""
    
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
            yield app
    
    @pytest.fixture
    def test_user(self, app_context):
        """创建测试用户"""
        from app import db
        
        user = User(
            username='testuser',
            email='test@example.com',
            nickname='测试用户'
        )
        user.set_password('testpass123')
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @pytest.fixture
    def existing_preference(self, app_context, test_user):
        """创建已存在的偏好设置"""
        from app import db
        
        preference = UserUIPreferences(
            user_id=test_user.id,
            preference_key='theme',
            preference_value={'mode': 'light', 'primary_color': '#000000'},
            category='appearance'
        )
        
        db.session.add(preference)
        db.session.commit()
        return preference
    
    def test_update_preference_success(self, client, test_user, existing_preference):
        """测试成功更新偏好 - 合约验证"""
        
        update_data = {
            'preference_key': 'theme',
            'preference_value': {
                'mode': 'dark',
                'primary_color': '#3b82f6',
                'accent_color': '#10b981'
            },
            'category': 'appearance'
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # 合约验证：状态码
        assert response.status_code == 200, "成功更新应该返回200状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        # 验证必须字段
        assert 'success' in data, "响应必须包含success字段"
        assert 'message' in data, "响应必须包含message字段"
        assert 'preference' in data, "响应必须包含preference字段"
        
        # 验证数据类型
        assert isinstance(data['success'], bool), "success字段必须为布尔类型"
        assert isinstance(data['message'], str), "message字段必须为字符串类型"
        assert isinstance(data['preference'], dict), "preference字段必须为字典类型"
        
        # 验证数据内容
        assert data['success'] is True, "成功更新success应为True"
        assert '成功' in data['message'] or 'success' in data['message'].lower(), "成功消息应包含成功提示"
        
        # 验证更新后的偏好对象
        pref = data['preference']
        assert pref['id'] == existing_preference.id, "ID应该保持不变"
        assert pref['preference_key'] == 'theme', "preference_key应该正确更新"
        assert pref['preference_value']['mode'] == 'dark', "preference_value应该正确更新"
        assert pref['preference_value']['primary_color'] == '#3b82f6', "新增字段应该存在"
        assert pref['category'] == 'appearance', "category应该正确"
        assert 'updated_at' in pref, "应该包含updated_at时间戳"
    
    def test_create_new_preference(self, client, test_user):
        """测试创建新偏好 - 合约验证"""
        
        new_preference_data = {
            'preference_key': 'dashboard_layout',
            'preference_value': {
                'layout': 'grid',
                'columns': 3,
                'widgets': ['chart', 'news', 'watchlist']
            },
            'category': 'layout'
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/new',
            data=json.dumps(new_preference_data),
            content_type='application/json'
        )
        
        # 合约验证：状态码
        assert response.status_code == 201, "创建新偏好应该返回201状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        assert data['success'] is True, "成功创建success应为True"
        assert 'preference' in data, "响应必须包含新创建的preference"
        
        pref = data['preference']
        assert 'id' in pref, "新创建的偏好必须有ID"
        assert pref['preference_key'] == 'dashboard_layout', "preference_key应该正确"
        assert pref['user_id'] == test_user.id, "user_id应该正确关联"
    
    def test_batch_update_preferences(self, client, test_user):
        """测试批量更新偏好 - 合约验证"""
        
        batch_data = {
            'preferences': {
                'theme': {
                    'mode': 'dark',
                    'primary_color': '#3b82f6'
                },
                'language': {
                    'locale': 'zh-CN',
                    'currency': 'CNY'
                },
                'notifications': {
                    'email_enabled': True,
                    'push_enabled': False
                }
            }
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 合约验证：状态码
        assert response.status_code == 200, "批量更新应该返回200状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        assert data['success'] is True, "成功批量更新success应为True"
        assert 'updated_count' in data, "批量更新响应必须包含updated_count"
        assert 'preferences' in data, "批量更新响应必须包含preferences列表"
        
        assert isinstance(data['updated_count'], int), "updated_count必须为整型"
        assert isinstance(data['preferences'], list), "preferences必须为列表类型"
        assert data['updated_count'] == 3, "应该更新3个偏好设置"
        assert len(data['preferences']) == 3, "应该返回3个偏好对象"
    
    def test_update_with_invalid_data(self, client, test_user, existing_preference):
        """测试无效数据更新 - 错误合约验证"""
        
        invalid_data = {
            'preference_key': '',  # 空字符串
            'preference_value': 'invalid_json',  # 无效的JSON结构
            'category': None  # 空值
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效数据应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'error' in data, "错误响应必须包含error字段"
        
        error = data['error']
        assert error['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
        assert 'message' in error, "错误必须包含message字段"
        assert 'details' in error, "验证错误应该包含details字段"
    
    def test_update_nonexistent_preference(self, client, test_user):
        """测试更新不存在的偏好 - 错误合约验证"""
        
        update_data = {
            'preference_key': 'theme',
            'preference_value': {'mode': 'dark'},
            'category': 'appearance'
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/999999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 404, "不存在的偏好应该返回404状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'NOT_FOUND', "错误代码应为NOT_FOUND"
    
    def test_update_unauthorized_user(self, client):
        """测试未授权用户更新 - 错误合约验证"""
        
        update_data = {
            'preference_key': 'theme',
            'preference_value': {'mode': 'dark'},
            'category': 'appearance'
        }
        
        response = client.put(
            '/api/user-preferences/999999/1',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应  
        assert response.status_code in [401, 403, 404], "未授权访问应该返回4xx状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'error' in data, "错误响应必须包含error字段"
    
    def test_update_with_missing_fields(self, client, test_user, existing_preference):
        """测试缺少必须字段的更新 - 错误合约验证"""
        
        incomplete_data = {
            'preference_value': {'mode': 'dark'}
            # 缺少 preference_key 和 category
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "缺少必须字段应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_update_with_invalid_json(self, client, test_user, existing_preference):
        """测试无效JSON格式 - 错误合约验证"""
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data='invalid json string',
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效JSON应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_response_headers_contract(self, client, test_user, existing_preference):
        """测试响应头合约"""
        
        update_data = {
            'preference_key': 'theme',
            'preference_value': {'mode': 'dark'},
            'category': 'appearance'
        }
        
        response = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # 合约验证：响应头
        assert response.headers['Content-Type'] == 'application/json', "响应Content-Type必须为application/json"
        
    def test_idempotent_update_contract(self, client, test_user, existing_preference):
        """测试幂等性合约 - 相同数据多次更新应产生相同结果"""
        
        update_data = {
            'preference_key': 'theme',
            'preference_value': {'mode': 'dark', 'primary_color': '#3b82f6'},
            'category': 'appearance'
        }
        
        # 第一次更新
        response1 = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data1 = json.loads(response1.data)
        
        # 第二次更新（相同数据）
        response2 = client.put(
            f'/api/user-preferences/{test_user.id}/{existing_preference.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        data2 = json.loads(response2.data)
        
        # 合约验证：幂等性
        assert response1.status_code == response2.status_code, "两次请求应返回相同状态码"
        assert data1['success'] == data2['success'], "两次请求success状态应相同"
        assert data1['preference']['preference_value'] == data2['preference']['preference_value'], "偏好值应保持相同"


if __name__ == '__main__':
    pytest.main([__file__])