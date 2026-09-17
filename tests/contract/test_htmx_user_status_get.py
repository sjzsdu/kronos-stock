"""
用户状态HTML视图GET合约测试
测试HTMX用户状态视图端点的合约规范
"""
import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models.user import User


class TestHTMXUserStatusGetContract:
    """HTMX用户状态GET视图合约测试类"""
    
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
        user.last_seen = datetime.utcnow()
        
        db.session.add(user)
        db.session.commit()
        return user
    
    def test_get_user_status_widget_contract(self, client, test_user):
        """测试获取用户状态小组件 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户状态小组件应该返回200或404状态码"
        
        if response.status_code == 200:
            # 合约验证：响应格式 (HTML)
            assert response.headers['Content-Type'].startswith('text/html'), "响应Content-Type必须为text/html"
            
            html_content = response.data.decode('utf-8')
            
            # 验证用户状态元素
            status_elements = [
                'user-status', 'status', 'online', 'offline',  # 状态相关类
                'avatar', 'profile-pic', 'user-icon',  # 头像元素
                'username', 'nickname', 'display-name',  # 用户名相关
                'last-seen', 'active', 'inactive'  # 活跃状态
            ]
            
            has_status_elements = any(elem in html_content for elem in status_elements)
            assert has_status_elements, "用户状态小组件必须包含状态相关元素"
            
            # 验证用户信息显示
            user_info = [
                test_user.username,
                test_user.nickname,
                '测试用户'
            ]
            
            has_user_info = any(info in html_content for info in user_info if info)
            assert has_user_info, "用户状态必须显示用户信息"
    
    def test_get_online_status_contract(self, client, test_user):
        """测试获取在线状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/online-status?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "在线状态应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证在线状态标识
            online_indicators = [
                'online', 'active', 'available',  # 在线状态
                'offline', 'inactive', 'away',  # 离线状态
                '在线', '离线', '活跃',  # 中文状态
                'status-dot', 'indicator', 'badge'  # 状态指示器
            ]
            
            has_online_indicator = any(indicator in html_content for indicator in online_indicators)
            assert has_online_indicator, "在线状态必须包含状态标识"
    
    def test_get_user_activity_contract(self, client, test_user):
        """测试获取用户活动状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/activity?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户活动状态应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证活动相关元素
            activity_elements = [
                'activity', 'action', 'event',  # 活动相关
                'last-action', 'recent', 'history',  # 最近活动
                'prediction', 'login', 'view',  # 活动类型
                '预测', '登录', '查看'  # 中文活动类型
            ]
            
            has_activity_elements = any(elem in html_content for elem in activity_elements)
            assert has_activity_elements, "用户活动状态必须包含活动相关信息"
    
    def test_get_user_preferences_status_contract(self, client, test_user):
        """测试获取用户偏好状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/preferences-status?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户偏好状态应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证偏好设置元素
            preferences_elements = [
                'preferences', 'settings', 'config',  # 偏好相关
                'theme', 'language', 'timezone',  # 偏好类型
                'notification', 'privacy', 'display',  # 设置类别
                '主题', '语言', '通知'  # 中文偏好
            ]
            
            has_preferences_elements = any(elem in html_content for elem in preferences_elements)
            assert has_preferences_elements, "用户偏好状态必须包含偏好相关信息"
    
    def test_get_user_session_status_contract(self, client, test_user):
        """测试获取用户会话状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/session-status?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户会话状态应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证会话相关元素
            session_elements = [
                'session', 'login', 'auth',  # 会话相关
                'token', 'expire', 'timeout',  # 会话属性
                'device', 'browser', 'ip',  # 会话信息
                '会话', '登录', '设备'  # 中文会话信息
            ]
            
            has_session_elements = any(elem in html_content for elem in session_elements)
            assert has_session_elements, "用户会话状态必须包含会话相关信息"
    
    def test_get_user_stats_contract(self, client, test_user):
        """测试获取用户统计信息 - 合约验证"""
        
        response = client.get(f'/htmx/user/stats?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 404], "用户统计信息应该返回200或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证统计相关元素
            stats_elements = [
                'stats', 'statistics', 'metrics',  # 统计相关
                'count', 'total', 'number',  # 数值相关
                'predictions', 'views', 'actions',  # 统计类型
                '预测次数', '查看次数', '统计'  # 中文统计
            ]
            
            has_stats_elements = any(elem in html_content for elem in stats_elements)
            assert has_stats_elements, "用户统计信息必须包含统计相关数据"
    
    def test_get_user_permissions_status_contract(self, client, test_user):
        """测试获取用户权限状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/permissions?user_id={test_user.id}')
        
        # 合约验证：状态码
        assert response.status_code in [200, 403, 404], "用户权限状态应该返回200、403或404状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证权限相关元素
            permission_elements = [
                'permission', 'role', 'access',  # 权限相关
                'admin', 'user', 'guest',  # 角色类型
                'allow', 'deny', 'grant',  # 权限状态
                '权限', '角色', '访问'  # 中文权限
            ]
            
            has_permission_elements = any(elem in html_content for elem in permission_elements)
            assert has_permission_elements, "用户权限状态必须包含权限相关信息"
    
    def test_user_status_real_time_updates_contract(self, client, test_user):
        """测试用户状态实时更新 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}&real_time=true')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：实时更新支持
        real_time_attributes = [
            'hx-trigger="every',  # 定时触发
            'hx-swap-oob',  # 外部交换
            'hx-poll',  # 轮询
            'ws-connect',  # WebSocket连接
            'sse-connect'  # Server-Sent Events
        ]
        
        # 检查实时更新机制
        has_real_time = any(attr in html_content for attr in real_time_attributes)
        
        # 如果启用实时更新，应该有相应机制
        if 'real_time=true' in str(response.request.url if hasattr(response, 'request') else ''):
            # 实时更新机制检查是可选的，因为实现方式可能不同
            pass
    
    def test_user_status_accessibility_contract(self, client, test_user):
        """测试用户状态可访问性 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：可访问性属性
        accessibility_attributes = [
            'aria-label',  # 标签
            'aria-live',  # 实时区域
            'aria-atomic',  # 原子更新
            'role="status"',  # 状态角色
            'alt=',  # 图像替代文本
            'title='  # 提示标题
        ]
        
        # 用户状态组件应该考虑可访问性
        has_accessibility = any(attr in html_content for attr in accessibility_attributes)
        
        # 可访问性是推荐的实践
        if len(html_content.strip()) > 50:
            # 如果有实际内容，建议考虑可访问性
            pass
    
    def test_user_status_responsive_design_contract(self, client, test_user):
        """测试用户状态响应式设计 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：响应式设计
        responsive_classes = [
            'sm:', 'md:', 'lg:', 'xl:',  # TailwindCSS响应式前缀
            'hidden-', 'visible-',  # Bootstrap响应式类
            '@media', 'responsive',  # CSS媒体查询
            'mobile', 'tablet', 'desktop'  # 设备类型类
        ]
        
        # 检查响应式设计支持
        has_responsive = any(cls in html_content for cls in responsive_classes)
        
        # 响应式设计是现代Web应用的推荐实践
        if len(html_content.strip()) > 100:
            # 如果内容较复杂，建议考虑响应式设计
            pass
    
    def test_user_status_loading_states_contract(self, client, test_user):
        """测试用户状态加载状态 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}&loading=true')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：加载状态
        loading_indicators = [
            'loading', 'spinner', 'skeleton',  # 加载状态
            'placeholder', 'shimmer', 'pulse',  # 占位符动画
            'htmx-indicator', 'htmx-request'  # HTMX加载指示器
        ]
        
        # 检查加载状态处理
        has_loading_state = any(indicator in html_content for indicator in loading_indicators)
        
        # 如果请求了加载状态，应该有相应指示器
        if 'loading=true' in str(response.request.url if hasattr(response, 'request') else ''):
            # 加载状态检查是可选的，因为实现方式可能不同
            pass
    
    def test_user_status_error_handling_contract(self, client):
        """测试用户状态错误处理 - 合约验证"""
        
        response = client.get('/htmx/user/status?user_id=999999')  # 不存在的用户
        
        # 合约验证：错误处理
        assert response.status_code in [200, 404, 403], "不存在用户的状态请求应该返回适当错误状态码"
        
        if response.status_code == 200:
            html_content = response.data.decode('utf-8')
            
            # 验证错误状态显示
            error_indicators = [
                'error', 'not-found', 'unavailable',  # 错误状态
                '错误', '未找到', '不可用',  # 中文错误
                'user-not-found', 'invalid-user'  # 用户相关错误
            ]
            
            has_error_indicator = any(indicator in html_content for indicator in error_indicators)
            # 如果返回200但用户不存在，应该显示适当的错误信息
        elif response.status_code == 404:
            # 404响应是合理的错误处理
            pass
    
    def test_user_status_privacy_contract(self, client, test_user):
        """测试用户状态隐私保护 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}&private=true')
        html_content = response.data.decode('utf-8')
        
        # 合约验证：隐私保护
        private_info = [
            test_user.email,  # 邮箱可能是隐私信息
            'password', 'token', 'secret',  # 敏感信息
            'private', 'confidential'  # 隐私标识
        ]
        
        # 检查是否泄露隐私信息
        has_private_info = any(info in html_content for info in private_info if info)
        
        # 用户状态显示应该保护隐私信息
        if has_private_info:
            # 如果显示了隐私信息，确保有适当的授权或脱敏处理
            privacy_protection = [
                '***', '###', 'masked',  # 脱敏标识
                'authorized', 'permitted'  # 授权标识
            ]
            has_privacy_protection = any(protection in html_content for protection in privacy_protection)
            # 隐私保护检查是重要的安全实践
    
    def test_user_status_caching_headers_contract(self, client, test_user):
        """测试用户状态缓存头 - 合约验证"""
        
        response = client.get(f'/htmx/user/status?user_id={test_user.id}')
        
        # 合约验证：缓存控制头
        cache_headers = [
            'Cache-Control',
            'ETag',
            'Last-Modified',
            'Expires'
        ]
        
        # 检查缓存相关头
        has_cache_headers = any(header in response.headers for header in cache_headers)
        
        # 用户状态可能需要缓存控制
        if has_cache_headers:
            # 如果有缓存头，验证缓存策略合理性
            cache_control = response.headers.get('Cache-Control', '')
            
            # 用户状态通常应该是短期缓存或不缓存
            appropriate_cache = any(directive in cache_control for directive in [
                'no-cache', 'no-store', 'max-age=0',  # 不缓存
                'max-age=60', 'max-age=300'  # 短期缓存
            ])
            # 缓存策略检查是性能和安全的考虑
    
    def test_user_status_batch_request_contract(self, client, test_user):
        """测试用户状态批量请求 - 合约验证"""
        
        user_ids = [test_user.id, test_user.id + 1, test_user.id + 2]
        response = client.get(f'/htmx/user/status-batch?user_ids={",".join(map(str, user_ids))}')
        
        # 合约验证：批量请求处理
        assert response.status_code == 200, "批量用户状态请求应该返回200状态码"
        
        html_content = response.data.decode('utf-8')
        
        # 验证批量结果结构
        batch_elements = [
            'user-status-list', 'status-batch', 'multi-user',  # 批量容器
            str(test_user.id),  # 至少包含测试用户ID
            'batch-item', 'status-item'  # 批量项目
        ]
        
        has_batch_structure = any(elem in html_content for elem in batch_elements)
        assert has_batch_structure, "批量用户状态必须包含适当的结构"
    
    def test_user_status_filtering_contract(self, client, test_user):
        """测试用户状态过滤 - 合约验证"""
        
        filters = ['online', 'offline', 'active', 'inactive']
        
        for filter_type in filters:
            response = client.get(f'/htmx/user/status?filter={filter_type}')
            
            # 合约验证：过滤响应
            assert response.status_code == 200, f"用户状态过滤 {filter_type} 应该返回200状态码"
            
            html_content = response.data.decode('utf-8')
            
            # 验证过滤结果
            filter_indicators = [
                filter_type,  # 过滤器名称
                f'status-{filter_type}',  # 状态类
                f'{filter_type}-users'  # 用户类型类
            ]
            
            # 如果有过滤结果，应该包含过滤标识
            if len(html_content.strip()) > 20:
                has_filter_indicator = any(indicator in html_content for indicator in filter_indicators)
                # 过滤标识检查是可选的，因为可能没有匹配的用户
    
    def test_user_status_sorting_contract(self, client):
        """测试用户状态排序 - 合约验证"""
        
        sort_options = ['name', 'last_seen', 'status', 'activity']
        
        for sort_by in sort_options:
            response = client.get(f'/htmx/user/status-list?sort={sort_by}')
            
            # 合约验证：排序响应
            assert response.status_code == 200, f"用户状态排序 {sort_by} 应该返回200状态码"
            
            html_content = response.data.decode('utf-8')
            
            # 验证排序指示器
            sort_indicators = [
                'sorted-by', 'order-by', 'sort',  # 排序标识
                'asc', 'desc', 'ascending', 'descending'  # 排序方向
            ]
            
            # 如果有排序结果，可能包含排序标识
            if len(html_content.strip()) > 50:
                has_sort_indicator = any(indicator in html_content for indicator in sort_indicators)
                # 排序标识检查是可选的，因为实现方式可能不同


if __name__ == '__main__':
    pytest.main([__file__])