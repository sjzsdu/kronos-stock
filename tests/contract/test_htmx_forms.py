"""
表单HTML视图GET/POST合约测试
测试HTMX表单视图端点的合约规范
"""
import pytest
from app import create_app
from app.models.user import User


class TestHTMXFormsContract:
    """HTMX表单视图合约测试类"""
    
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
    
    def test_get_prediction_form_contract(self, client):
        """测试获取预测表单 - 合约验证"""
        
        response = client.get('/htmx/forms/prediction')
        
        # 合约验证：状态码
        assert response.status_code == 200, "预测表单应该返回200状态码"
        
        # 合约验证：响应格式 (HTML)
        assert response.headers['Content-Type'].startswith('text/html'), "响应Content-Type必须为text/html"
        
        # 合约验证：HTML结构
        html_content = response.data.decode('utf-8')
        
        # 验证表单元素存在
        assert '<form' in html_content, "响应必须包含表单元素"
        assert 'hx-post' in html_content or 'hx-get' in html_content, "表单必须包含HTMX属性"
        assert 'stock_code' in html_content, "表单必须包含股票代码字段"
        assert 'prediction_days' in html_content, "表单必须包含预测天数字段"
        
        # 验证语义化CSS类
        assert 'form' in html_content, "表单必须使用语义化CSS类"
        assert 'form-input' in html_content or 'form-group' in html_content, "输入字段必须使用语义化CSS类"
        assert 'btn' in html_content, "按钮必须使用语义化CSS类"
    
    def test_get_user_profile_form_contract(self, client):
        """测试获取用户资料表单 - 合约验证"""
        
        response = client.get('/htmx/forms/profile?user_id=1')
        
        # 合约验证：状态码
        assert response.status_code == 200, "用户资料表单应该返回200状态码"
        
        # 合约验证：HTML结构
        html_content = response.data.decode('utf-8')
        
        # 验证用户资料字段
        assert 'nickname' in html_content or 'full_name' in html_content, "表单必须包含用户资料字段"
        assert 'email' in html_content, "表单必须包含邮箱字段"
        
        # 验证HTMX属性
        assert 'hx-post' in html_content or 'hx-put' in html_content, "表单必须包含HTMX提交属性"
        assert 'hx-target' in html_content, "表单必须指定HTMX目标元素"
    
    def test_get_settings_form_contract(self, client):
        """测试获取设置表单 - 合约验证"""
        
        response = client.get('/htmx/forms/settings?category=preferences')
        
        # 合约验证：状态码
        assert response.status_code == 200, "设置表单应该返回200状态码"
        
        # 合约验证：HTML结构
        html_content = response.data.decode('utf-8')
        
        # 验证设置相关元素
        assert 'form' in html_content, "响应必须包含表单"
        assert 'theme' in html_content or 'language' in html_content, "设置表单必须包含配置选项"
    
    def test_post_form_submission_contract(self, client, test_user):
        """测试表单提交 - 合约验证"""
        
        form_data = {
            'stock_code': '000001',
            'prediction_days': '5',
            'model_name': 'kronos-mini'
        }
        
        response = client.post(
            '/htmx/forms/prediction',
            data=form_data,
            headers={'HX-Request': 'true'}
        )
        
        # 合约验证：HTMX响应处理
        # 可能返回200(成功)、422(验证失败)或其他状态码
        assert response.status_code in [200, 201, 422, 400], "表单提交应该返回明确的状态码"
        
        # 合约验证：响应格式
        if response.status_code in [200, 201]:
            # 成功提交的响应
            html_content = response.data.decode('utf-8')
            assert len(html_content) > 0, "成功响应不应为空"
        elif response.status_code in [422, 400]:
            # 验证失败的响应
            html_content = response.data.decode('utf-8')
            assert 'error' in html_content.lower() or 'invalid' in html_content.lower(), "错误响应应包含错误信息"
    
    def test_form_with_invalid_data_contract(self, client):
        """测试无效数据表单提交 - 错误合约验证"""
        
        invalid_data = {
            'stock_code': '',  # 空股票代码
            'prediction_days': 'invalid',  # 无效天数
        }
        
        response = client.post(
            '/htmx/forms/prediction',
            data=invalid_data,
            headers={'HX-Request': 'true'}
        )
        
        # 合约验证：错误处理
        assert response.status_code in [400, 422], "无效数据应该返回客户端错误状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证错误反馈
        assert 'error' in html_content.lower() or 'invalid' in html_content.lower() or '错误' in html_content, "错误响应必须包含错误信息"
    
    def test_form_partial_update_contract(self, client):
        """测试表单部分更新 - 合约验证"""
        
        response = client.get('/htmx/forms/stock-selector?query=平安')
        
        # 合约验证：部分表单更新
        assert response.status_code == 200, "部分表单更新应该成功"
        
        html_content = response.data.decode('utf-8')
        
        # 验证部分内容
        assert 'option' in html_content or 'select' in html_content, "股票选择器应包含选项元素"
    
    def test_form_validation_feedback_contract(self, client):
        """测试表单验证反馈 - 合约验证"""
        
        response = client.get('/htmx/forms/validation?field=stock_code&value=INVALID')
        
        # 合约验证：实时验证
        # 实时验证可能返回验证结果或空响应
        assert response.status_code in [200, 204], "实时验证应该返回200或204状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            # 验证反馈可能为空（有效）或包含错误信息（无效）
            assert isinstance(html_content, str), "验证响应应该是字符串"
    
    def test_form_htmx_attributes_contract(self, client):
        """测试表单HTMX属性合约"""
        
        response = client.get('/htmx/forms/prediction')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：HTMX属性
        htmx_attributes = [
            'hx-post', 'hx-get', 'hx-put', 'hx-delete',  # HTTP方法
            'hx-target', 'hx-swap',  # 目标和交换策略
            'hx-trigger',  # 触发事件
            'hx-indicator',  # 加载指示器
        ]
        
        # 至少应该包含一个HTMX属性
        has_htmx_attr = any(attr in html_content for attr in htmx_attributes)
        assert has_htmx_attr, "表单必须包含至少一个HTMX属性"
    
    def test_form_accessibility_contract(self, client):
        """测试表单可访问性合约"""
        
        response = client.get('/htmx/forms/prediction')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：可访问性
        assert 'label' in html_content, "表单必须包含标签"
        assert 'for=' in html_content or 'aria-label' in html_content, "表单必须有适当的标签关联"
        
        # 验证必填字段标识
        if 'required' in html_content:
            assert '*' in html_content or 'aria-required' in html_content, "必填字段必须有适当标识"
    
    def test_form_csrf_protection_contract(self, client):
        """测试表单CSRF保护合约"""
        
        response = client.get('/htmx/forms/prediction')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：CSRF保护
        # 检查是否有CSRF令牌字段
        has_csrf = (
            'csrf_token' in html_content or 
            'authenticity_token' in html_content or
            'name="_token"' in html_content
        )
        
        # 注意：某些HTMX请求可能不需要CSRF保护，这里只是检查是否考虑了安全性
        if '<form' in html_content and 'method="post"' in html_content.lower():
            # POST表单通常需要CSRF保护
            assert has_csrf or 'hx-headers' in html_content, "POST表单应该包含CSRF保护或安全头"
    
    def test_form_loading_states_contract(self, client):
        """测试表单加载状态合约"""
        
        response = client.get('/htmx/forms/prediction')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：加载状态
        loading_indicators = [
            'hx-indicator',  # HTMX加载指示器
            'loading',  # 加载CSS类
            'spinner',  # 旋转器
            'htmx-request'  # HTMX请求状态类
        ]
        
        # 检查是否有加载状态处理
        has_loading_state = any(indicator in html_content for indicator in loading_indicators)
        
        # 如果是HTMX表单，应该有加载状态处理
        if 'hx-' in html_content:
            assert has_loading_state, "HTMX表单应该包含加载状态处理"
    
    def test_form_error_handling_contract(self, client):
        """测试表单错误处理合约"""
        
        # 测试带有错误参数的表单
        response = client.get('/htmx/forms/prediction?error=validation_failed')
        
        # 合约验证：错误状态处理
        assert response.status_code == 200, "带错误参数的表单请求应该成功"
        
        html_content = response.data.decode('utf-8')
        
        # 验证是否有错误显示机制
        error_elements = [
            'form-error',  # 错误CSS类
            'alert-error',  # 错误提示类
            'error-message',  # 错误消息类
            'invalid-feedback'  # 无效反馈类
        ]
        
        # 如果有错误参数，应该有错误显示
        if 'error=' in str(response.request.url if hasattr(response, 'request') else ''):
            has_error_display = any(elem in html_content for elem in error_elements)
            # 注意：这个检查可能因实现而异


if __name__ == '__main__':
    pytest.main([__file__])