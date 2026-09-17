"""
加载状态指示器组件
提供各种加载状态的视觉反馈，包括骨架屏、进度条、加载动画等
"""
from typing import Dict, List, Optional, Any
from flask import render_template_string, request, current_app
import json


class LoadingIndicatorManager:
    """加载状态指示器管理器"""
    
    def __init__(self):
        # 加载状态类型
        self.indicator_types = {
            'spinner': {
                'name': '旋转器',
                'use_cases': ['按钮加载', '小范围加载'],
                'duration': 'short'
            },
            'progress_bar': {
                'name': '进度条',
                'use_cases': ['文件上传', '数据处理'],
                'duration': 'medium'
            },
            'skeleton': {
                'name': '骨架屏',
                'use_cases': ['页面初始加载', '内容预览'],
                'duration': 'long'
            },
            'pulse': {
                'name': '脉冲动画',
                'use_cases': ['占位符', '等待数据'],
                'duration': 'medium'
            },
            'dots': {
                'name': '点状加载',
                'use_cases': ['文本加载', '简单提示'],
                'duration': 'short'
            }
        }
        
        # 加载消息模板
        self.loading_messages = {
            'data_fetch': ['正在获取数据...', '数据加载中...', '请稍候...'],
            'file_upload': ['正在上传文件...', '文件处理中...', '上传进行中...'],
            'calculation': ['正在计算...', '数据分析中...', '处理中...'],
            'prediction': ['正在生成预测...', '模型运算中...', '预测分析中...'],
            'save': ['正在保存...', '数据提交中...', '保存进行中...']
        }
    
    def create_spinner(self, size: str = 'medium', color: str = 'primary', 
                      message: str = None) -> str:
        """创建旋转加载器"""
        size_classes = {
            'small': 'w-4 h-4',
            'medium': 'w-6 h-6', 
            'large': 'w-8 h-8',
            'xl': 'w-12 h-12'
        }
        
        color_classes = {
            'primary': 'text-blue-600',
            'secondary': 'text-gray-600',
            'success': 'text-green-600',
            'warning': 'text-yellow-600',
            'danger': 'text-red-600'
        }
        
        size_class = size_classes.get(size, size_classes['medium'])
        color_class = color_classes.get(color, color_classes['primary'])
        
        spinner_template = f'''
        <div class="loading-spinner-container flex items-center justify-center space-x-2" 
             role="status" aria-live="polite" aria-label="加载中">
            <svg class="animate-spin {size_class} {color_class}" 
                 xmlns="http://www.w3.org/2000/svg" 
                 fill="none" 
                 viewBox="0 0 24 24">
                <circle class="opacity-25" 
                        cx="12" cy="12" r="10" 
                        stroke="currentColor" 
                        stroke-width="4"></circle>
                <path class="opacity-75" 
                      fill="currentColor" 
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {f'<span class="text-sm text-gray-600">{message}</span>' if message else ''}
        </div>
        '''
        
        return spinner_template
    
    def create_progress_bar(self, progress: int = 0, show_percentage: bool = True,
                          animated: bool = True, color: str = 'primary',
                          message: str = None) -> str:
        """创建进度条"""
        color_classes = {
            'primary': 'bg-blue-600',
            'success': 'bg-green-600', 
            'warning': 'bg-yellow-600',
            'danger': 'bg-red-600'
        }
        
        color_class = color_classes.get(color, color_classes['primary'])
        animation_class = 'progress-bar-animated' if animated else ''
        
        progress_template = f'''
        <div class="progress-container w-full" 
             role="progressbar" 
             aria-valuenow="{progress}" 
             aria-valuemin="0" 
             aria-valuemax="100"
             aria-label="加载进度">
            {f'<div class="text-sm text-gray-600 mb-2">{message}</div>' if message else ''}
            <div class="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div class="h-full {color_class} {animation_class} transition-all duration-300 ease-out rounded-full" 
                     style="width: {progress}%"></div>
            </div>
            {f'<div class="text-xs text-gray-500 mt-1 text-right">{progress}%</div>' if show_percentage else ''}
        </div>
        '''
        
        return progress_template
    
    def create_skeleton_screen(self, layout: str = 'default', 
                             items_count: int = 3) -> str:
        """创建骨架屏"""
        skeleton_layouts = {
            'default': '''
            <div class="skeleton-item animate-pulse">
                <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-300 rounded w-1/2 mb-2"></div>
                <div class="h-3 bg-gray-300 rounded w-2/3"></div>
            </div>
            ''',
            'card': '''
            <div class="skeleton-card animate-pulse">
                <div class="h-32 bg-gray-300 rounded-lg mb-4"></div>
                <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                <div class="h-3 bg-gray-300 rounded w-1/2"></div>
            </div>
            ''',
            'list': '''
            <div class="skeleton-list-item animate-pulse flex space-x-3 mb-3">
                <div class="w-10 h-10 bg-gray-300 rounded-full"></div>
                <div class="flex-1 space-y-2">
                    <div class="h-3 bg-gray-300 rounded w-1/2"></div>
                    <div class="h-2 bg-gray-300 rounded w-3/4"></div>
                </div>
            </div>
            ''',
            'table': '''
            <div class="skeleton-table-row animate-pulse flex space-x-4 mb-2">
                <div class="h-4 bg-gray-300 rounded w-1/4"></div>
                <div class="h-4 bg-gray-300 rounded w-1/3"></div>
                <div class="h-4 bg-gray-300 rounded w-1/6"></div>
                <div class="h-4 bg-gray-300 rounded w-1/4"></div>
            </div>
            '''
        }
        
        skeleton_item = skeleton_layouts.get(layout, skeleton_layouts['default'])
        
        skeleton_template = f'''
        <div class="skeleton-container" 
             role="status" 
             aria-live="polite" 
             aria-label="内容加载中">
            <div class="sr-only">内容正在加载，请稍候...</div>
            {''.join([skeleton_item for _ in range(items_count)])}
        </div>
        '''
        
        return skeleton_template
    
    def create_pulse_animation(self, shape: str = 'rectangle', 
                             size: Dict[str, str] = None) -> str:
        """创建脉冲动画"""
        if size is None:
            size = {'width': 'w-full', 'height': 'h-4'}
        
        shape_classes = {
            'rectangle': 'rounded',
            'circle': 'rounded-full',
            'square': 'rounded-lg'
        }
        
        shape_class = shape_classes.get(shape, shape_classes['rectangle'])
        
        pulse_template = f'''
        <div class="pulse-animation animate-pulse" 
             role="status" 
             aria-label="加载中">
            <div class="{size['width']} {size['height']} bg-gray-300 {shape_class}"></div>
        </div>
        '''
        
        return pulse_template
    
    def create_dots_loader(self, color: str = 'primary', size: str = 'medium') -> str:
        """创建点状加载器"""
        size_classes = {
            'small': 'w-2 h-2',
            'medium': 'w-3 h-3',
            'large': 'w-4 h-4'
        }
        
        color_classes = {
            'primary': 'bg-blue-600',
            'secondary': 'bg-gray-600',
            'success': 'bg-green-600',
            'warning': 'bg-yellow-600',
            'danger': 'bg-red-600'
        }
        
        size_class = size_classes.get(size, size_classes['medium'])
        color_class = color_classes.get(color, color_classes['primary'])
        
        dots_template = f'''
        <div class="dots-loader flex space-x-1 justify-center items-center" 
             role="status" 
             aria-label="加载中">
            <div class="{size_class} {color_class} rounded-full animate-bounce" 
                 style="animation-delay: 0ms"></div>
            <div class="{size_class} {color_class} rounded-full animate-bounce" 
                 style="animation-delay: 150ms"></div>
            <div class="{size_class} {color_class} rounded-full animate-bounce" 
                 style="animation-delay: 300ms"></div>
        </div>
        '''
        
        return dots_template
    
    def create_button_loading_state(self, button_text: str, 
                                   loading_text: str = "加载中...",
                                   show_spinner: bool = True) -> str:
        """创建按钮加载状态"""
        spinner_html = self.create_spinner(size='small', color='secondary') if show_spinner else ''
        
        button_template = f'''
        <button class="loading-button btn btn-primary" 
                disabled 
                aria-disabled="true"
                aria-describedby="loading-status">
            <span class="button-content flex items-center justify-center space-x-2">
                {spinner_html}
                <span>{loading_text}</span>
            </span>
            <span id="loading-status" class="sr-only">按钮处于加载状态，请等待操作完成</span>
        </button>
        '''
        
        return button_template
    
    def create_page_loading_overlay(self, message: str = "页面加载中...",
                                   background_opacity: str = "75") -> str:
        """创建页面加载遮罩"""
        overlay_template = f'''
        <div class="page-loading-overlay fixed inset-0 bg-gray-900 bg-opacity-{background_opacity} z-50 flex items-center justify-center"
             role="status" 
             aria-live="assertive" 
             aria-label="页面加载中">
            <div class="loading-content bg-white rounded-lg p-6 shadow-lg max-w-sm mx-4 text-center">
                {self.create_spinner(size='large', color='primary')}
                <p class="mt-4 text-gray-700 font-medium">{message}</p>
                <div class="mt-2 text-sm text-gray-500">请稍候，正在为您准备内容...</div>
            </div>
        </div>
        '''
        
        return overlay_template
    
    def get_loading_css(self) -> str:
        """获取加载动画CSS样式"""
        css_styles = '''
        /* 加载状态指示器样式 */
        .loading-spinner-container {
            min-height: 2rem;
        }
        
        .progress-bar-animated {
            background-image: linear-gradient(
                45deg,
                rgba(255, 255, 255, 0.2) 25%,
                transparent 25%,
                transparent 50%,
                rgba(255, 255, 255, 0.2) 50%,
                rgba(255, 255, 255, 0.2) 75%,
                transparent 75%,
                transparent
            );
            background-size: 1rem 1rem;
            animation: progress-bar-stripes 1s linear infinite;
        }
        
        @keyframes progress-bar-stripes {
            0% { background-position-x: 0; }
            100% { background-position-x: 1rem; }
        }
        
        .skeleton-container .animate-pulse {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .dots-loader .animate-bounce {
            animation: bounce 1s infinite;
        }
        
        @keyframes bounce {
            0%, 100% {
                transform: translateY(-25%);
                animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
            }
            50% {
                transform: none;
                animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
            }
        }
        
        .loading-button {
            pointer-events: none;
            opacity: 0.7;
        }
        
        .page-loading-overlay {
            backdrop-filter: blur(2px);
        }
        
        /* 减少动画偏好设置 */
        @media (prefers-reduced-motion: reduce) {
            .animate-spin,
            .animate-pulse,
            .animate-bounce,
            .progress-bar-animated {
                animation: none !important;
            }
        }
        
        /* 高对比度模式适配 */
        @media (prefers-contrast: high) {
            .skeleton-container div,
            .pulse-animation div {
                background-color: #666 !important;
            }
        }
        '''
        
        return css_styles
    
    def get_loading_javascript(self) -> str:
        """获取加载状态管理JavaScript"""
        js_code = '''
        // 加载状态管理器
        class LoadingManager {
            constructor() {
                this.activeLoaders = new Set();
                this.loadingOverlay = null;
            }
            
            // 显示加载状态
            showLoading(elementId, type = 'spinner', options = {}) {
                const element = document.getElementById(elementId);
                if (!element) return;
                
                // 记录原始内容
                if (!element.dataset.originalContent) {
                    element.dataset.originalContent = element.innerHTML;
                }
                
                // 添加加载状态
                element.classList.add('loading-state');
                element.setAttribute('aria-busy', 'true');
                
                // 根据类型显示不同的加载指示器
                switch (type) {
                    case 'spinner':
                        this.showSpinner(element, options);
                        break;
                    case 'skeleton':
                        this.showSkeleton(element, options);
                        break;
                    case 'pulse':
                        this.showPulse(element, options);
                        break;
                }
                
                this.activeLoaders.add(elementId);
            }
            
            // 隐藏加载状态
            hideLoading(elementId) {
                const element = document.getElementById(elementId);
                if (!element || !this.activeLoaders.has(elementId)) return;
                
                // 恢复原始内容
                if (element.dataset.originalContent) {
                    element.innerHTML = element.dataset.originalContent;
                    delete element.dataset.originalContent;
                }
                
                // 移除加载状态
                element.classList.remove('loading-state');
                element.removeAttribute('aria-busy');
                
                this.activeLoaders.delete(elementId);
            }
            
            // 显示页面级加载遮罩
            showPageLoading(message = '加载中...') {
                if (this.loadingOverlay) return;
                
                this.loadingOverlay = document.createElement('div');
                this.loadingOverlay.className = 'page-loading-overlay fixed inset-0 bg-gray-900 bg-opacity-75 z-50 flex items-center justify-center';
                this.loadingOverlay.setAttribute('role', 'status');
                this.loadingOverlay.setAttribute('aria-live', 'assertive');
                this.loadingOverlay.setAttribute('aria-label', '页面加载中');
                
                this.loadingOverlay.innerHTML = `
                    <div class="loading-content bg-white rounded-lg p-6 shadow-lg max-w-sm mx-4 text-center">
                        <div class="loading-spinner-container flex items-center justify-center mb-4">
                            <svg class="animate-spin w-8 h-8 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                        </div>
                        <p class="text-gray-700 font-medium">${message}</p>
                    </div>
                `;
                
                document.body.appendChild(this.loadingOverlay);
                document.body.style.overflow = 'hidden';
            }
            
            // 隐藏页面级加载遮罩
            hidePageLoading() {
                if (this.loadingOverlay) {
                    this.loadingOverlay.remove();
                    this.loadingOverlay = null;
                    document.body.style.overflow = '';
                }
            }
            
            // 显示旋转器
            showSpinner(element, options) {
                const size = options.size || 'medium';
                const color = options.color || 'primary';
                const message = options.message || '';
                
                element.innerHTML = `
                    <div class="loading-spinner-container flex items-center justify-center space-x-2">
                        <svg class="animate-spin w-6 h-6 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        ${message ? `<span class="text-sm text-gray-600">${message}</span>` : ''}
                    </div>
                `;
            }
            
            // 显示骨架屏
            showSkeleton(element, options) {
                const itemsCount = options.itemsCount || 3;
                const layout = options.layout || 'default';
                
                let skeletonHTML = '';
                for (let i = 0; i < itemsCount; i++) {
                    skeletonHTML += `
                        <div class="skeleton-item animate-pulse mb-4">
                            <div class="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
                            <div class="h-3 bg-gray-300 rounded w-1/2 mb-2"></div>
                            <div class="h-3 bg-gray-300 rounded w-2/3"></div>
                        </div>
                    `;
                }
                
                element.innerHTML = `
                    <div class="skeleton-container">
                        <div class="sr-only">内容正在加载，请稍候...</div>
                        ${skeletonHTML}
                    </div>
                `;
            }
            
            // 显示脉冲动画
            showPulse(element, options) {
                element.innerHTML = `
                    <div class="pulse-animation animate-pulse">
                        <div class="w-full h-4 bg-gray-300 rounded"></div>
                    </div>
                `;
            }
        }
        
        // 全局加载管理器实例
        window.loadingManager = new LoadingManager();
        
        // HTMX集成
        if (typeof htmx !== 'undefined') {
            // HTMX请求开始时显示加载状态
            document.addEventListener('htmx:beforeRequest', function(event) {
                const target = event.target;
                if (target.hasAttribute('hx-loading')) {
                    const loadingType = target.getAttribute('hx-loading-type') || 'spinner';
                    const loadingMessage = target.getAttribute('hx-loading-message') || '加载中...';
                    
                    window.loadingManager.showLoading(target.id, loadingType, {
                        message: loadingMessage
                    });
                }
            });
            
            // HTMX请求完成时隐藏加载状态
            document.addEventListener('htmx:afterRequest', function(event) {
                const target = event.target;
                if (target.hasAttribute('hx-loading')) {
                    window.loadingManager.hideLoading(target.id);
                }
            });
        }
        '''
        
        return js_code


