"""
使用统计POST合约测试
测试使用统计跟踪API的POST端点合约规范
"""
import pytest
import json
import time
from app import create_app
from app.models.user import User


class TestUsageTrackingPostContract:
    """使用统计POST API合约测试类"""
    
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
    
    def test_track_component_usage_success(self, client, test_user):
        """测试成功记录组件使用 - 合约验证"""
        
        usage_data = {
            'component_name': 'prediction_form',
            'action': 'submit',
            'user_id': test_user.id,
            'session_id': 'sess_123456789',
            'additional_data': {
                'stock_code': '000001',
                'model_used': 'kronos-mini',
                'prediction_days': 5,
                'form_completion_time': 45.2
            }
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        # 合约验证：状态码
        assert response.status_code == 201, "成功记录使用统计应该返回201状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        # 验证必须字段
        assert 'success' in data, "响应必须包含success字段"
        assert 'message' in data, "响应必须包含message字段"
        assert 'tracking_id' in data, "响应必须包含tracking_id字段"
        assert 'recorded_at' in data, "响应必须包含recorded_at时间戳"
        
        # 验证数据类型
        assert isinstance(data['success'], bool), "success字段必须为布尔类型"
        assert isinstance(data['message'], str), "message字段必须为字符串类型"
        assert isinstance(data['tracking_id'], int), "tracking_id字段必须为整型"
        assert isinstance(data['recorded_at'], str), "recorded_at字段必须为字符串类型"
        
        # 验证数据内容
        assert data['success'] is True, "成功记录success应为True"
        assert '成功' in data['message'] or 'success' in data['message'].lower(), "消息应包含成功提示"
        assert data['tracking_id'] > 0, "tracking_id应该为正整数"
    
    def test_track_minimal_usage_data(self, client):
        """测试记录最小必须数据 - 合约验证"""
        
        minimal_data = {
            'component_name': 'sidebar',
            'action': 'toggle'
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        
        # 合约验证：最小数据应该成功
        assert response.status_code == 201, "最小必须数据应该成功记录"
        
        data = json.loads(response.data)
        assert data['success'] is True, "最小数据记录success应为True"
        assert 'tracking_id' in data, "响应必须包含生成的tracking_id"
    
    def test_track_batch_usage_events(self, client, test_user):
        """测试批量记录使用事件 - 合约验证"""
        
        batch_data = {
            'events': [
                {
                    'component_name': 'prediction_form',
                    'action': 'view',
                    'user_id': test_user.id,
                    'session_id': 'sess_123'
                },
                {
                    'component_name': 'prediction_form',
                    'action': 'input_stock_code',
                    'user_id': test_user.id,
                    'session_id': 'sess_123',
                    'additional_data': {'stock_code': '000001'}
                },
                {
                    'component_name': 'prediction_form',
                    'action': 'submit',
                    'user_id': test_user.id,
                    'session_id': 'sess_123',
                    'additional_data': {'stock_code': '000001', 'model': 'kronos-mini'}
                }
            ]
        }
        
        response = client.post(
            '/api/usage-tracking/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 合约验证：批量记录
        assert response.status_code == 201, "批量记录应该返回201状态码"
        
        data = json.loads(response.data)
        assert data['success'] is True, "批量记录success应为True"
        assert 'recorded_count' in data, "批量记录响应必须包含recorded_count"
        assert 'tracking_ids' in data, "批量记录响应必须包含tracking_ids列表"
        
        assert isinstance(data['recorded_count'], int), "recorded_count必须为整型"
        assert isinstance(data['tracking_ids'], list), "tracking_ids必须为列表类型"
        assert data['recorded_count'] == 3, "应该记录3个事件"
        assert len(data['tracking_ids']) == 3, "应该返回3个跟踪ID"
    
    def test_track_with_invalid_component_name(self, client):
        """测试无效组件名称 - 错误合约验证"""
        
        invalid_data = {
            'component_name': '',  # 空字符串
            'action': 'click'
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "空组件名称应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'error' in data, "错误响应必须包含error字段"
        
        error = data['error']
        assert error['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
        assert 'component_name' in error['message'], "错误消息应提及component_name字段"
    
    def test_track_with_invalid_action(self, client):
        """测试无效操作类型 - 错误合约验证"""
        
        invalid_data = {
            'component_name': 'test_component',
            'action': None  # 空值
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效操作应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_track_with_missing_required_fields(self, client):
        """测试缺少必须字段 - 错误合约验证"""
        
        incomplete_data = {
            'action': 'click'
            # 缺少 component_name
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "缺少必须字段应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
        assert 'details' in data['error'], "验证错误应该包含details字段"
    
    def test_track_with_invalid_json(self, client):
        """测试无效JSON格式 - 错误合约验证"""
        
        response = client.post(
            '/api/usage-tracking/',
            data='invalid json format',
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效JSON应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_track_duplicate_events(self, client, test_user):
        """测试重复事件记录 - 合约验证"""
        
        usage_data = {
            'component_name': 'prediction_form',
            'action': 'submit',
            'user_id': test_user.id,
            'session_id': 'sess_duplicate_test',
            'additional_data': {'stock_code': '000001'}
        }
        
        # 第一次提交
        response1 = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        # 第二次提交相同数据
        response2 = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        # 合约验证：重复事件处理
        assert response1.status_code == 201, "第一次提交应该成功"
        assert response2.status_code == 201, "重复事件也应该被记录"
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        
        assert data1['tracking_id'] != data2['tracking_id'], "重复事件应该生成不同的tracking_id"
    
    def test_supported_component_actions_contract(self, client):
        """测试支持的组件操作合约"""
        
        supported_actions = [
            ('prediction_form', 'view'),
            ('prediction_form', 'submit'),
            ('prediction_form', 'reset'),
            ('sidebar', 'toggle'),
            ('sidebar', 'collapse'),
            ('sidebar', 'expand'),
            ('chart_display', 'zoom'),
            ('chart_display', 'pan'),
            ('modal', 'open'),
            ('modal', 'close'),
            ('button', 'click'),
            ('link', 'click')
        ]
        
        for component, action in supported_actions:
            usage_data = {
                'component_name': component,
                'action': action
            }
            
            response = client.post(
                '/api/usage-tracking/',
                data=json.dumps(usage_data),
                content_type='application/json'
            )
            
            # 合约验证：所有支持的操作都应该被接受
            assert response.status_code == 201, f"组件 {component} 的操作 {action} 应该被支持"
    
    def test_tracking_with_anonymous_user(self, client):
        """测试匿名用户使用跟踪 - 合约验证"""
        
        anonymous_data = {
            'component_name': 'stock_search',
            'action': 'search',
            'session_id': 'anonymous_sess_123',
            'additional_data': {
                'search_term': '平安银行',
                'result_count': 5
            }
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(anonymous_data),
            content_type='application/json'
        )
        
        # 合约验证：匿名用户跟踪
        assert response.status_code == 201, "匿名用户操作应该被记录"
        
        data = json.loads(response.data)
        assert data['success'] is True, "匿名用户记录success应为True"
    
    def test_response_headers_contract(self, client):
        """测试响应头合约"""
        
        usage_data = {
            'component_name': 'test_component',
            'action': 'test_action'
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        # 合约验证：响应头
        assert response.headers['Content-Type'] == 'application/json', "响应Content-Type必须为application/json"
    
    def test_tracking_with_large_additional_data(self, client):
        """测试大量附加数据 - 合约验证"""
        
        large_additional_data = {
            'user_interactions': [f'interaction_{i}' for i in range(1000)],
            'form_data': {f'field_{i}': f'value_{i}' for i in range(100)},
            'performance_metrics': {f'metric_{i}': i * 0.1 for i in range(50)}
        }
        
        usage_data = {
            'component_name': 'complex_form',
            'action': 'submit_with_large_data',
            'additional_data': large_additional_data
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        # 合约验证：大数据处理
        # 根据系统配置，可能接受也可能拒绝
        assert response.status_code in [201, 413, 400], "大数据请求应该有明确的处理结果"
        
        if response.status_code == 201:
            data = json.loads(response.data)
            assert data['success'] is True, "接受的大数据请求应该成功处理"
    
    def test_timestamp_accuracy_contract(self, client):
        """测试时间戳准确性合约"""
        
        before_time = time.time()
        
        usage_data = {
            'component_name': 'timestamp_test',
            'action': 'test_timing'
        }
        
        response = client.post(
            '/api/usage-tracking/',
            data=json.dumps(usage_data),
            content_type='application/json'
        )
        
        after_time = time.time()
        
        # 合约验证：时间戳准确性
        assert response.status_code == 201, "请求应该成功"
        
        data = json.loads(response.data)
        recorded_at = data['recorded_at']
        
        # 验证时间戳格式和准确性
        from datetime import datetime
        recorded_datetime = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
        recorded_timestamp = recorded_datetime.timestamp()
        
        assert before_time <= recorded_timestamp <= after_time, "记录时间应该在请求时间范围内"
    
    def test_session_tracking_contract(self, client):
        """测试会话跟踪合约"""
        
        session_id = 'test_session_123'
        
        # 同一会话的多个操作
        actions = ['view', 'interact', 'submit']
        
        for action in actions:
            usage_data = {
                'component_name': 'session_test_component',
                'action': action,
                'session_id': session_id
            }
            
            response = client.post(
                '/api/usage-tracking/',
                data=json.dumps(usage_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201, f"会话操作 {action} 应该成功记录"
            
            data = json.loads(response.data)
            assert data['success'] is True, f"会话操作 {action} 记录应该成功"


if __name__ == '__main__':
    pytest.main([__file__])