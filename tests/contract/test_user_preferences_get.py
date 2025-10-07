"""
用户偏好GET合约测试
测试用户偏好API的GET端点合约规范
"""
import pytest
import json
from app import create_app
from app.models.user_ui_preferences import UserUIPreferences
from app.models.user import User
from flask import url_for


class TestUserPreferencesGetContract:
    """用户偏好GET API合约测试类"""
    
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
    def test_preferences(self, app_context, test_user):
        """创建测试偏好数据"""
        from app import db
        
        preferences = [
            UserUIPreferences(
                user_id=test_user.id,
                preference_key='theme',
                preference_value={'mode': 'dark', 'primary_color': '#3b82f6'},
                category='appearance'
            ),
            UserUIPreferences(
                user_id=test_user.id,
                preference_key='language',
                preference_value={'locale': 'zh-CN', 'currency': 'CNY'},
                category='localization'
            ),
            UserUIPreferences(
                user_id=test_user.id,
                preference_key='dashboard',
                preference_value={'layout': 'grid', 'widgets': ['chart', 'news']},
                category='layout'
            )
        ]
        
        for pref in preferences:
            db.session.add(pref)
        
        db.session.commit()
        return preferences
    
    def test_get_user_preferences_success(self, client, test_user, test_preferences):
        """测试成功获取用户偏好 - 合约验证"""
        
        # 发送GET请求
        response = client.get(f'/api/user-preferences/{test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code == 200, "应该返回200状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        # 验证响应结构
        assert 'success' in data, "响应必须包含success字段"
        assert 'preferences' in data, "响应必须包含preferences字段"
        assert 'user_id' in data, "响应必须包含user_id字段"
        assert 'total_count' in data, "响应必须包含total_count字段"
        
        # 验证数据类型
        assert isinstance(data['success'], bool), "success字段必须为布尔类型"
        assert isinstance(data['preferences'], list), "preferences字段必须为列表类型"
        assert isinstance(data['user_id'], int), "user_id字段必须为整型"
        assert isinstance(data['total_count'], int), "total_count字段必须为整型"
        
        # 验证数据内容
        assert data['success'] is True, "成功请求success应为True"
        assert data['user_id'] == test_user.id, "user_id应该匹配请求的用户ID"
        assert data['total_count'] == 3, "应该返回3个偏好设置"
        assert len(data['preferences']) == 3, "preferences列表应包含3个元素"
        
        # 验证偏好项结构
        for pref in data['preferences']:
            assert 'id' in pref, "每个偏好项必须包含id字段"
            assert 'preference_key' in pref, "每个偏好项必须包含preference_key字段"
            assert 'preference_value' in pref, "每个偏好项必须包含preference_value字段"
            assert 'category' in pref, "每个偏好项必须包含category字段"
            assert 'created_at' in pref, "每个偏好项必须包含created_at字段"
            assert 'updated_at' in pref, "每个偏好项必须包含updated_at字段"
            
            # 验证字段类型
            assert isinstance(pref['id'], int), "id字段必须为整型"
            assert isinstance(pref['preference_key'], str), "preference_key字段必须为字符串"
            assert isinstance(pref['preference_value'], dict), "preference_value字段必须为字典"
            assert isinstance(pref['category'], str), "category字段必须为字符串"
    
    def test_get_specific_preference_success(self, client, test_user, test_preferences):
        """测试获取特定偏好项 - 合约验证"""
        
        pref_id = test_preferences[0].id
        response = client.get(f'/api/user-preferences/{test_user.id}/{pref_id}')
        
        # 合约验证：状态码
        assert response.status_code == 200, "应该返回200状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        # 验证响应结构
        assert 'success' in data, "响应必须包含success字段"
        assert 'preference' in data, "响应必须包含preference字段"
        
        # 验证数据类型和内容
        assert data['success'] is True, "成功请求success应为True"
        assert isinstance(data['preference'], dict), "preference字段必须为字典类型"
        
        pref = data['preference']
        assert pref['id'] == pref_id, "返回的偏好ID应该匹配请求的ID"
        assert pref['preference_key'] == 'theme', "应该返回正确的偏好键"
        assert pref['preference_value']['mode'] == 'dark', "应该返回正确的偏好值"
    
    def test_get_preferences_by_category(self, client, test_user, test_preferences):
        """测试按分类获取偏好 - 合约验证"""
        
        response = client.get(f'/api/user-preferences/{test_user.id}?category=appearance')
        
        # 合约验证
        assert response.status_code == 200, "应该返回200状态码"
        
        data = json.loads(response.data)
        assert data['success'] is True, "成功请求success应为True"
        assert data['total_count'] == 1, "appearance分类应该只有1个偏好"
        assert len(data['preferences']) == 1, "应该只返回1个偏好项"
        assert data['preferences'][0]['category'] == 'appearance', "返回的偏好应该属于appearance分类"
    
    def test_get_preferences_with_pagination(self, client, test_user, test_preferences):
        """测试分页获取偏好 - 合约验证"""
        
        response = client.get(f'/api/user-preferences/{test_user.id}?page=1&per_page=2')
        
        # 合约验证
        assert response.status_code == 200, "应该返回200状态码"
        
        data = json.loads(response.data)
        assert 'pagination' in data, "分页请求响应必须包含pagination字段"
        
        pagination = data['pagination']
        assert 'page' in pagination, "pagination必须包含page字段"
        assert 'per_page' in pagination, "pagination必须包含per_page字段"
        assert 'total' in pagination, "pagination必须包含total字段"
        assert 'pages' in pagination, "pagination必须包含pages字段"
        
        assert pagination['page'] == 1, "当前页应为1"
        assert pagination['per_page'] == 2, "每页条数应为2"
        assert pagination['total'] == 3, "总数应为3"
        assert len(data['preferences']) <= 2, "返回的偏好数量不应超过per_page设置"
    
    def test_get_nonexistent_user_preferences(self, client):
        """测试获取不存在用户的偏好 - 错误合约验证"""
        
        response = client.get('/api/user-preferences/999999')
        
        # 合约验证：错误响应
        assert response.status_code == 404, "不存在的用户应该返回404状态码"
        
        data = json.loads(response.data)
        assert 'success' in data, "错误响应也必须包含success字段"
        assert 'error' in data, "错误响应必须包含error字段"
        
        assert data['success'] is False, "错误请求success应为False"
        assert isinstance(data['error'], dict), "error字段必须为字典类型"
        assert 'code' in data['error'], "error必须包含code字段"
        assert 'message' in data['error'], "error必须包含message字段"
    
    def test_get_nonexistent_preference(self, client, test_user):
        """测试获取不存在的偏好项 - 错误合约验证"""
        
        response = client.get(f'/api/user-preferences/{test_user.id}/999999')
        
        # 合约验证：错误响应
        assert response.status_code == 404, "不存在的偏好项应该返回404状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'error' in data, "错误响应必须包含error字段"
        assert data['error']['code'] == 'NOT_FOUND', "错误代码应为NOT_FOUND"
    
    def test_get_preferences_invalid_user_id(self, client):
        """测试无效用户ID格式 - 错误合约验证"""
        
        response = client.get('/api/user-preferences/invalid')
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效用户ID应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_response_headers_contract(self, client, test_user):
        """测试响应头合约"""
        
        response = client.get(f'/api/user-preferences/{test_user.id}')
        
        # 合约验证：响应头
        assert response.headers['Content-Type'] == 'application/json', "响应Content-Type必须为application/json"
        assert 'X-Total-Count' in response.headers, "响应必须包含X-Total-Count头"
        
    def test_response_time_contract(self, client, test_user):
        """测试响应时间合约"""
        import time
        
        start_time = time.time()
        response = client.get(f'/api/user-preferences/{test_user.id}')
        end_time = time.time()
        
        # 合约验证：响应时间
        response_time = end_time - start_time
        assert response_time < 2.0, f"响应时间应小于2秒，实际为{response_time:.2f}秒"
        assert response.status_code == 200, "响应应该成功"


if __name__ == '__main__':
    pytest.main([__file__])