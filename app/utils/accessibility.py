"""
无障碍访问(A11y)工具和辅助功能
提供网站无障碍访问支持，包括屏幕阅读器、键盘导航、色彩对比度等
"""
import re
import colorsys
from typing import Dict, List, Optional, Tuple, Any
from flask import request, session, current_app
import json


class AccessibilityManager:
    """无障碍访问管理器"""
    
    def __init__(self):
        # WCAG 2.1 颜色对比度标准
        self.contrast_standards = {
            'AA_normal': 4.5,      # WCAG AA 标准文本
            'AA_large': 3.0,       # WCAG AA 大号文本
            'AAA_normal': 7.0,     # WCAG AAA 标准文本
            'AAA_large': 4.5       # WCAG AAA 大号文本
        }
        
        # 键盘快捷键配置
        self.keyboard_shortcuts = {
            'skip_to_content': 'Alt+1',
            'main_navigation': 'Alt+2',
            'search': 'Alt+3',
            'footer': 'Alt+4',
            'help': 'Alt+H',
            'home': 'Alt+0'
        }
        
        # ARIA标签模板
        self.aria_templates = {
            'button': {
                'role': 'button',
                'aria-pressed': 'false',
                'tabindex': '0'
            },
            'dialog': {
                'role': 'dialog',
                'aria-modal': 'true',
                'aria-labelledby': '',
                'aria-describedby': ''
            },
            'navigation': {
                'role': 'navigation',
                'aria-label': ''
            },
            'main': {
                'role': 'main',
                'aria-labelledby': 'main-heading'
            },
            'alert': {
                'role': 'alert',
                'aria-live': 'assertive',
                'aria-atomic': 'true'
            },
            'status': {
                'role': 'status',
                'aria-live': 'polite',
                'aria-atomic': 'true'
            }
        }
        
        # 无障碍用户偏好设置
        self.accessibility_preferences = {
            'high_contrast': False,
            'large_text': False,
            'reduce_motion': False,
            'screen_reader': False,
            'keyboard_only': False,
            'focus_indicators': True,
            'skip_links': True
        }
    
    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """将十六进制颜色转换为RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for c in hex_color])
        
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except ValueError:
            return (0, 0, 0)  # 默认黑色
    
    def rgb_to_luminance(self, rgb: Tuple[int, int, int]) -> float:
        """计算RGB颜色的相对亮度"""
        def normalize_channel(channel):
            channel = channel / 255.0
            if channel <= 0.03928:
                return channel / 12.92
            else:
                return pow((channel + 0.055) / 1.055, 2.4)
        
        r, g, b = [normalize_channel(c) for c in rgb]
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """计算两个颜色之间的对比度"""
        rgb1 = self.hex_to_rgb(color1)
        rgb2 = self.hex_to_rgb(color2)
        
        lum1 = self.rgb_to_luminance(rgb1)
        lum2 = self.rgb_to_luminance(rgb2)
        
        # 确保较亮的颜色在分子位置
        brighter = max(lum1, lum2)
        darker = min(lum1, lum2)
        
        return (brighter + 0.05) / (darker + 0.05)
    
    def check_color_accessibility(self, foreground: str, background: str, 
                                text_size: str = 'normal') -> Dict[str, Any]:
        """检查颜色组合的无障碍性"""
        contrast_ratio = self.calculate_contrast_ratio(foreground, background)
        
        # 选择对应的标准
        if text_size in ['large', 'bold']:
            aa_standard = self.contrast_standards['AA_large']
            aaa_standard = self.contrast_standards['AAA_large']
        else:
            aa_standard = self.contrast_standards['AA_normal']
            aaa_standard = self.contrast_standards['AAA_normal']
        
        return {
            'contrast_ratio': round(contrast_ratio, 2),
            'wcag_aa': contrast_ratio >= aa_standard,
            'wcag_aaa': contrast_ratio >= aaa_standard,
            'recommendation': self._get_contrast_recommendation(contrast_ratio, aa_standard, aaa_standard),
            'foreground_color': foreground,
            'background_color': background,
            'text_size': text_size
        }
    
    def _get_contrast_recommendation(self, ratio: float, aa_threshold: float, 
                                   aaa_threshold: float) -> str:
        """获取对比度建议"""
        if ratio >= aaa_threshold:
            return "优秀 - 符合WCAG AAA标准"
        elif ratio >= aa_threshold:
            return "良好 - 符合WCAG AA标准"
        else:
            needed_improvement = aa_threshold / ratio
            return f"需要改进 - 对比度需要提升 {needed_improvement:.1f} 倍"
    
    def generate_aria_attributes(self, element_type: str, custom_attrs: Dict = None) -> Dict[str, str]:
        """生成ARIA属性"""
        base_attrs = self.aria_templates.get(element_type, {}).copy()
        
        if custom_attrs:
            base_attrs.update(custom_attrs)
        
        return base_attrs
    
    def create_skip_links(self, links: List[Dict[str, str]] = None) -> str:
        """创建跳过链接"""
        if links is None:
            links = [
                {'href': '#main-content', 'text': '跳到主要内容'},
                {'href': '#navigation', 'text': '跳到导航'},
                {'href': '#footer', 'text': '跳到页脚'}
            ]
        
        skip_links_html = ['<div class="skip-links" aria-label="跳过链接">']
        
        for link in links:
            skip_links_html.append(
                f'<a href="{link["href"]}" class="skip-link">{link["text"]}</a>'
            )
        
        skip_links_html.append('</div>')
        
        return '\n'.join(skip_links_html)
    
    def get_accessibility_css(self, preferences: Dict = None) -> str:
        """生成无障碍CSS样式"""
        if preferences is None:
            preferences = self.accessibility_preferences
        
        css_rules = [
            """
            /* 跳过链接样式 */
            .skip-links {
                position: absolute;
                top: -40px;
                left: 6px;
                z-index: 1000;
            }
            
            .skip-link {
                position: absolute;
                top: -40px;
                left: 6px;
                background: #000;
                color: #fff;
                padding: 8px;
                text-decoration: none;
                border-radius: 0 0 4px 4px;
                font-weight: bold;
                z-index: 1001;
            }
            
            .skip-link:focus {
                top: 0;
            }
            
            /* 焦点指示器 */
            *:focus {
                outline: 2px solid #0066cc;
                outline-offset: 2px;
            }
            
            .focus-visible {
                outline: 2px solid #0066cc;
                outline-offset: 2px;
            }
            
            /* 屏幕阅读器专用文本 */
            .sr-only {
                position: absolute;
                width: 1px;
                height: 1px;
                padding: 0;
                margin: -1px;
                overflow: hidden;
                clip: rect(0, 0, 0, 0);
                white-space: nowrap;
                border: 0;
            }
            
            /* 键盘导航增强 */
            .keyboard-user *:focus {
                outline: 3px solid #ff6b35;
                outline-offset: 2px;
            }
            """
        ]
        
        # 高对比度模式
        if preferences.get('high_contrast'):
            css_rules.append("""
            /* 高对比度模式 */
            .high-contrast {
                background: #000 !important;
                color: #fff !important;
            }
            
            .high-contrast a {
                color: #ffff00 !important;
            }
            
            .high-contrast button {
                background: #fff !important;
                color: #000 !important;
                border: 2px solid #fff !important;
            }
            """)
        
        # 大字体模式
        if preferences.get('large_text'):
            css_rules.append("""
            /* 大字体模式 */
            .large-text {
                font-size: 1.25em !important;
                line-height: 1.6 !important;
            }
            
            .large-text h1 { font-size: 2.5em !important; }
            .large-text h2 { font-size: 2em !important; }
            .large-text h3 { font-size: 1.75em !important; }
            """)
        
        # 减少动画模式
        if preferences.get('reduce_motion'):
            css_rules.append("""
            /* 减少动画模式 */
            .reduce-motion,
            .reduce-motion *,
            .reduce-motion *::before,
            .reduce-motion *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
            """)
        
        return '\n'.join(css_rules)
    
    def validate_form_accessibility(self, form_html: str) -> Dict[str, Any]:
        """验证表单的无障碍性"""
        issues = []
        suggestions = []
        
        # 检查标签关联
        input_pattern = r'<input[^>]*>'
        label_pattern = r'<label[^>]*for=["\']([^"\']+)["\'][^>]*>'
        
        inputs = re.findall(input_pattern, form_html, re.IGNORECASE)
        labels = re.findall(label_pattern, form_html, re.IGNORECASE)
        
        input_ids = []
        for input_tag in inputs:
            id_match = re.search(r'id=["\']([^"\']+)["\']', input_tag, re.IGNORECASE)
            if id_match:
                input_ids.append(id_match.group(1))
        
        # 检查无标签的输入框
        unlabeled_inputs = set(input_ids) - set(labels)
        if unlabeled_inputs:
            issues.append(f"发现 {len(unlabeled_inputs)} 个无标签的输入框")
            suggestions.append("为所有输入框添加对应的label标签")
        
        # 检查必填字段标识
        if 'required' in form_html.lower() and 'aria-required' not in form_html.lower():
            suggestions.append("为必填字段添加 aria-required=\"true\" 属性")
        
        # 检查错误提示
        if 'error' in form_html.lower() and 'aria-describedby' not in form_html.lower():
            suggestions.append("使用 aria-describedby 关联错误提示信息")
        
        return {
            'total_inputs': len(input_ids),
            'labeled_inputs': len(labels),
            'issues_count': len(issues),
            'issues': issues,
            'suggestions': suggestions,
            'accessibility_score': max(0, 100 - len(issues) * 20)
        }
    
    def generate_keyboard_shortcuts_help(self) -> str:
        """生成键盘快捷键帮助"""
        shortcuts_html = [
            '<div class="keyboard-shortcuts-help" role="dialog" aria-labelledby="shortcuts-title">',
            '<h2 id="shortcuts-title">键盘快捷键</h2>',
            '<ul>'
        ]
        
        for action, shortcut in self.keyboard_shortcuts.items():
            action_text = action.replace('_', ' ').title()
            shortcuts_html.append(f'<li><kbd>{shortcut}</kbd> - {action_text}</li>')
        
        shortcuts_html.extend(['</ul>', '</div>'])
        
        return '\n'.join(shortcuts_html)
    
    def get_user_preferences(self, user_id: int = None) -> Dict:
        """获取用户无障碍偏好设置"""
        if user_id:
            # 从数据库获取用户偏好（这里简化为从session获取）
            return session.get(f'a11y_preferences_{user_id}', self.accessibility_preferences.copy())
        else:
            return session.get('a11y_preferences', self.accessibility_preferences.copy())
    
    def save_user_preferences(self, preferences: Dict, user_id: int = None):
        """保存用户无障碍偏好设置"""
        if user_id:
            session[f'a11y_preferences_{user_id}'] = preferences
        else:
            session['a11y_preferences'] = preferences
    
    def detect_screen_reader(self, user_agent: str = None) -> bool:
        """检测是否使用屏幕阅读器"""
        if user_agent is None:
            user_agent = request.headers.get('User-Agent', '').lower()
        
        screen_reader_indicators = [
            'nvda', 'jaws', 'dragon', 'zoomtext', 'supernova',
            'narrator', 'voiceover', 'talkback', 'orca'
        ]
        
        return any(indicator in user_agent for indicator in screen_reader_indicators)
    
    def create_live_region(self, message: str, level: str = 'polite') -> str:
        """创建ARIA实时区域"""
        aria_live = 'assertive' if level == 'urgent' else 'polite'
        
        return f'''
        <div class="live-region" 
             aria-live="{aria_live}" 
             aria-atomic="true" 
             aria-relevant="additions text">
            {message}
        </div>
        '''


# 全局无障碍管理器
accessibility_manager = AccessibilityManager()


def init_accessibility(app):
    """初始化无障碍功能"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_accessibility_context():
        """注入无障碍上下文到模板"""
        user_preferences = accessibility_manager.get_user_preferences()
        
        return {
            'a11y_manager': accessibility_manager,
            'a11y_preferences': user_preferences,
            'a11y_css': accessibility_manager.get_accessibility_css(user_preferences),
            'skip_links': accessibility_manager.create_skip_links(),
            'keyboard_shortcuts_help': accessibility_manager.generate_keyboard_shortcuts_help()
        }
    
    # 注册无障碍API路由
    @app.route('/api/accessibility/preferences', methods=['GET', 'POST'])
    def accessibility_preferences():
        """无障碍偏好设置API"""
        if request.method == 'GET':
            try:
                user_id = request.args.get('user_id', type=int)
                preferences = accessibility_manager.get_user_preferences(user_id)
                return {'preferences': preferences}
            except Exception as e:
                return {'error': str(e)}, 500
        
        elif request.method == 'POST':
            try:
                data = request.get_json()
                preferences = data.get('preferences', {})
                user_id = data.get('user_id')
                
                accessibility_manager.save_user_preferences(preferences, user_id)
                return {'message': '偏好设置已保存', 'preferences': preferences}
            except Exception as e:
                return {'error': str(e)}, 500
    
    @app.route('/api/accessibility/contrast-check', methods=['POST'])
    def contrast_check():
        """颜色对比度检查API"""
        try:
            data = request.get_json()
            foreground = data.get('foreground', '#000000')
            background = data.get('background', '#ffffff')
            text_size = data.get('text_size', 'normal')
            
            result = accessibility_manager.check_color_accessibility(
                foreground, background, text_size
            )
            return result
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/accessibility/validate-form', methods=['POST'])
    def validate_form():
        """表单无障碍验证API"""
        try:
            data = request.get_json()
            form_html = data.get('html', '')
            
            result = accessibility_manager.validate_form_accessibility(form_html)
            return result
        except Exception as e:
            return {'error': str(e)}, 500
    
    app.logger.info("无障碍功能已初始化")


def get_accessibility_manager():
    """获取无障碍管理器实例"""
    return accessibility_manager