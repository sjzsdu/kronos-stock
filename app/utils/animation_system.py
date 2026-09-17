"""
动画系统和交互反馈
提供流畅的用户界面动画、过渡效果和视觉反馈
"""
from typing import Dict, List, Optional, Any, Tuple
from flask import current_app, request
import json


class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        # 动画配置
        self.animation_config = {
            'duration': {
                'fast': '150ms',
                'normal': '300ms',
                'slow': '500ms',
                'slower': '1000ms'
            },
            'easing': {
                'linear': 'linear',
                'ease': 'ease',
                'ease_in': 'ease-in',
                'ease_out': 'ease-out',
                'ease_in_out': 'ease-in-out',
                'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
                'elastic': 'cubic-bezier(0.175, 0.885, 0.32, 1.275)'
            }
        }
        
        # 预定义动画效果
        self.animations = {
            'fade_in': {
                'keyframes': {
                    'from': {'opacity': '0'},
                    'to': {'opacity': '1'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'fade_out': {
                'keyframes': {
                    'from': {'opacity': '1'},
                    'to': {'opacity': '0'}
                },
                'duration': 'normal',
                'easing': 'ease_in'
            },
            'slide_in_down': {
                'keyframes': {
                    'from': {'opacity': '0', 'transform': 'translateY(-20px)'},
                    'to': {'opacity': '1', 'transform': 'translateY(0)'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'slide_in_up': {
                'keyframes': {
                    'from': {'opacity': '0', 'transform': 'translateY(20px)'},
                    'to': {'opacity': '1', 'transform': 'translateY(0)'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'slide_in_left': {
                'keyframes': {
                    'from': {'opacity': '0', 'transform': 'translateX(-20px)'},
                    'to': {'opacity': '1', 'transform': 'translateX(0)'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'slide_in_right': {
                'keyframes': {
                    'from': {'opacity': '0', 'transform': 'translateX(20px)'},
                    'to': {'opacity': '1', 'transform': 'translateX(0)'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'scale_in': {
                'keyframes': {
                    'from': {'opacity': '0', 'transform': 'scale(0.95)'},
                    'to': {'opacity': '1', 'transform': 'scale(1)'}
                },
                'duration': 'normal',
                'easing': 'ease_out'
            },
            'scale_out': {
                'keyframes': {
                    'from': {'opacity': '1', 'transform': 'scale(1)'},
                    'to': {'opacity': '0', 'transform': 'scale(0.95)'}
                },
                'duration': 'normal',
                'easing': 'ease_in'
            },
            'bounce_in': {
                'keyframes': {
                    '0%': {'opacity': '0', 'transform': 'scale(0.3)'},
                    '50%': {'opacity': '1', 'transform': 'scale(1.05)'},
                    '70%': {'transform': 'scale(0.9)'},
                    '100%': {'opacity': '1', 'transform': 'scale(1)'}
                },
                'duration': 'slow',
                'easing': 'bounce'
            },
            'shake': {
                'keyframes': {
                    '0%, 100%': {'transform': 'translateX(0)'},
                    '10%, 30%, 50%, 70%, 90%': {'transform': 'translateX(-5px)'},
                    '20%, 40%, 60%, 80%': {'transform': 'translateX(5px)'}
                },
                'duration': 'slow',
                'easing': 'ease_in_out'
            },
            'pulse': {
                'keyframes': {
                    '0%, 100%': {'opacity': '1', 'transform': 'scale(1)'},
                    '50%': {'opacity': '0.8', 'transform': 'scale(1.05)'}
                },
                'duration': 'slower',
                'easing': 'ease_in_out',
                'iteration_count': 'infinite'
            },
            'spin': {
                'keyframes': {
                    'from': {'transform': 'rotate(0deg)'},
                    'to': {'transform': 'rotate(360deg)'}
                },
                'duration': 'slower',
                'easing': 'linear',
                'iteration_count': 'infinite'
            }
        }
        
        # 交互状态动画
        self.interaction_animations = {
            'button_press': {
                'transform': 'scale(0.98)',
                'transition': 'transform 100ms ease-in-out'
            },
            'button_hover': {
                'transform': 'translateY(-2px)',
                'box_shadow': '0 4px 12px rgba(0, 0, 0, 0.15)',
                'transition': 'all 200ms ease-out'
            },
            'card_hover': {
                'transform': 'translateY(-4px) scale(1.02)',
                'box_shadow': '0 8px 24px rgba(0, 0, 0, 0.12)',
                'transition': 'all 300ms ease-out'
            },
            'input_focus': {
                'border_color': '#3b82f6',
                'box_shadow': '0 0 0 3px rgba(59, 130, 246, 0.1)',
                'transition': 'all 200ms ease-out'
            }
        }
    
    def generate_animation_css(self, animation_name: str, 
                             custom_duration: str = None,
                             custom_easing: str = None) -> str:
        """生成动画CSS"""
        if animation_name not in self.animations:
            return ''
        
        animation = self.animations[animation_name]
        duration = custom_duration or self.animation_config['duration'][animation.get('duration', 'normal')]
        easing = custom_easing or self.animation_config['easing'][animation.get('easing', 'ease')]
        iteration_count = animation.get('iteration_count', '1')
        
        # 生成keyframes
        keyframes_css = f'@keyframes {animation_name} {{\n'
        for step, styles in animation['keyframes'].items():
            keyframes_css += f'  {step} {{\n'
            for property, value in styles.items():
                property_css = property.replace('_', '-')
                keyframes_css += f'    {property_css}: {value};\n'
            keyframes_css += f'  }}\n'
        keyframes_css += '}\n\n'
        
        # 生成animation类
        class_css = f'.animate-{animation_name.replace("_", "-")} {{\n'
        class_css += f'  animation: {animation_name} {duration} {easing} {iteration_count};\n'
        class_css += '}\n\n'
        
        return keyframes_css + class_css
    
    def generate_all_animations_css(self) -> str:
        """生成所有动画的CSS"""
        css_parts = [
            '/* 动画系统样式 */',
            '/* ============= */',
            ''
        ]
        
        # 生成所有预定义动画
        for animation_name in self.animations:
            css_parts.append(self.generate_animation_css(animation_name))
        
        # 交互动画样式
        css_parts.extend([
            '/* 交互动画 */',
            '.interactive-button {',
            '  transition: all 200ms ease-out;',
            '}',
            '',
            '.interactive-button:hover {',
            '  transform: translateY(-2px);',
            '  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);',
            '}',
            '',
            '.interactive-button:active {',
            '  transform: scale(0.98);',
            '}',
            '',
            '.interactive-card {',
            '  transition: all 300ms ease-out;',
            '}',
            '',
            '.interactive-card:hover {',
            '  transform: translateY(-4px) scale(1.02);',
            '  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);',
            '}',
            '',
            '.interactive-input {',
            '  transition: all 200ms ease-out;',
            '}',
            '',
            '.interactive-input:focus {',
            '  border-color: #3b82f6;',
            '  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);',
            '}',
            '',
            '/* 页面过渡动画 */',
            '.page-transition-enter {',
            '  opacity: 0;',
            '  transform: translateY(20px);',
            '}',
            '',
            '.page-transition-enter-active {',
            '  opacity: 1;',
            '  transform: translateY(0);',
            '  transition: all 400ms ease-out;',
            '}',
            '',
            '.page-transition-exit {',
            '  opacity: 1;',
            '  transform: translateY(0);',
            '}',
            '',
            '.page-transition-exit-active {',
            '  opacity: 0;',
            '  transform: translateY(-20px);',
            '  transition: all 300ms ease-in;',
            '}',
            '',
            '/* 模态框动画 */',
            '.modal-backdrop {',
            '  transition: opacity 300ms ease-out;',
            '}',
            '',
            '.modal-enter {',
            '  opacity: 0;',
            '  transform: scale(0.95) translateY(-20px);',
            '}',
            '',
            '.modal-enter-active {',
            '  opacity: 1;',
            '  transform: scale(1) translateY(0);',
            '  transition: all 300ms ease-out;',
            '}',
            '',
            '.modal-exit {',
            '  opacity: 1;',
            '  transform: scale(1) translateY(0);',
            '}',
            '',
            '.modal-exit-active {',
            '  opacity: 0;',
            '  transform: scale(0.95) translateY(-20px);',
            '  transition: all 200ms ease-in;',
            '}',
            '',
            '/* 列表项动画 */',
            '.list-item-enter {',
            '  opacity: 0;',
            '  transform: translateX(-20px);',
            '  max-height: 0;',
            '  overflow: hidden;',
            '}',
            '',
            '.list-item-enter-active {',
            '  opacity: 1;',
            '  transform: translateX(0);',
            '  max-height: 200px;',
            '  transition: all 400ms ease-out;',
            '}',
            '',
            '.list-item-exit {',
            '  opacity: 1;',
            '  transform: translateX(0);',
            '  max-height: 200px;',
            '}',
            '',
            '.list-item-exit-active {',
            '  opacity: 0;',
            '  transform: translateX(20px);',
            '  max-height: 0;',
            '  transition: all 300ms ease-in;',
            '}',
            '',
            '/* 加载状态动画增强 */',
            '.loading-shimmer {',
            '  background: linear-gradient(',
            '    90deg,',
            '    #f0f0f0 25%,',
            '    #e0e0e0 50%,',
            '    #f0f0f0 75%',
            '  );',
            '  background-size: 200% 100%;',
            '  animation: shimmer 2s infinite;',
            '}',
            '',
            '@keyframes shimmer {',
            '  0% { background-position: -200% 0; }',
            '  100% { background-position: 200% 0; }',
            '}',
            '',
            '/* 视觉反馈动画 */',
            '.feedback-success {',
            '  animation: success-pulse 600ms ease-out;',
            '}',
            '',
            '@keyframes success-pulse {',
            '  0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }',
            '  70% { box-shadow: 0 0 0 10px rgba(34, 197, 94, 0); }',
            '  100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }',
            '}',
            '',
            '.feedback-error {',
            '  animation: error-shake 600ms ease-in-out;',
            '}',
            '',
            '@keyframes error-shake {',
            '  0%, 100% { transform: translateX(0); }',
            '  10%, 30%, 50%, 70%, 90% { transform: translateX(-3px); }',
            '  20%, 40%, 60%, 80% { transform: translateX(3px); }',
            '}',
            '',
            '/* 无障碍和偏好设置 */',
            '@media (prefers-reduced-motion: reduce) {',
            '  *,',
            '  *::before,',
            '  *::after {',
            '    animation-duration: 0.01ms !important;',
            '    animation-iteration-count: 1 !important;',
            '    transition-duration: 0.01ms !important;',
            '    scroll-behavior: auto !important;',
            '  }',
            '}',
            '',
            '/* 高对比度模式优化 */',
            '@media (prefers-contrast: high) {',
            '  .interactive-button:hover,',
            '  .interactive-card:hover {',
            '    border: 2px solid currentColor;',
            '  }',
            '}',
            ''
        ])
        
        return '\n'.join(css_parts)
    
    def get_animation_javascript(self) -> str:
        """获取动画控制JavaScript"""
        js_code = '''
        // 动画系统管理器
        class AnimationSystem {
            constructor() {
                this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
                this.animationQueue = [];
                this.isAnimating = false;
                
                this.init();
            }
            
            init() {
                // 监听偏好设置变化
                window.matchMedia('(prefers-reduced-motion: reduce)')
                      .addEventListener('change', (e) => {
                    this.reducedMotion = e.matches;
                });
                
                // 初始化页面元素动画
                this.initPageAnimations();
                
                // 绑定交互动画
                this.bindInteractionAnimations();
            }
            
            // 初始化页面动画
            initPageAnimations() {
                // 页面加载时的入场动画
                const animatedElements = document.querySelectorAll('[data-animate]');
                
                animatedElements.forEach((element, index) => {
                    const animationType = element.dataset.animate;
                    const delay = element.dataset.animateDelay || (index * 100);
                    
                    // 初始隐藏元素
                    element.style.opacity = '0';
                    
                    // 延迟显示动画
                    setTimeout(() => {
                        this.animate(element, animationType);
                    }, parseInt(delay));
                });
            }
            
            // 绑定交互动画
            bindInteractionAnimations() {
                // 按钮交互
                document.addEventListener('mousedown', (e) => {
                    if (e.target.matches('.interactive-button, button')) {
                        this.addInteractionClass(e.target, 'button-pressed');
                    }
                });
                
                document.addEventListener('mouseup', (e) => {
                    if (e.target.matches('.interactive-button, button')) {
                        this.removeInteractionClass(e.target, 'button-pressed');
                    }
                });
                
                // 卡片悬停动画
                document.addEventListener('mouseenter', (e) => {
                    if (e.target.matches('.interactive-card')) {
                        this.addInteractionClass(e.target, 'card-hovered');
                    }
                });
                
                document.addEventListener('mouseleave', (e) => {
                    if (e.target.matches('.interactive-card')) {
                        this.removeInteractionClass(e.target, 'card-hovered');
                    }
                });
            }
            
            // 执行动画
            animate(element, animationType, options = {}) {
                if (this.reducedMotion && !options.force) {
                    // 如果用户偏好减少动画，直接显示最终状态
                    element.style.opacity = '1';
                    element.style.transform = 'none';
                    return Promise.resolve();
                }
                
                return new Promise((resolve) => {
                    const duration = options.duration || 300;
                    const easing = options.easing || 'ease-out';
                    
                    // 添加动画类
                    element.classList.add(`animate-${animationType}`);
                    element.style.opacity = '1';
                    
                    // 动画完成后清理
                    const cleanup = () => {
                        element.classList.remove(`animate-${animationType}`);
                        resolve();
                    };
                    
                    // 监听动画结束事件
                    element.addEventListener('animationend', cleanup, { once: true });
                    
                    // 备用定时器（防止事件不触发）
                    setTimeout(cleanup, duration + 100);
                });
            }
            
            // 批量动画
            animateSequence(elements, animationType, options = {}) {
                const stagger = options.stagger || 100;
                const promises = [];
                
                elements.forEach((element, index) => {
                    const delay = index * stagger;
                    
                    const promise = new Promise((resolve) => {
                        setTimeout(() => {
                            this.animate(element, animationType, options).then(resolve);
                        }, delay);
                    });
                    
                    promises.push(promise);
                });
                
                return Promise.all(promises);
            }
            
            // 添加交互类
            addInteractionClass(element, className) {
                if (this.reducedMotion) return;
                element.classList.add(className);
            }
            
            // 移除交互类
            removeInteractionClass(element, className) {
                element.classList.remove(className);
            }
            
            // 显示成功反馈
            showSuccessFeedback(element, message) {
                element.classList.add('feedback-success');
                
                if (message) {
                    this.showTooltip(element, message, 'success');
                }
                
                setTimeout(() => {
                    element.classList.remove('feedback-success');
                }, 600);
            }
            
            // 显示错误反馈
            showErrorFeedback(element, message) {
                element.classList.add('feedback-error');
                
                if (message) {
                    this.showTooltip(element, message, 'error');
                }
                
                setTimeout(() => {
                    element.classList.remove('feedback-error');
                }, 600);
            }
            
            // 显示工具提示
            showTooltip(element, message, type = 'info') {
                const tooltip = document.createElement('div');
                tooltip.className = `tooltip tooltip-${type}`;
                tooltip.textContent = message;
                
                // 定位工具提示
                const rect = element.getBoundingClientRect();
                tooltip.style.position = 'fixed';
                tooltip.style.top = `${rect.bottom + 10}px`;
                tooltip.style.left = `${rect.left + rect.width / 2}px`;
                tooltip.style.transform = 'translateX(-50%)';
                tooltip.style.zIndex = '9999';
                
                document.body.appendChild(tooltip);
                
                // 动画显示
                this.animate(tooltip, 'fade-in');
                
                // 自动移除
                setTimeout(() => {
                    this.animate(tooltip, 'fade-out').then(() => {
                        if (tooltip.parentNode) {
                            tooltip.parentNode.removeChild(tooltip);
                        }
                    });
                }, 3000);
            }
            
            // 页面转场动画
            transitionToPage(url, animationType = 'slide-left') {
                if (this.reducedMotion) {
                    window.location.href = url;
                    return;
                }
                
                const overlay = document.createElement('div');
                overlay.className = 'page-transition-overlay';
                overlay.style.cssText = `
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: #fff;
                    z-index: 9999;
                    opacity: 0;
                `;
                
                document.body.appendChild(overlay);
                
                // 淡入遮罩
                this.animate(overlay, 'fade-in', { duration: 300 }).then(() => {
                    window.location.href = url;
                });
            }
            
            // 模态框动画
            showModal(modalElement) {
                if (this.reducedMotion) {
                    modalElement.style.display = 'block';
                    return Promise.resolve();
                }
                
                modalElement.style.display = 'block';
                modalElement.classList.add('modal-enter');
                
                return this.animate(modalElement, 'modal-enter-active', {
                    duration: 300
                }).then(() => {
                    modalElement.classList.remove('modal-enter', 'modal-enter-active');
                });
            }
            
            hideModal(modalElement) {
                if (this.reducedMotion) {
                    modalElement.style.display = 'none';
                    return Promise.resolve();
                }
                
                modalElement.classList.add('modal-exit');
                
                return this.animate(modalElement, 'modal-exit-active', {
                    duration: 200
                }).then(() => {
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('modal-exit', 'modal-exit-active');
                });
            }
            
            // 列表项动画
            addListItem(listElement, itemElement) {
                if (this.reducedMotion) {
                    listElement.appendChild(itemElement);
                    return Promise.resolve();
                }
                
                itemElement.classList.add('list-item-enter');
                listElement.appendChild(itemElement);
                
                return this.animate(itemElement, 'list-item-enter-active', {
                    duration: 400
                }).then(() => {
                    itemElement.classList.remove('list-item-enter', 'list-item-enter-active');
                });
            }
            
            removeListItem(itemElement) {
                if (this.reducedMotion) {
                    if (itemElement.parentNode) {
                        itemElement.parentNode.removeChild(itemElement);
                    }
                    return Promise.resolve();
                }
                
                itemElement.classList.add('list-item-exit');
                
                return this.animate(itemElement, 'list-item-exit-active', {
                    duration: 300
                }).then(() => {
                    if (itemElement.parentNode) {
                        itemElement.parentNode.removeChild(itemElement);
                    }
                });
            }
        }
        
        // 全局动画系统实例
        window.animationSystem = new AnimationSystem();
        
        // 便捷方法
        function animateElement(element, animationType, options = {}) {
            return window.animationSystem.animate(element, animationType, options);
        }
        
        function showSuccess(element, message = '操作成功') {
            window.animationSystem.showSuccessFeedback(element, message);
        }
        
        function showError(element, message = '操作失败') {
            window.animationSystem.showErrorFeedback(element, message);
        }
        
        function showTooltip(element, message, type = 'info') {
            window.animationSystem.showTooltip(element, message, type);
        }
        
        // HTMX集成
        if (typeof htmx !== 'undefined') {
            // HTMX请求成功时显示反馈
            document.addEventListener('htmx:afterRequest', function(event) {
                if (event.detail.xhr.status >= 200 && event.detail.xhr.status < 300) {
                    const target = event.target;
                    if (target.hasAttribute('data-success-feedback')) {
                        showSuccess(target, target.getAttribute('data-success-feedback'));
                    }
                }
            });
            
            // HTMX内容交换时的动画
            document.addEventListener('htmx:beforeSwap', function(event) {
                const target = event.target;
                if (target.hasAttribute('data-swap-animation')) {
                    const animationType = target.getAttribute('data-swap-animation');
                    event.detail.shouldSwap = false;
                    
                    // 淡出旧内容
                    animateElement(target, 'fade-out').then(() => {
                        // 交换内容
                        target.innerHTML = event.detail.xhr.responseText;
                        
                        // 淡入新内容
                        animateElement(target, animationType || 'fade-in');
                    });
                }
            });
        }
        
        // 页面加载完成后初始化
        document.addEventListener('DOMContentLoaded', function() {
            // 为页面添加加载动画
            const pageContent = document.querySelector('main, .main-content, .page-content');
            if (pageContent) {
                animateElement(pageContent, 'fade-in', { duration: 400 });
            }
        });
        '''
        
        return js_code
    
    def create_animation_config_html(self) -> str:
        """创建动画配置HTML控件"""
        config_html = '''
        <div class="animation-config-panel bg-white rounded-lg shadow-lg p-6 max-w-md">
            <h3 class="text-lg font-semibold text-gray-800 mb-4">动画设置</h3>
            
            <!-- 动画开关 -->
            <div class="mb-4">
                <label class="flex items-center space-x-3">
                    <input type="checkbox" 
                           id="enable-animations" 
                           class="form-checkbox h-5 w-5 text-blue-600"
                           onchange="toggleAnimations(this.checked)">
                    <span class="text-gray-700">启用动画效果</span>
                </label>
            </div>
            
            <!-- 动画速度 -->
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    动画速度
                </label>
                <select id="animation-speed" 
                        class="form-select block w-full"
                        onchange="setAnimationSpeed(this.value)">
                    <option value="fast">快速 (150ms)</option>
                    <option value="normal" selected>正常 (300ms)</option>
                    <option value="slow">慢速 (500ms)</option>
                </select>
            </div>
            
            <!-- 动画缓动 -->
            <div class="mb-4">
                <label class="block text-sm font-medium text-gray-700 mb-2">
                    缓动效果
                </label>
                <select id="animation-easing" 
                        class="form-select block w-full"
                        onchange="setAnimationEasing(this.value)">
                    <option value="ease">默认</option>
                    <option value="ease-in">缓入</option>
                    <option value="ease-out" selected>缓出</option>
                    <option value="ease-in-out">缓入缓出</option>
                    <option value="bounce">弹跳</option>
                </select>
            </div>
            
            <!-- 减少动画 -->
            <div class="mb-4">
                <label class="flex items-center space-x-3">
                    <input type="checkbox" 
                           id="reduce-motion" 
                           class="form-checkbox h-5 w-5 text-blue-600"
                           onchange="setReduceMotion(this.checked)">
                    <span class="text-gray-700">减少动画（无障碍模式）</span>
                </label>
            </div>
            
            <!-- 测试按钮 -->
            <div class="space-y-2">
                <button class="btn btn-primary w-full interactive-button"
                        onclick="testAnimation('fade-in')">
                    测试淡入动画
                </button>
                <button class="btn btn-secondary w-full interactive-button"
                        onclick="testAnimation('slide-in-up')">
                    测试滑入动画
                </button>
                <button class="btn btn-success w-full interactive-button"
                        onclick="testAnimation('bounce-in')">
                    测试弹跳动画
                </button>
            </div>
        </div>
        
        <script>
        // 动画配置控制
        function toggleAnimations(enabled) {
            document.documentElement.style.setProperty(
                '--animation-play-state', 
                enabled ? 'running' : 'paused'
            );
            
            if (!enabled) {
                document.documentElement.classList.add('reduce-motion');
            } else {
                document.documentElement.classList.remove('reduce-motion');
            }
        }
        
        function setAnimationSpeed(speed) {
            const durations = {
                fast: '150ms',
                normal: '300ms',
                slow: '500ms'
            };
            
            document.documentElement.style.setProperty(
                '--animation-duration',
                durations[speed] || '300ms'
            );
        }
        
        function setAnimationEasing(easing) {
            document.documentElement.style.setProperty(
                '--animation-timing-function',
                easing
            );
        }
        
        function setReduceMotion(reduce) {
            if (reduce) {
                document.documentElement.classList.add('reduce-motion');
            } else {
                document.documentElement.classList.remove('reduce-motion');
            }
        }
        
        function testAnimation(animationType) {
            const testElement = document.createElement('div');
            testElement.className = 'test-animation-element bg-blue-500 text-white p-4 rounded-lg text-center';
            testElement.textContent = `测试 ${animationType} 动画`;
            testElement.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 9999;
                opacity: 0;
            `;
            
            document.body.appendChild(testElement);
            
            // 执行动画
            if (window.animationSystem) {
                window.animationSystem.animate(testElement, animationType, {
                    duration: 600
                }).then(() => {
                    setTimeout(() => {
                        window.animationSystem.animate(testElement, 'fade-out').then(() => {
                            if (testElement.parentNode) {
                                testElement.parentNode.removeChild(testElement);
                            }
                        });
                    }, 1500);
                });
            }
        }
        </script>
        '''
        
        return config_html


# 全局动画管理器
animation_manager = AnimationManager()


def init_animation_system(app):
    """初始化动画系统"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_animation_context():
        """注入动画上下文到模板"""
        return {
            'animation_manager': animation_manager,
            'animation_css': animation_manager.generate_all_animations_css(),
            'animation_js': animation_manager.get_animation_javascript(),
            'animation_config_html': animation_manager.create_animation_config_html()
        }
    
    # 注册动画API
    @app.route('/api/animations/css/<animation_name>')
    def get_animation_css(animation_name):
        """获取特定动画CSS"""
        try:
            css = animation_manager.generate_animation_css(animation_name)
            return {'css': css}
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/animations/config', methods=['GET', 'POST'])
    def animation_config():
        """动画配置API"""
        if request.method == 'GET':
            return {
                'durations': animation_manager.animation_config['duration'],
                'easings': animation_manager.animation_config['easing'],
                'animations': list(animation_manager.animations.keys())
            }
        
        elif request.method == 'POST':
            # 保存用户动画偏好
            data = request.get_json()
            # 这里可以保存到session或数据库
            return {'message': '动画配置已保存', 'config': data}
    
    current_app.logger.info("动画系统已初始化")


def get_animation_manager():
    """获取动画管理器实例"""
    return animation_manager