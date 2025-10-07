"""
性能指标POST合约测试
测试性能监控API的POST端点合约规范
"""
import pytest
import json
import time
from app import create_app
from app.models.user import User


class TestPerformanceMetricsPostContract:
    """性能指标POST API合约测试类"""
    
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
    
    def test_submit_performance_metric_success(self, client, test_user):
        """测试成功提交性能指标 - 合约验证"""
        
        metric_data = {
            'metric_type': 'page_load',
            'metric_name': 'dashboard_load_time',
            'metric_value': 1.25,
            'user_id': test_user.id,
            'session_id': 'sess_123456789',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'additional_data': {
                'page': '/dashboard',
                'component_count': 15,
                'cache_hits': 8,
                'cache_misses': 2
            }
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        # 合约验证：状态码
        assert response.status_code == 201, "成功提交指标应该返回201状态码"
        
        # 合约验证：响应格式
        data = json.loads(response.data)
        
        # 验证必须字段
        assert 'success' in data, "响应必须包含success字段"
        assert 'message' in data, "响应必须包含message字段"
        assert 'metric_id' in data, "响应必须包含metric_id字段"
        assert 'recorded_at' in data, "响应必须包含recorded_at时间戳"
        
        # 验证数据类型
        assert isinstance(data['success'], bool), "success字段必须为布尔类型"
        assert isinstance(data['message'], str), "message字段必须为字符串类型"
        assert isinstance(data['metric_id'], int), "metric_id字段必须为整型"
        assert isinstance(data['recorded_at'], str), "recorded_at字段必须为字符串类型"
        
        # 验证数据内容
        assert data['success'] is True, "成功提交success应为True"
        assert '成功' in data['message'] or 'success' in data['message'].lower(), "消息应包含成功提示"
        assert data['metric_id'] > 0, "metric_id应该为正整数"
    
    def test_submit_minimal_metric_data(self, client):
        """测试提交最小必须数据 - 合约验证"""
        
        minimal_data = {
            'metric_type': 'api_response',
            'metric_name': 'prediction_api_time',
            'metric_value': 0.85
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        
        # 合约验证：最小数据应该成功
        assert response.status_code == 201, "最小必须数据应该成功提交"
        
        data = json.loads(response.data)
        assert data['success'] is True, "最小数据提交success应为True"
        assert 'metric_id' in data, "响应必须包含生成的metric_id"
    
    def test_submit_batch_metrics(self, client, test_user):
        """测试批量提交性能指标 - 合约验证"""
        
        batch_data = {
            'metrics': [
                {
                    'metric_type': 'page_load',
                    'metric_name': 'dashboard_load_time',
                    'metric_value': 1.2,
                    'user_id': test_user.id
                },
                {
                    'metric_type': 'api_response',
                    'metric_name': 'stock_search_time',
                    'metric_value': 0.3,
                    'user_id': test_user.id
                },
                {
                    'metric_type': 'user_interaction',
                    'metric_name': 'form_completion_time',
                    'metric_value': 45.6,
                    'user_id': test_user.id
                }
            ]
        }
        
        response = client.post(
            '/api/performance/metrics/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        # 合约验证：批量提交
        assert response.status_code == 201, "批量提交应该返回201状态码"
        
        data = json.loads(response.data)
        assert data['success'] is True, "批量提交success应为True"
        assert 'submitted_count' in data, "批量提交响应必须包含submitted_count"
        assert 'metric_ids' in data, "批量提交响应必须包含metric_ids列表"
        
        assert isinstance(data['submitted_count'], int), "submitted_count必须为整型"
        assert isinstance(data['metric_ids'], list), "metric_ids必须为列表类型"
        assert data['submitted_count'] == 3, "应该提交3个指标"
        assert len(data['metric_ids']) == 3, "应该返回3个指标ID"
    
    def test_submit_with_invalid_metric_type(self, client):
        """测试无效指标类型 - 错误合约验证"""
        
        invalid_data = {
            'metric_type': 'invalid_type',
            'metric_name': 'test_metric',
            'metric_value': 1.0
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效指标类型应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'error' in data, "错误响应必须包含error字段"
        
        error = data['error']
        assert error['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
        assert 'metric_type' in error['message'], "错误消息应提及metric_type字段"
    
    def test_submit_with_invalid_metric_value(self, client):
        """测试无效指标值 - 错误合约验证"""
        
        invalid_data = {
            'metric_type': 'page_load',
            'metric_name': 'test_metric',
            'metric_value': 'not_a_number'
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效指标值应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_submit_with_missing_required_fields(self, client):
        """测试缺少必须字段 - 错误合约验证"""
        
        incomplete_data = {
            'metric_type': 'page_load'
            # 缺少 metric_name 和 metric_value
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "缺少必须字段应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
        assert 'details' in data['error'], "验证错误应该包含details字段"
    
    def test_submit_with_invalid_json(self, client):
        """测试无效JSON格式 - 错误合约验证"""
        
        response = client.post(
            '/api/performance/metrics',
            data='invalid json format',
            content_type='application/json'
        )
        
        # 合约验证：错误响应
        assert response.status_code == 400, "无效JSON应该返回400状态码"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert data['error']['code'] == 'VALIDATION_ERROR', "错误代码应为VALIDATION_ERROR"
    
    def test_submit_with_negative_metric_value(self, client):
        """测试负数指标值 - 错误合约验证"""
        
        negative_data = {
            'metric_type': 'page_load',
            'metric_name': 'test_metric',
            'metric_value': -1.5
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(negative_data),
            content_type='application/json'
        )
        
        # 合约验证：负数处理
        assert response.status_code == 400, "负数指标值应该被拒绝"
        
        data = json.loads(response.data)
        assert data['success'] is False, "错误请求success应为False"
        assert 'metric_value' in data['error']['message'], "错误消息应提及metric_value"
    
    def test_submit_with_oversized_data(self, client):
        """测试超大数据提交 - 错误合约验证"""
        
        oversized_data = {
            'metric_type': 'page_load',
            'metric_name': 'test_metric',
            'metric_value': 1.0,
            'additional_data': {
                'large_field': 'x' * 100000  # 100KB的数据
            }
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(oversized_data),
            content_type='application/json'
        )
        
        # 合约验证：数据大小限制
        assert response.status_code == 413 or response.status_code == 400, "超大数据应该被拒绝"
        
        if response.status_code == 400:
            data = json.loads(response.data)
            assert data['success'] is False, "错误请求success应为False"
    
    def test_response_headers_contract(self, client):
        """测试响应头合约"""
        
        metric_data = {
            'metric_type': 'page_load',
            'metric_name': 'test_metric',
            'metric_value': 1.0
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        # 合约验证：响应头
        assert response.headers['Content-Type'] == 'application/json', "响应Content-Type必须为application/json"
        
    def test_request_id_tracing(self, client):
        """测试请求ID跟踪合约"""
        
        metric_data = {
            'metric_type': 'page_load',
            'metric_name': 'test_metric',
            'metric_value': 1.0,
            'request_id': 'req_123456789'
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        # 合约验证：请求跟踪
        assert response.status_code == 201, "包含request_id的请求应该成功"
        
        data = json.loads(response.data)
        assert data['success'] is True, "请求应该成功处理"
    
    def test_performance_metric_types_contract(self, client):
        """测试支持的指标类型合约"""
        
        valid_types = [
            'page_load',
            'api_response', 
            'user_interaction',
            'database_query',
            'cache_operation',
            'model_prediction'
        ]
        
        for metric_type in valid_types:
            metric_data = {
                'metric_type': metric_type,
                'metric_name': f'test_{metric_type}_metric',
                'metric_value': 1.0
            }
            
            response = client.post(
                '/api/performance/metrics',
                data=json.dumps(metric_data),
                content_type='application/json'
            )
            
            # 合约验证：所有有效类型都应该被接受
            assert response.status_code == 201, f"指标类型 {metric_type} 应该被接受"
    
    def test_submission_timestamp_contract(self, client):
        """测试提交时间戳合约"""
        
        before_time = time.time()
        
        metric_data = {
            'metric_type': 'page_load',
            'metric_name': 'timestamp_test',
            'metric_value': 1.0
        }
        
        response = client.post(
            '/api/performance/metrics',
            data=json.dumps(metric_data),
            content_type='application/json'
        )
        
        after_time = time.time()
        
        # 合约验证：时间戳
        assert response.status_code == 201, "请求应该成功"
        
        data = json.loads(response.data)
        recorded_at = data['recorded_at']
        
        # 验证时间戳格式和范围
        from datetime import datetime
        recorded_datetime = datetime.fromisoformat(recorded_at.replace('Z', '+00:00'))
        recorded_timestamp = recorded_datetime.timestamp()
        
        assert before_time <= recorded_timestamp <= after_time, "recorded_at时间戳应该在请求时间范围内"


if __name__ == '__main__':
    pytest.main([__file__])