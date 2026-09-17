"""
错误提示优化组件
提供用户友好的错误消息、多级别提示、自动恢复建议等
"""
from typing import Dict, List, Optional, Any, Tuple
from flask import current_app, request, session
from datetime import datetime, timedelta
import json
import traceback
import re


class ErrorManager:
    """错误管理器"""
    
    def __init__(self):
        # 错误级别定义
        self.error_levels = {
            'info': {
                'name': '信息',
                'color': 'blue',
                'icon': 'info-circle',
                'priority': 1,
                'auto_dismiss': True,
                'duration': 5000
            },
            'success': {
                'name': '成功',
                'color': 'green', 
                'icon': 'check-circle',
                'priority': 2,
                'auto_dismiss': True,
                'duration': 4000
            },
            'warning': {
                'name': '警告',
                'color': 'yellow',
                'icon': 'exclamation-triangle',
                'priority': 3,
                'auto_dismiss': True,
                'duration': 6000
            },
            'error': {
                'name': '错误',
                'color': 'red',
                'icon': 'exclamation-circle',
                'priority': 4,
                'auto_dismiss': False,
                'duration': 0
            },
            'critical': {
                'name': '严重错误',
                'color': 'red',
                'icon': 'times-circle',
                'priority': 5,
                'auto_dismiss': False,
                'duration': 0
            }
        }
        
        # 常见错误类型和用户友好消息
        self.error_messages = {
            'validation_error': {
                'title': '输入验证失败',
                'message': '请检查您输入的信息是否正确',
                'suggestions': [
                    '确保所有必填字段已填写',
                    '检查邮箱、手机号等格式是否正确',
                    '密码长度和复杂度是否符合要求'
                ]
            },
            'network_error': {
                'title': '网络连接问题',
                'message': '无法连接到服务器，请检查网络连接',
                'suggestions': [
                    '检查网络连接是否正常',
                    '稍后重试',
                    '刷新页面重新加载'
                ]
            },
            'server_error': {
                'title': '服务器错误',
                'message': '服务器遇到问题，我们正在努力修复',
                'suggestions': [
                    '稍后重试',
                    '联系技术支持',
                    '保存您的工作内容'
                ]
            },
            'permission_denied': {
                'title': '权限不足',
                'message': '您没有执行此操作的权限',
                'suggestions': [
                    '联系管理员获取权限',
                    '检查是否已登录',
                    '使用有权限的账户'
                ]
            },
            'not_found': {
                'title': '资源不存在',
                'message': '请求的资源未找到',
                'suggestions': [
                    '检查URL是否正确',
                    '返回首页重新导航',
                    '联系客服寻求帮助'
                ]
            },
            'timeout_error': {
                'title': '请求超时',
                'message': '操作时间过长，请求已超时',
                'suggestions': [
                    '重新尝试操作',
                    '检查网络连接速度',
                    '联系技术支持'
                ]
            },
            'file_upload_error': {
                'title': '文件上传失败',
                'message': '文件上传过程中发生错误',
                'suggestions': [
                    '检查文件大小是否超出限制',
                    '确认文件格式是否支持',
                    '重新选择文件上传'
                ]
            },
            'data_processing_error': {
                'title': '数据处理失败',
                'message': '数据处理过程中遇到问题',
                'suggestions': [
                    '检查数据格式是否正确',
                    '重新提交数据',
                    '联系技术支持'
                ]
            }
        }
        
        # 错误恢复策略
        self.recovery_strategies = {
            'retry': {
                'name': '重试操作',
                'action': 'retry',
                'automatic': True,
                'max_attempts': 3,
                'delay': 1000
            },
            'refresh': {
                'name': '刷新页面',
                'action': 'refresh',
                'automatic': False
            },
            'redirect': {
                'name': '返回安全页面',
                'action': 'redirect',
                'automatic': False,
                'target': '/'
            },
            'contact_support': {
                'name': '联系技术支持',
                'action': 'contact',
                'automatic': False,
                'email': 'support@example.com',
                'phone': '400-123-4567'
            }
        }
    
    def classify_error(self, error: Exception, context: Dict = None) -> str:
        """分类错误类型"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # 根据异常类型分类
        if 'validation' in error_type.lower() or 'invalid' in error_message:
            return 'validation_error'
        elif 'connection' in error_message or 'network' in error_message:
            return 'network_error'
        elif 'permission' in error_message or 'forbidden' in error_message:
            return 'permission_denied'
        elif 'not found' in error_message or '404' in error_message:
            return 'not_found'
        elif 'timeout' in error_message:
            return 'timeout_error'
        elif 'upload' in error_message:
            return 'file_upload_error'
        elif 'data' in error_message or 'processing' in error_message:
            return 'data_processing_error'
        else:
            return 'server_error'
    
    def create_error_response(self, error: Exception, error_type: str = None,
                            context: Dict = None, user_friendly: bool = True) -> Dict[str, Any]:
        """创建错误响应"""
        if error_type is None:
            error_type = self.classify_error(error, context)
        
        # 获取错误模板
        error_template = self.error_messages.get(error_type, self.error_messages['server_error'])
        
        # 基础错误信息
        error_response = {
            'success': False,
            'error': {
                'type': error_type,
                'code': getattr(error, 'code', 500),
                'title': error_template['title'],
                'message': error_template['message'] if user_friendly else str(error),
                'timestamp': datetime.utcnow().isoformat(),
                'level': self._determine_error_level(error_type),
                'suggestions': error_template['suggestions'],
                'recovery_options': self._get_recovery_options(error_type)
            }
        }
        
        # 添加上下文信息
        if context:
            error_response['error']['context'] = context
        
        # 开发环境下添加详细信息
        if current_app.debug and not user_friendly:
            error_response['error']['details'] = {
                'exception_type': type(error).__name__,
                'exception_message': str(error),
                'traceback': traceback.format_exc()
            }
        
        return error_response
    
    def _determine_error_level(self, error_type: str) -> str:
        """确定错误级别"""
        level_mapping = {
            'validation_error': 'warning',
            'network_error': 'error',
            'server_error': 'error',
            'permission_denied': 'warning',
            'not_found': 'warning',
            'timeout_error': 'warning',
            'file_upload_error': 'error',
            'data_processing_error': 'error'
        }
        
        return level_mapping.get(error_type, 'error')
    
    def _get_recovery_options(self, error_type: str) -> List[Dict]:
        """获取错误恢复选项"""
        recovery_mapping = {
            'validation_error': ['retry'],
            'network_error': ['retry', 'refresh'],
            'server_error': ['retry', 'contact_support'],
            'permission_denied': ['redirect', 'contact_support'],
            'not_found': ['redirect', 'refresh'],
            'timeout_error': ['retry', 'refresh'],
            'file_upload_error': ['retry'],
            'data_processing_error': ['retry', 'contact_support']
        }
        
        strategy_keys = recovery_mapping.get(error_type, ['retry'])
        return [self.recovery_strategies[key] for key in strategy_keys if key in self.recovery_strategies]
    
    def create_notification_html(self, level: str, title: str, message: str,
                               suggestions: List[str] = None, 
                               recovery_options: List[Dict] = None,
                               dismissible: bool = True,
                               notification_id: str = None) -> str:
        """创建通知HTML"""
        if notification_id is None:
            notification_id = f"notification-{datetime.utcnow().timestamp()}"
        
        level_config = self.error_levels.get(level, self.error_levels['info'])
        
        # 构建通知HTML
        notification_html = f'''
        <div id="{notification_id}" 
             class="notification notification-{level} bg-{level_config['color']}-50 border border-{level_config['color']}-200 rounded-lg p-4 mb-4 shadow-sm"
             role="alert"
             aria-live="{'assertive' if level in ['error', 'critical'] else 'polite'}"
             aria-labelledby="{notification_id}-title"
             aria-describedby="{notification_id}-message"
             data-level="{level}"
             data-priority="{level_config['priority']}"
             {f'data-auto-dismiss="true" data-duration="{level_config["duration"]}"' if level_config["auto_dismiss"] else ''}>
            
            <div class="flex items-start space-x-3">
                <!-- 图标 -->
                <div class="flex-shrink-0">
                    <i class="fas fa-{level_config['icon']} text-{level_config['color']}-500 text-lg"></i>
                </div>
                
                <!-- 内容区 -->
                <div class="flex-grow min-w-0">
                    <h4 id="{notification_id}-title" 
                        class="text-sm font-semibold text-{level_config['color']}-800 mb-1">
                        {title}
                    </h4>
                    
                    <p id="{notification_id}-message" 
                       class="text-sm text-{level_config['color']}-700 mb-2">
                        {message}
                    </p>
                    
                    <!-- 建议列表 -->
                    {self._create_suggestions_html(suggestions, level_config['color']) if suggestions else ''}
                    
                    <!-- 恢复选项 -->
                    {self._create_recovery_options_html(recovery_options, notification_id) if recovery_options else ''}
                </div>
                
                <!-- 关闭按钮 -->
                {f'''
                <div class="flex-shrink-0">
                    <button class="notification-close-btn inline-flex text-{level_config['color']}-400 hover:text-{level_config['color']}-600 focus:outline-none focus:ring-2 focus:ring-{level_config['color']}-500 rounded"
                            onclick="dismissNotification('{notification_id}')"
                            aria-label="关闭通知">
                        <i class="fas fa-times text-sm"></i>
                    </button>
                </div>
                ''' if dismissible else ''}
            </div>
        </div>
        '''
        
        return notification_html
    
    def _create_suggestions_html(self, suggestions: List[str], color: str) -> str:
        """创建建议列表HTML"""
        if not suggestions:
            return ''
        
        suggestions_html = f'''
        <div class="mt-2">
            <p class="text-xs font-medium text-{color}-800 mb-1">建议解决方案：</p>
            <ul class="text-xs text-{color}-700 space-y-1">
        '''
        
        for suggestion in suggestions:
            suggestions_html += f'''
                <li class="flex items-start space-x-1">
                    <span class="text-{color}-500 mt-0.5">•</span>
                    <span>{suggestion}</span>
                </li>
            '''
        
        suggestions_html += '''
            </ul>
        </div>
        '''
        
        return suggestions_html
    
    def _create_recovery_options_html(self, recovery_options: List[Dict], 
                                    notification_id: str) -> str:
        """创建恢复选项HTML"""
        if not recovery_options:
            return ''
        
        options_html = '''
        <div class="mt-3 flex flex-wrap gap-2">
        '''
        
        for option in recovery_options:
            button_class = 'btn btn-sm btn-outline-primary' if option['action'] != 'retry' else 'btn btn-sm btn-primary'
            
            options_html += f'''
            <button class="{button_class} recovery-option-btn"
                    data-action="{option['action']}"
                    data-notification-id="{notification_id}"
                    onclick="handleRecoveryAction('{option['action']}', '{notification_id}')">
                <i class="fas fa-{self._get_action_icon(option['action'])} mr-1"></i>
                {option['name']}
            </button>
            '''
        
        options_html += '''
        </div>
        '''
        
        return options_html
    
    def _get_action_icon(self, action: str) -> str:
        """获取操作图标"""
        icon_mapping = {
            'retry': 'redo',
            'refresh': 'sync',
            'redirect': 'home',
            'contact': 'envelope'
        }
        
        return icon_mapping.get(action, 'cog')
    
    def get_error_styles(self) -> str:
        """获取错误样式CSS"""
        css_styles = '''
        /* 通知样式 */
        .notification {
            transition: all 0.3s ease-in-out;
            animation: slideInDown 0.3s ease-out;
        }
        
        .notification.notification-dismissing {
            animation: slideOutUp 0.3s ease-in;
            opacity: 0;
            transform: translateY(-20px);
        }
        
        @keyframes slideInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideOutUp {
            from {
                opacity: 1;
                transform: translateY(0);
            }
            to {
                opacity: 0;
                transform: translateY(-20px);
            }
        }
        
        .notification-close-btn {
            transition: all 0.2s ease;
        }
        
        .recovery-option-btn {
            transition: all 0.2s ease;
        }
        
        .recovery-option-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* 通知容器 */
        .notifications-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            max-width: 400px;
            pointer-events: none;
        }
        
        .notifications-container .notification {
            pointer-events: all;
            margin-bottom: 10px;
        }
        
        /* 响应式适配 */
        @media (max-width: 640px) {
            .notifications-container {
                top: 10px;
                right: 10px;
                left: 10px;
                max-width: none;
            }
            
            .notification {
                font-size: 0.875rem;
            }
        }
        
        /* 高对比度模式 */
        @media (prefers-contrast: high) {
            .notification {
                border-width: 2px;
            }
        }
        
        /* 减少动画模式 */
        @media (prefers-reduced-motion: reduce) {
            .notification {
                animation: none !important;
                transition: none !important;
            }
        }
        '''
        
        return css_styles
    
    def get_error_javascript(self) -> str:
        """获取错误处理JavaScript"""
        js_code = '''
        // 错误处理和通知管理
        class NotificationManager {
            constructor() {
                this.container = null;
                this.notifications = new Map();
                this.autoCloseTimers = new Map();
                this.init();
            }
            
            init() {
                // 创建通知容器
                this.container = document.createElement('div');
                this.container.className = 'notifications-container';
                this.container.setAttribute('aria-live', 'polite');
                this.container.setAttribute('aria-label', '通知区域');
                document.body.appendChild(this.container);
            }
            
            // 显示通知
            show(level, title, message, options = {}) {
                const notificationId = options.id || `notification-${Date.now()}`;
                
                // 创建通知元素
                const notification = this.createNotification(level, title, message, {
                    ...options,
                    id: notificationId
                });
                
                // 添加到容器
                this.container.appendChild(notification);
                this.notifications.set(notificationId, notification);
                
                // 设置自动关闭
                if (options.autoDismiss !== false && options.duration > 0) {
                    this.setAutoClose(notificationId, options.duration);
                }
                
                return notificationId;
            }
            
            // 创建通知元素
            createNotification(level, title, message, options = {}) {
                const notification = document.createElement('div');
                const notificationId = options.id || `notification-${Date.now()}`;
                
                notification.id = notificationId;
                notification.className = `notification notification-${level}`;
                notification.setAttribute('role', 'alert');
                notification.setAttribute('aria-live', level === 'error' ? 'assertive' : 'polite');
                
                // 构建内容
                let suggestionsHtml = '';
                if (options.suggestions && options.suggestions.length > 0) {
                    suggestionsHtml = `
                        <div class="mt-2">
                            <p class="text-xs font-medium mb-1">建议解决方案：</p>
                            <ul class="text-xs space-y-1">
                                ${options.suggestions.map(s => `<li>• ${s}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
                
                let recoveryHtml = '';
                if (options.recoveryOptions && options.recoveryOptions.length > 0) {
                    recoveryHtml = `
                        <div class="mt-3 flex flex-wrap gap-2">
                            ${options.recoveryOptions.map(option => `
                                <button class="btn btn-sm btn-outline-primary recovery-option-btn"
                                        data-action="${option.action}"
                                        onclick="handleRecoveryAction('${option.action}', '${notificationId}')">
                                    ${option.name}
                                </button>
                            `).join('')}
                        </div>
                    `;
                }
                
                notification.innerHTML = `
                    <div class="flex items-start space-x-3 p-4">
                        <div class="flex-shrink-0">
                            <i class="fas fa-${this.getLevelIcon(level)} text-lg"></i>
                        </div>
                        <div class="flex-grow min-w-0">
                            <h4 class="text-sm font-semibold mb-1">${title}</h4>
                            <p class="text-sm mb-2">${message}</p>
                            ${suggestionsHtml}
                            ${recoveryHtml}
                        </div>
                        ${options.dismissible !== false ? `
                        <div class="flex-shrink-0">
                            <button class="notification-close-btn"
                                    onclick="notificationManager.dismiss('${notificationId}')"
                                    aria-label="关闭通知">
                                <i class="fas fa-times text-sm"></i>
                            </button>
                        </div>
                        ` : ''}
                    </div>
                `;
                
                return notification;
            }
            
            // 获取级别图标
            getLevelIcon(level) {
                const icons = {
                    info: 'info-circle',
                    success: 'check-circle',
                    warning: 'exclamation-triangle',
                    error: 'exclamation-circle',
                    critical: 'times-circle'
                };
                return icons[level] || 'info-circle';
            }
            
            // 设置自动关闭
            setAutoClose(notificationId, duration) {
                const timer = setTimeout(() => {
                    this.dismiss(notificationId);
                }, duration);
                
                this.autoCloseTimers.set(notificationId, timer);
            }
            
            // 取消通知
            dismiss(notificationId) {
                const notification = this.notifications.get(notificationId);
                if (!notification) return;
                
                // 清除自动关闭定时器
                const timer = this.autoCloseTimers.get(notificationId);
                if (timer) {
                    clearTimeout(timer);
                    this.autoCloseTimers.delete(notificationId);
                }
                
                // 添加关闭动画
                notification.classList.add('notification-dismissing');
                
                // 动画完成后移除
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.parentNode.removeChild(notification);
                    }
                    this.notifications.delete(notificationId);
                }, 300);
            }
            
            // 清除所有通知
            clearAll() {
                this.notifications.forEach((notification, id) => {
                    this.dismiss(id);
                });
            }
        }
        
        // 全局通知管理器
        window.notificationManager = new NotificationManager();
        
        // 恢复操作处理
        function handleRecoveryAction(action, notificationId) {
            switch (action) {
                case 'retry':
                    // 重试最后一个操作
                    if (window.lastFailedAction) {
                        window.lastFailedAction();
                    } else {
                        location.reload();
                    }
                    break;
                    
                case 'refresh':
                    location.reload();
                    break;
                    
                case 'redirect':
                    window.location.href = '/';
                    break;
                    
                case 'contact':
                    // 打开联系支持的模态框或页面
                    if (typeof openContactModal === 'function') {
                        openContactModal();
                    } else {
                        alert('请联系技术支持：support@example.com');
                    }
                    break;
            }
            
            // 关闭当前通知
            notificationManager.dismiss(notificationId);
        }
        
        // 全局错误处理
        window.addEventListener('error', function(event) {
            notificationManager.show('error', '页面错误', '页面发生了未预期的错误', {
                suggestions: ['刷新页面重试', '检查浏览器控制台', '联系技术支持'],
                recoveryOptions: [
                    { name: '刷新页面', action: 'refresh' },
                    { name: '返回首页', action: 'redirect' }
                ]
            });
        });
        
        // HTMX错误处理集成
        if (typeof htmx !== 'undefined') {
            document.addEventListener('htmx:responseError', function(event) {
                const status = event.detail.xhr.status;
                let title, message, suggestions;
                
                switch (status) {
                    case 400:
                        title = '请求错误';
                        message = '请求参数有误，请检查输入';
                        suggestions = ['检查表单输入', '重新提交'];
                        break;
                    case 401:
                        title = '未授权';
                        message = '请先登录后再进行操作';
                        suggestions = ['重新登录', '检查账户状态'];
                        break;
                    case 403:
                        title = '权限不足';
                        message = '您没有执行此操作的权限';
                        suggestions = ['联系管理员', '使用其他账户'];
                        break;
                    case 404:
                        title = '资源不存在';
                        message = '请求的资源未找到';
                        suggestions = ['检查链接', '返回上一页'];
                        break;
                    case 500:
                        title = '服务器错误';
                        message = '服务器遇到问题，请稍后重试';
                        suggestions = ['稍后重试', '联系技术支持'];
                        break;
                    default:
                        title = '网络错误';
                        message = '请求失败，请检查网络连接';
                        suggestions = ['检查网络', '重新尝试'];
                }
                
                notificationManager.show('error', title, message, {
                    suggestions: suggestions,
                    recoveryOptions: [
                        { name: '重试', action: 'retry' },
                        { name: '刷新', action: 'refresh' }
                    ]
                });
            });
        }
        
        // 便捷方法
        function showSuccess(message, title = '操作成功') {
            return notificationManager.show('success', title, message);
        }
        
        function showError(message, title = '操作失败') {
            return notificationManager.show('error', title, message, {
                recoveryOptions: [
                    { name: '重试', action: 'retry' }
                ]
            });
        }
        
        function showWarning(message, title = '注意') {
            return notificationManager.show('warning', title, message);
        }
        
        function showInfo(message, title = '提示') {
            return notificationManager.show('info', title, message);
        }
        '''
        
        return js_code


# 全局错误管理器
error_manager = ErrorManager()


def init_error_handling(app):
    """初始化错误处理功能"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_error_context():
        """注入错误处理上下文到模板"""
        return {
            'error_manager': error_manager,
            'error_styles': error_manager.get_error_styles(),
            'error_js': error_manager.get_error_javascript()
        }
    
    # 注册全局错误处理器
    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """处理通用异常"""
        try:
            error_response = error_manager.create_error_response(
                error,
                context={
                    'url': request.url,
                    'method': request.method,
                    'user_agent': request.headers.get('User-Agent'),
                    'ip_address': request.remote_addr
                }
            )
            
            # 记录错误日志
            current_app.logger.error(f"未处理异常: {error}", exc_info=True)
            
            # 根据请求类型返回不同格式
            if request.is_json or 'hx-request' in request.headers:
                return error_response, error_response['error']['code']
            else:
                # 渲染错误页面
                return render_error_page(error_response), error_response['error']['code']
                
        except Exception as e:
            current_app.logger.error(f"错误处理器本身出错: {e}", exc_info=True)
            return {'error': '系统错误'}, 500
    
    # 注册错误通知API
    @app.route('/api/errors/notify', methods=['POST'])
    def notify_error():
        """前端错误通知API"""
        try:
            data = request.get_json()
            error_type = data.get('type', 'client_error')
            message = data.get('message', '未知错误')
            context = data.get('context', {})
            
            # 创建虚拟异常对象
            class ClientError(Exception):
                def __init__(self, message):
                    self.message = message
                    super().__init__(message)
            
            client_error = ClientError(message)
            error_response = error_manager.create_error_response(
                client_error,
                error_type=error_type,
                context=context
            )
            
            # 记录客户端错误
            current_app.logger.warning(f"客户端错误: {message}, 上下文: {context}")
            
            return error_response
            
        except Exception as e:
            current_app.logger.error(f"处理客户端错误通知失败: {e}")
            return {'error': '处理失败'}, 500
    
    current_app.logger.info("错误处理功能已初始化")


def render_error_page(error_response: Dict) -> str:
    """渲染错误页面"""
    error_info = error_response['error']
    
    # 这里应该渲染一个专门的错误页面模板
    # 为简化，返回基本的HTML
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>错误 - {error_info['title']}</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; }}
            .error-container {{ max-width: 600px; margin: 100px auto; padding: 20px; text-align: center; }}
            .error-title {{ color: #dc3545; font-size: 24px; margin-bottom: 10px; }}
            .error-message {{ color: #666; font-size: 16px; margin-bottom: 20px; }}
            .suggestions {{ text-align: left; background: #f8f9fa; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="error-container">
            <h1 class="error-title">{error_info['title']}</h1>
            <p class="error-message">{error_info['message']}</p>
            
            {f'''
            <div class="suggestions">
                <h3>建议解决方案：</h3>
                <ul>
                    {''.join([f'<li>{suggestion}</li>' for suggestion in error_info['suggestions']])}
                </ul>
            </div>
            ''' if error_info.get('suggestions') else ''}
            
            <button onclick="history.back()">返回上一页</button>
            <button onclick="location.href='/'">返回首页</button>
        </div>
    </body>
    </html>
    '''


def get_error_manager():
    """获取错误管理器实例"""
    return error_manager