# 全局加载指示器管理器
loading_manager = LoadingIndicatorManager()


def init_loading_indicators(app):
    """初始化加载状态指示器功能"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_loading_context():
        """注入加载指示器上下文到模板"""
        return {
            'loading_manager': loading_manager,
            'loading_css': loading_manager.get_loading_css(),
            'loading_js': loading_manager.get_loading_javascript()
        }
    
    # 注册加载指示器API
    @app.route('/api/loading/templates')
    def loading_templates():
        """获取加载模板API"""
        try:
            template_type = request.args.get('type', 'spinner')
            size = request.args.get('size', 'medium')
            color = request.args.get('color', 'primary')
            message = request.args.get('message')
            
            if template_type == 'spinner':
                html = loading_manager.create_spinner(size, color, message)
            elif template_type == 'progress':
                progress = int(request.args.get('progress', 0))
                html = loading_manager.create_progress_bar(progress, message=message)
            elif template_type == 'skeleton':
                layout = request.args.get('layout', 'default')
                items = int(request.args.get('items', 3))
                html = loading_manager.create_skeleton_screen(layout, items)
            elif template_type == 'dots':
                html = loading_manager.create_dots_loader(color, size)
            else:
                html = loading_manager.create_spinner(size, color, message)
            
            return {'html': html}
        except Exception as e:
            return {'error': str(e)}, 500
    
    app.logger.info("加载状态指示器功能已初始化")


def get_loading_manager():
    """获取加载指示器管理器实例"""
    return loading_manager