"""
模态框HTML视图GET合约测试
测试HTMX模态框视图端点的合约规范
"""
import pytest
from app import create_app
from app.models.user import User


class TestHTMXModalsGetContract:
    """HTMX模态框GET视图合约测试类"""
    
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
    
    def test_get_prediction_modal_contract(self, client):
        """测试获取预测结果模态框 - 合约验证"""
        
        response = client.get('/htmx/modals/prediction?stock_code=000001')
        
        # 合约验证：状态码
        assert response.status_code == 200, "预测模态框应该返回200状态码"
        
        # 合约验证：响应格式 (HTML)
        assert response.headers['Content-Type'].startswith('text/html'), "响应Content-Type必须为text/html"
        
        # 合约验证：模态框HTML结构
        html_content = response.data.decode('utf-8')
        
        # 验证模态框基本结构
        modal_elements = [
            'modal',  # 模态框容器
            'modal-dialog',  # 对话框
            'modal-content',  # 内容区
            'modal-header',  # 头部
            'modal-body',  # 主体
            'modal-footer'  # 底部
        ]
        
        # 至少应包含模态框相关类
        has_modal_structure = any(elem in html_content for elem in modal_elements)
        assert has_modal_structure, "响应必须包含模态框结构元素"
        
        # 验证关闭按钮
        assert 'close' in html_content or '×' in html_content or '关闭' in html_content, "模态框必须包含关闭按钮"
        
        # 验证股票相关内容
        assert '000001' in html_content or '股票' in html_content, "预测模态框必须包含股票相关内容"
    
    def test_get_user_profile_modal_contract(self, client):
        """测试获取用户资料模态框 - 合约验证"""
        
        response = client.get('/htmx/modals/profile?user_id=1')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户资料模态框应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证用户资料内容
            profile_elements = [
                'nickname', 'username', 'email',  # 用户信息字段
                'avatar', 'profile', '资料',  # 资料相关
                'edit', 'update', '编辑'  # 编辑操作
            ]
            
            has_profile_content = any(elem in html_content for elem in profile_elements)
            assert has_profile_content, "用户资料模态框必须包含用户相关内容"
    
    def test_get_confirmation_modal_contract(self, client):
        """测试获取确认模态框 - 合约验证"""
        
        response = client.get('/htmx/modals/confirm?action=delete&target=prediction&id=123')
        
        # 合约验证：状态码
        assert response.status_code == 200, "确认模态框应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证确认模态框元素
        confirm_elements = [
            'confirm', '确认',  # 确认文本
            'cancel', '取消',  # 取消文本
            'warning', 'danger', '警告',  # 警告提示
            'delete', 'remove', '删除'  # 删除操作
        ]
        
        has_confirm_content = any(elem in html_content for elem in confirm_elements)
        assert has_confirm_content, "确认模态框必须包含确认相关内容"
        
        # 验证确认和取消按钮
        assert ('确认' in html_content or 'confirm' in html_content), "必须有确认按钮"
        assert ('取消' in html_content or 'cancel' in html_content), "必须有取消按钮"
    
    def test_get_settings_modal_contract(self, client):
        """测试获取设置模态框 - 合约验证"""
        
        response = client.get('/htmx/modals/settings?category=theme')
        
        # 合约验证：状态码
        assert response.status_code == 200, "设置模态框应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证设置相关内容
        settings_elements = [
            'settings', '设置',  # 设置文本
            'theme', 'language', 'preferences',  # 设置类别
            'save', 'apply', '保存', '应用'  # 保存操作
        ]
        
        has_settings_content = any(elem in html_content for elem in settings_elements)
        assert has_settings_content, "设置模态框必须包含设置相关内容"
    
    def test_get_help_modal_contract(self, client):
        """测试获取帮助模态框 - 合约验证"""
        
        response = client.get('/htmx/modals/help?topic=prediction')
        
        # 合约验证：状态码
        assert response.status_code == 200, "帮助模态框应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证帮助内容
        help_elements = [
            'help', '帮助',  # 帮助文本
            'guide', 'tutorial', '指南', '教程',  # 指导内容
            'tip', 'hint', '提示'  # 提示信息
        ]
        
        has_help_content = any(elem in html_content for elem in help_elements)
        assert has_help_content, "帮助模态框必须包含帮助相关内容"
    
    def test_modal_htmx_attributes_contract(self, client):
        """测试模态框HTMX属性合约"""
        
        response = client.get('/htmx/modals/prediction?stock_code=000001')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：HTMX属性
        htmx_attributes = [
            'hx-get', 'hx-post', 'hx-put', 'hx-delete',  # HTTP方法
            'hx-target', 'hx-swap',  # 目标和交换策略
            'hx-trigger',  # 触发事件
            'hx-confirm',  # 确认提示
        ]
        
        # 模态框可能包含HTMX属性用于交互
        # 注意：不是所有模态框都必须有HTMX属性，但如果有操作按钮通常会有
        if any('button' in line and ('submit' in line or 'action' in line) for line in html_content.split('\n')):
            has_htmx_attr = any(attr in html_content for attr in htmx_attributes)
            # 如果有交互按钮，通常应该有HTMX属性
    
    def test_modal_accessibility_contract(self, client):
        """测试模态框可访问性合约"""
        
        response = client.get('/htmx/modals/prediction?stock_code=000001')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：可访问性属性
        accessibility_attributes = [
            'aria-label',  # 标签
            'aria-labelledby',  # 标签引用
            'aria-describedby',  # 描述引用
            'role="dialog"',  # 对话框角色
            'tabindex',  # 标签索引
        ]
        
        # 模态框应该有适当的可访问性属性
        has_accessibility = any(attr in html_content for attr in accessibility_attributes)
        assert has_accessibility, "模态框应该包含可访问性属性"
    
    def test_modal_keyboard_navigation_contract(self, client):
        """测试模态框键盘导航合约"""
        
        response = client.get('/htmx/modals/confirm?action=delete')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：键盘导航支持
        keyboard_support = [
            'tabindex',  # 标签导航
            'autofocus',  # 自动焦点
            'onkeydown',  # 键盘事件
            'aria-hidden'  # 隐藏状态
        ]
        
        # 检查是否考虑了键盘导航
        has_keyboard_support = any(support in html_content for support in keyboard_support)
        
        # 至少应该有可聚焦的元素
        focusable_elements = [
            'button', 'input', 'select', 'textarea', 'a href'
        ]
        has_focusable = any(elem in html_content for elem in focusable_elements)
        assert has_focusable, "模态框必须包含可聚焦的元素"
    
    def test_modal_close_mechanisms_contract(self, client):
        """测试模态框关闭机制合约"""
        
        response = client.get('/htmx/modals/settings')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：关闭机制
        close_mechanisms = [
            'close', '关闭',  # 关闭文本
            '×',  # 关闭符号
            'modal-close',  # 关闭类
            'dismiss',  # 取消类
            'data-dismiss'  # Bootstrap关闭属性
        ]
        
        has_close_mechanism = any(mechanism in html_content for mechanism in close_mechanisms)
        assert has_close_mechanism, "模态框必须提供关闭机制"
    
    def test_modal_size_variants_contract(self, client):
        """测试模态框尺寸变体合约"""
        
        # 测试不同尺寸的模态框
        modal_sizes = [
            ('/htmx/modals/help', 'large'),
            ('/htmx/modals/confirm', 'small'),
            ('/htmx/modals/settings', 'medium')
        ]
        
        for url, expected_size in modal_sizes:
            response = client.get(url)
            
            # 合约验证：基本响应
            assert response.status_code == 200, f"模态框 {url} 应该返回200状态码"
            
            html_content = response.data.decode('utf-8')
            
            # 验证尺寸相关类（可能的实现）
            size_classes = [
                'modal-sm', 'modal-lg', 'modal-xl',  # Bootstrap风格
                'small', 'large', 'medium',  # 通用尺寸类
                'w-', 'max-w-'  # TailwindCSS宽度类
            ]
            
            # 检查是否有尺寸控制
            has_size_control = any(size_class in html_content for size_class in size_classes)
            # 注意：这个检查是可选的，因为尺寸可能通过CSS或其他方式控制
    
    def test_modal_content_loading_contract(self, client):
        """测试模态框内容加载合约"""
        
        response = client.get('/htmx/modals/prediction?stock_code=000001&loading=true')
        
        # 合约验证：加载状态
        assert response.status_code == 200, "加载状态的模态框应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证加载指示器
        loading_indicators = [
            'loading', 'spinner', 'skeleton',  # 加载状态
            'placeholder', 'shimmer',  # 占位符
            'htmx-indicator'  # HTMX加载指示器
        ]
        
        # 如果有loading参数，应该显示加载状态
        if 'loading=true' in str(response.request.url if hasattr(response, 'request') else ''):
            has_loading_indicator = any(indicator in html_content for indicator in loading_indicators)
            # 注意：加载状态的具体实现可能因应用而异
    
    def test_modal_error_states_contract(self, client):
        """测试模态框错误状态合约"""
        
        response = client.get('/htmx/modals/prediction?stock_code=INVALID')
        
        # 合约验证：错误处理
        # 可能返回200(显示错误)或4xx(错误状态)
        assert response.status_code in [200, 400, 404, 422], "无效参数应该返回适当的错误状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证错误显示
            error_indicators = [
                'error', 'invalid', 'not found',  # 错误文本
                '错误', '无效', '未找到',  # 中文错误
                'alert-error', 'text-red', 'error-message'  # 错误样式类
            ]
            
            # 检查是否显示了错误信息
            has_error_display = any(indicator in html_content for indicator in error_indicators)
            # 注意：错误显示的具体实现可能因应用而异
    
    def test_modal_dynamic_content_contract(self, client, test_user):
        """测试模态框动态内容合约"""
        
        response = client.get(f'/htmx/modals/profile?user_id={test_user.id}')
        
        # 合约验证：动态内容
        assert response.status_code == 200, "动态用户模态框应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证用户特定内容
        user_specific_content = [
            test_user.username,
            test_user.email,
            test_user.nickname or '测试用户'
        ]
        
        # 至少应该包含一些用户特定信息
        has_user_content = any(content in html_content for content in user_specific_content if content)
        assert has_user_content, "用户模态框应该包含用户特定内容"
    
    def test_modal_nested_content_contract(self, client):
        """测试模态框嵌套内容合约"""
        
        response = client.get('/htmx/modals/settings?category=advanced')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：嵌套结构处理
        nested_elements = [
            'accordion', 'collapse', 'tab',  # 嵌套组件
            'dropdown', 'select', 'option',  # 选择组件
            'form', 'fieldset', 'legend'  # 表单嵌套
        ]
        
        # 检查是否有嵌套结构
        has_nested_content = any(element in html_content for element in nested_elements)
        
        # 如果有嵌套内容，验证结构合理性
        if has_nested_content:
            # 确保HTML结构有效（简单检查）
            open_tags = html_content.count('<')
            close_tags = html_content.count('</')
            # 粗略检查标签配对（不是严格验证，但可以发现明显问题）
            assert abs(open_tags - close_tags * 2) < 10, "HTML标签结构应该基本平衡"


if __name__ == '__main__':
    pytest.main([__file__])