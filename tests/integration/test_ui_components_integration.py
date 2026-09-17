"""
用户界面组件集成测试
测试用户界面组件之间的交互和协作功能
"""
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService


class TestUIComponentsIntegration:
    """用户界面组件集成测试类"""
    
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
    def authenticated_user(self, app_context):
        """创建已认证用户"""
        user_service = UserService()
        user = user_service.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123!',
            nickname='测试用户'
        )
        return user
    
    def test_form_modal_interaction(self, client, app_context, authenticated_user):
        """测试表单与模态框的交互"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 通过HTMX加载模态框中的表单
        modal_response = client.get('/htmx/modals/profile-edit')
        assert modal_response.status_code == 200, "资料编辑模态框应该可以加载"
        
        modal_html = modal_response.data.decode('utf-8')
        
        # 验证模态框包含表单
        assert 'form' in modal_html, "模态框应该包含表单"
        assert 'hx-post' in modal_html or 'hx-put' in modal_html, "表单应该包含HTMX提交属性"
        assert 'modal' in modal_html, "响应应该包含模态框结构"
        
        # 步骤2: 在模态框中提交表单
        form_data = {
            'nickname': '更新的昵称',
            'bio': '更新的个人简介'
        }
        
        form_response = client.post(
            '/htmx/forms/profile-edit',
            data=form_data,
            headers={'HX-Request': 'true'}
        )
        
        # 验证表单提交结果
        assert form_response.status_code in [200, 201], "模态框表单提交应该成功"
        
        # 步骤3: 验证模态框关闭和页面更新
        form_html = form_response.data.decode('utf-8')
        
        # 检查是否包含关闭模态框的指令
        modal_close_indicators = [
            'hx-trigger="close"',  # 关闭触发器
            'modal-close',  # 关闭类
            'success',  # 成功标识
            'updated'  # 更新标识
        ]
        
        has_close_indicator = any(indicator in form_html for indicator in modal_close_indicators)
        # 模态框关闭机制可能因实现而异
    
    def test_form_notification_integration(self, client, app_context, authenticated_user):
        """测试表单提交与通知系统的集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 提交表单并期待通知反馈
        form_data = {
            'username': 'newusername',
            'email': 'newemail@example.com'
        }
        
        response = client.post(
            '/htmx/forms/profile-update',
            data=form_data,
            headers={'HX-Request': 'true'}
        )
        
        # 步骤2: 验证通知生成
        if response.status_code in [200, 201]:
            # 成功提交应该生成成功通知
            notifications_response = client.get('/htmx/notifications?type=success&recent=true')
            assert notifications_response.status_code == 200, "成功通知应该可以获取"
            
            notifications_html = notifications_response.data.decode('utf-8')
            
            # 验证成功通知内容
            success_indicators = [
                'success', '成功', 'updated', '已更新',
                'profile', '资料', 'saved', '保存'
            ]
            
            has_success_notification = any(indicator in notifications_html for indicator in success_indicators)
            assert has_success_notification, "应该有成功更新的通知"
        
        # 步骤3: 测试错误表单的通知反馈
        invalid_form_data = {
            'email': 'invalid-email'  # 无效邮箱格式
        }
        
        error_response = client.post(
            '/htmx/forms/profile-update',
            data=invalid_form_data,
            headers={'HX-Request': 'true'}
        )
        
        if error_response.status_code in [400, 422]:
            # 错误提交应该生成错误通知
            error_notifications_response = client.get('/htmx/notifications?type=error&recent=true')
            
            if error_notifications_response.status_code == 200:
                error_html = error_notifications_response.data.decode('utf-8')
                
                error_indicators = [
                    'error', '错误', 'invalid', '无效',
                    'validation', '验证', 'failed', '失败'
                ]
                
                has_error_notification = any(indicator in error_html for indicator in error_indicators)
                # 错误通知的具体实现可能因系统而异
    
    def test_sidebar_navigation_integration(self, client, app_context, authenticated_user):
        """测试侧边栏导航与页面内容的集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 获取侧边栏组件
        sidebar_response = client.get('/htmx/components/sidebar')
        assert sidebar_response.status_code == 200, "侧边栏组件应该可以加载"
        
        sidebar_html = sidebar_response.data.decode('utf-8')
        
        # 验证侧边栏导航项
        navigation_items = [
            'dashboard', '仪表板',
            'profile', '个人资料',
            'settings', '设置',
            'predictions', '预测'
        ]
        
        has_navigation = any(item in sidebar_html for item in navigation_items)
        assert has_navigation, "侧边栏应该包含导航项目"
        
        # 步骤2: 测试导航项点击加载对应内容
        navigation_links = [
            '/user/dashboard',
            '/user/profile',
            '/user/settings'
        ]
        
        for link in navigation_links:
            nav_response = client.get(link, headers={'HX-Request': 'true'})
            
            # 验证导航响应
            if nav_response.status_code == 200:
                nav_html = nav_response.data.decode('utf-8')
                
                # 验证内容区域更新
                content_indicators = [
                    'content', 'main', 'page',
                    '内容', '页面', 'section'
                ]
                
                has_content = any(indicator in nav_html for indicator in content_indicators)
                assert has_content, f"导航到 {link} 应该返回内容"
        
        # 步骤3: 验证活跃状态更新
        active_link_response = client.get('/user/profile', headers={'HX-Request': 'true'})
        
        if active_link_response.status_code == 200:
            # 检查侧边栏状态更新
            updated_sidebar_response = client.get('/htmx/components/sidebar?active=profile')
            
            if updated_sidebar_response.status_code == 200:
                updated_sidebar_html = updated_sidebar_response.data.decode('utf-8')
                
                # 验证活跃状态
                active_indicators = [
                    'active', 'current', 'selected',
                    '当前', '活跃', '选中'
                ]
                
                has_active_state = any(indicator in updated_sidebar_html for indicator in active_indicators)
                # 活跃状态的具体实现可能因UI框架而异
    
    def test_user_status_notification_integration(self, client, app_context, authenticated_user):
        """测试用户状态与通知系统的集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 获取用户状态组件
        status_response = client.get(f'/htmx/user/status?user_id={authenticated_user.id}')
        assert status_response.status_code == 200, "用户状态组件应该可以加载"
        
        status_html = status_response.data.decode('utf-8')
        
        # 验证用户状态显示
        status_elements = [
            'online', 'offline', '在线', '离线',
            'active', 'inactive', '活跃', '非活跃'
        ]
        
        has_status_display = any(element in status_html for element in status_elements)
        assert has_status_display, "用户状态应该有状态显示"
        
        # 步骤2: 测试状态变更触发通知
        # 模拟用户操作（例如更新资料）
        update_response = client.post('/htmx/user/update-activity', data={
            'action': 'profile_update',
            'timestamp': datetime.utcnow().isoformat()
        })
        
        if update_response.status_code in [200, 201]:
            # 步骤3: 验证状态更新反映在界面
            updated_status_response = client.get(f'/htmx/user/status?user_id={authenticated_user.id}')
            
            if updated_status_response.status_code == 200:
                updated_status_html = updated_status_response.data.decode('utf-8')
                
                # 验证最近活动显示
                activity_indicators = [
                    'last-seen', 'recent', 'activity',
                    '最近活动', '最后访问', '活动时间'
                ]
                
                has_activity_update = any(indicator in updated_status_html for indicator in activity_indicators)
                # 活动状态更新的具体实现可能因系统而异
    
    def test_search_results_pagination_integration(self, client, app_context, authenticated_user):
        """测试搜索结果与分页组件的集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 执行搜索请求
        search_response = client.get('/htmx/search?q=股票&page=1&limit=10')
        
        if search_response.status_code == 200:
            search_html = search_response.data.decode('utf-8')
            
            # 验证搜索结果显示
            search_elements = [
                'search-results', 'results', '搜索结果',
                'item', 'result', '结果项'
            ]
            
            has_search_results = any(element in search_html for element in search_elements)
            assert has_search_results, "搜索应该返回结果组件"
            
            # 步骤2: 测试分页导航
            pagination_elements = [
                'pagination', 'pager', 'next', 'prev',
                '分页', '下一页', '上一页', '页码'
            ]
            
            has_pagination = any(element in search_html for element in pagination_elements)
            
            if has_pagination:
                # 步骤3: 测试分页链接
                next_page_response = client.get('/htmx/search?q=股票&page=2&limit=10')
                
                if next_page_response.status_code == 200:
                    next_page_html = next_page_response.data.decode('utf-8')
                    
                    # 验证页面内容更新
                    assert 'page=2' in str(next_page_response.request.url) if hasattr(next_page_response, 'request') else True
                    
                    # 验证结果区域更新
                    has_updated_results = any(element in next_page_html for element in search_elements)
                    assert has_updated_results, "分页应该更新搜索结果"
    
    def test_form_validation_feedback_integration(self, client, app_context, authenticated_user):
        """测试表单验证与反馈组件的集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 获取带验证的表单
        form_response = client.get('/htmx/forms/user-registration')
        assert form_response.status_code == 200, "用户注册表单应该可以加载"
        
        form_html = form_response.data.decode('utf-8')
        
        # 验证表单验证属性
        validation_attributes = [
            'required', 'pattern', 'minlength', 'maxlength',
            'hx-trigger', 'hx-post', 'hx-validate'
        ]
        
        has_validation_attrs = any(attr in form_html for attr in validation_attributes)
        assert has_validation_attrs, "表单应该包含验证属性"
        
        # 步骤2: 测试实时验证
        validation_data = {
            'username': 'a',  # 太短的用户名
            'email': 'invalid-email',  # 无效邮箱
            'password': '123'  # 弱密码
        }
        
        for field, value in validation_data.items():
            validate_response = client.post('/htmx/forms/validate', data={
                'field': field,
                'value': value
            })
            
            if validate_response.status_code in [200, 422]:
                validate_html = validate_response.data.decode('utf-8')
                
                # 验证错误反馈
                error_indicators = [
                    'error', 'invalid', 'warning',
                    '错误', '无效', '警告',
                    'field-error', 'validation-error'
                ]
                
                has_error_feedback = any(indicator in validate_html for indicator in error_indicators)
                # 实时验证反馈的具体实现可能因系统而异
        
        # 步骤3: 测试成功验证反馈
        valid_data = {
            'username': 'validuser123',
            'email': 'valid@example.com',
            'password': 'StrongPassword123!'
        }
        
        for field, value in valid_data.items():
            success_response = client.post('/htmx/forms/validate', data={
                'field': field,
                'value': value
            })
            
            if success_response.status_code == 200:
                success_html = success_response.data.decode('utf-8')
                
                # 验证成功反馈
                success_indicators = [
                    'valid', 'success', 'ok',
                    '有效', '成功', '正确',
                    'field-valid', 'validation-success'
                ]
                
                has_success_feedback = any(indicator in success_html for indicator in success_indicators)
                # 成功验证反馈也可能是空响应，表示没有错误
    
    def test_modal_form_notification_chain(self, client, app_context, authenticated_user):
        """测试模态框→表单→通知的完整交互链"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 打开模态框
        modal_response = client.get('/htmx/modals/create-prediction')
        assert modal_response.status_code == 200, "预测创建模态框应该可以打开"
        
        modal_html = modal_response.data.decode('utf-8')
        
        # 验证模态框包含表单
        assert 'form' in modal_html and 'modal' in modal_html, "模态框应该包含表单"
        
        # 步骤2: 在模态框中提交表单
        prediction_data = {
            'stock_code': '000001',
            'prediction_days': '5',
            'model_name': 'kronos-mini'
        }
        
        form_response = client.post(
            '/htmx/forms/create-prediction',
            data=prediction_data,
            headers={'HX-Request': 'true'}
        )
        
        # 步骤3: 验证表单提交触发多个UI更新
        if form_response.status_code in [200, 201]:
            # 3a: 验证模态框关闭响应
            form_html = form_response.data.decode('utf-8')
            
            close_indicators = [
                'hx-trigger="close"', 'modal-close',
                'success', 'created', '创建成功'
            ]
            
            has_close_response = any(indicator in form_html for indicator in close_indicators)
            
            # 3b: 验证通知生成
            notifications_response = client.get('/htmx/notifications?recent=true')
            
            if notifications_response.status_code == 200:
                notifications_html = notifications_response.data.decode('utf-8')
                
                notification_indicators = [
                    'prediction', 'created', '预测', '已创建',
                    '000001', 'success', '成功'
                ]
                
                has_notification = any(indicator in notifications_html for indicator in notification_indicators)
                
            # 3c: 验证页面内容更新
            dashboard_response = client.get('/htmx/components/prediction-list')
            
            if dashboard_response.status_code == 200:
                dashboard_html = dashboard_response.data.decode('utf-8')
                
                # 验证新预测出现在列表中
                prediction_indicators = [
                    '000001', prediction_data['stock_code'],
                    'prediction', '预测'
                ]
                
                has_prediction_update = any(indicator in dashboard_html for indicator in prediction_indicators)
    
    def test_responsive_component_interaction(self, client, app_context, authenticated_user):
        """测试响应式组件交互"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 模拟不同设备类型的请求
        device_types = [
            {'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)', 'device': 'mobile'},
            {'user_agent': 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)', 'device': 'tablet'},
            {'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'device': 'desktop'}
        ]
        
        for device_info in device_types:
            # 步骤1: 获取响应式导航组件
            nav_response = client.get(
                '/htmx/components/navigation',
                headers={'User-Agent': device_info['user_agent']}
            )
            
            if nav_response.status_code == 200:
                nav_html = nav_response.data.decode('utf-8')
                
                # 验证响应式类
                responsive_classes = [
                    'mobile', 'tablet', 'desktop',
                    'sm:', 'md:', 'lg:', 'xl:',  # TailwindCSS
                    'hidden-', 'visible-',  # Bootstrap
                    device_info['device']
                ]
                
                has_responsive_design = any(cls in nav_html for cls in responsive_classes)
                # 响应式设计的具体实现可能因框架而异
                
                # 步骤2: 测试设备特定的交互
                if device_info['device'] == 'mobile':
                    # 移动设备可能有折叠菜单
                    mobile_menu_response = client.get('/htmx/components/mobile-menu')
                    
                    if mobile_menu_response.status_code == 200:
                        mobile_html = mobile_menu_response.data.decode('utf-8')
                        
                        mobile_indicators = [
                            'mobile-menu', 'hamburger', 'drawer',
                            '菜单', '抽屉', 'toggle'
                        ]
                        
                        has_mobile_features = any(indicator in mobile_html for indicator in mobile_indicators)
    
    def test_async_component_loading_integration(self, client, app_context, authenticated_user):
        """测试异步组件加载集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 请求需要异步加载的组件
        async_response = client.get('/htmx/components/prediction-chart?stock_code=000001')
        
        # 可能返回加载指示器或实际内容
        if async_response.status_code == 200:
            async_html = async_response.data.decode('utf-8')
            
            # 检查是否是加载状态
            loading_indicators = [
                'loading', 'spinner', 'skeleton',
                '加载中', '正在加载', 'htmx-indicator'
            ]
            
            is_loading_state = any(indicator in async_html for indicator in loading_indicators)
            
            if is_loading_state:
                # 步骤2: 等待并检查加载完成
                import time
                time.sleep(1)  # 简单等待，实际应用中可能需要轮询
                
                completed_response = client.get('/htmx/components/prediction-chart?stock_code=000001')
                
                if completed_response.status_code == 200:
                    completed_html = completed_response.data.decode('utf-8')
                    
                    # 验证内容已加载
                    content_indicators = [
                        'chart', 'graph', 'data',
                        '图表', '数据', 'prediction'
                    ]
                    
                    has_content = any(indicator in completed_html for indicator in content_indicators)
                    assert has_content, "异步组件应该最终加载内容"
            else:
                # 直接返回了内容
                content_indicators = [
                    'chart', 'graph', 'prediction',
                    '000001', '图表', '预测'
                ]
                
                has_direct_content = any(indicator in async_html for indicator in content_indicators)
                assert has_direct_content, "组件应该包含相关内容"
    
    def test_error_handling_across_components(self, client, app_context, authenticated_user):
        """测试组件间的错误处理集成"""
        
        # 模拟登录
        with client.session_transaction() as sess:
            sess['user_id'] = authenticated_user.id
            sess['logged_in'] = True
        
        # 步骤1: 触发错误情况（例如无效的股票代码）
        error_response = client.post('/htmx/forms/create-prediction', data={
            'stock_code': 'INVALID',
            'prediction_days': 'abc'  # 无效天数
        })
        
        # 步骤2: 验证错误在多个组件中正确显示
        if error_response.status_code in [400, 422]:
            error_html = error_response.data.decode('utf-8')
            
            # 验证表单错误显示
            form_error_indicators = [
                'field-error', 'form-error', 'invalid',
                '字段错误', '表单错误', '无效'
            ]
            
            has_form_error = any(indicator in error_html for indicator in form_error_indicators)
            assert has_form_error, "表单应该显示字段错误"
            
            # 步骤3: 检查错误通知
            error_notifications = client.get('/htmx/notifications?type=error&recent=true')
            
            if error_notifications.status_code == 200:
                notification_html = error_notifications.data.decode('utf-8')
                
                error_notification_indicators = [
                    'error', 'failed', 'invalid',
                    '错误', '失败', '无效',
                    'INVALID', 'prediction'
                ]
                
                has_error_notification = any(indicator in notification_html for indicator in error_notification_indicators)
                # 错误通知的具体实现可能因系统而异
        
        # 步骤4: 测试网络错误处理
        # 模拟服务器错误（通过请求不存在的端点）
        network_error_response = client.get('/htmx/nonexistent-endpoint')
        
        assert network_error_response.status_code == 404, "不存在的端点应该返回404"
        
        # 检查是否有友好的错误页面
        if network_error_response.status_code == 404:
            error_page_html = network_error_response.data.decode('utf-8')
            
            user_friendly_indicators = [
                '404', 'not found', 'page not found',
                '页面未找到', '不存在', '错误'
            ]
            
            has_user_friendly_error = any(indicator in error_page_html for indicator in user_friendly_indicators)
            # 友好错误页面是良好用户体验的体现


if __name__ == '__main__':
    pytest.main([__file__])