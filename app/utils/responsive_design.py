"""
响应式设计工具和样式
用于提供响应式布局、断点管理和自适应组件
"""
from typing import Dict, List, Optional, Any
from flask import request
import json
import re

# 尝试导入user_agents，如果不存在则使用简单的解析器
try:
    from user_agents import parse
    HAS_USER_AGENTS = True
except ImportError:
    HAS_USER_AGENTS = False
    
    class MockUserAgent:
        def __init__(self, ua_string):
            self.ua_string = ua_string.lower()
            
        @property
        def is_mobile(self):
            return any(keyword in self.ua_string for keyword in [
                'mobile', 'android', 'iphone', 'ipod', 'blackberry', 'nokia'
            ])
            
        @property
        def is_tablet(self):
            return any(keyword in self.ua_string for keyword in [
                'tablet', 'ipad', 'kindle', 'silk'
            ])
            
        @property
        def is_pc(self):
            return not (self.is_mobile or self.is_tablet)
            
        @property
        def is_bot(self):
            return any(keyword in self.ua_string for keyword in [
                'bot', 'crawler', 'spider', 'scraper'
            ])
            
        @property
        def browser(self):
            return type('Browser', (), {
                'family': 'Unknown',
                'version_string': '1.0'
            })()
            
        @property
        def os(self):
            return type('OS', (), {
                'family': 'Unknown',
                'version_string': '1.0'
            })()
            
        @property
        def device(self):
            return type('Device', (), {
                'family': 'Unknown',
                'brand': 'Unknown',
                'model': 'Unknown'
            })()
    
    def parse(ua_string):
        return MockUserAgent(ua_string)


class ResponsiveDesignManager:
    """响应式设计管理器"""
    
    def __init__(self):
        # 响应式断点配置（基于TailwindCSS）
        self.breakpoints = {
            'xs': {'min': 0, 'max': 479, 'name': '超小屏幕'},
            'sm': {'min': 480, 'max': 767, 'name': '小屏幕'},
            'md': {'min': 768, 'max': 1023, 'name': '中等屏幕'},
            'lg': {'min': 1024, 'max': 1279, 'name': '大屏幕'},
            'xl': {'min': 1280, 'max': 1535, 'name': '超大屏幕'},
            '2xl': {'min': 1536, 'max': float('inf'), 'name': '2K屏幕'}
        }
        
        # 设备类型映射
        self.device_types = {
            'mobile': ['xs', 'sm'],
            'tablet': ['md'],
            'desktop': ['lg', 'xl', '2xl']
        }
        
        # 组件响应式配置模板
        self.component_configs = {
            'grid': {
                'xs': {'columns': 1, 'gap': '0.5rem'},
                'sm': {'columns': 2, 'gap': '0.75rem'},
                'md': {'columns': 3, 'gap': '1rem'},
                'lg': {'columns': 4, 'gap': '1.25rem'},
                'xl': {'columns': 5, 'gap': '1.5rem'},
                '2xl': {'columns': 6, 'gap': '2rem'}
            },
            'typography': {
                'xs': {'base_size': '14px', 'line_height': '1.4'},
                'sm': {'base_size': '15px', 'line_height': '1.5'},
                'md': {'base_size': '16px', 'line_height': '1.6'},
                'lg': {'base_size': '17px', 'line_height': '1.6'},
                'xl': {'base_size': '18px', 'line_height': '1.7'},
                '2xl': {'base_size': '20px', 'line_height': '1.8'}
            },
            'spacing': {
                'xs': {'padding': '0.5rem', 'margin': '0.25rem'},
                'sm': {'padding': '0.75rem', 'margin': '0.5rem'},
                'md': {'padding': '1rem', 'margin': '0.75rem'},
                'lg': {'padding': '1.5rem', 'margin': '1rem'},
                'xl': {'padding': '2rem', 'margin': '1.5rem'},
                '2xl': {'padding': '3rem', 'margin': '2rem'}
            }
        }
    
    def detect_device_info(self, user_agent_string: str = None) -> Dict[str, Any]:
        """检测设备信息"""
        if user_agent_string is None:
            user_agent_string = request.headers.get('User-Agent', '')
        
        try:
            user_agent = parse(user_agent_string)
            
            device_info = {
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_pc': user_agent.is_pc,
                'is_bot': user_agent.is_bot,
                'browser': {
                    'family': user_agent.browser.family,
                    'version': user_agent.browser.version_string
                },
                'os': {
                    'family': user_agent.os.family,
                    'version': user_agent.os.version_string
                },
                'device': {
                    'family': user_agent.device.family,
                    'brand': user_agent.device.brand,
                    'model': user_agent.device.model
                }
            }
            
            # 推断设备类型
            if user_agent.is_mobile:
                device_info['device_type'] = 'mobile'
                device_info['suggested_breakpoint'] = 'xs'
            elif user_agent.is_tablet:
                device_info['device_type'] = 'tablet'
                device_info['suggested_breakpoint'] = 'md'
            else:
                device_info['device_type'] = 'desktop'
                device_info['suggested_breakpoint'] = 'lg'
            
            return device_info
            
        except Exception as e:
            return {
                'error': str(e),
                'device_type': 'desktop',
                'suggested_breakpoint': 'lg'
            }
    
    def get_breakpoint_by_width(self, width: int) -> str:
        """根据屏幕宽度获取断点"""
        for breakpoint, config in self.breakpoints.items():
            if config['min'] <= width <= config['max']:
                return breakpoint
        return 'lg'  # 默认断点
    
    def get_component_config(self, component_type: str, breakpoint: str = None) -> Dict:
        """获取组件的响应式配置"""
        if breakpoint is None:
            # 尝试从请求中获取设备信息
            device_info = self.detect_device_info()
            breakpoint = device_info.get('suggested_breakpoint', 'lg')
        
        component_config = self.component_configs.get(component_type, {})
        return component_config.get(breakpoint, component_config.get('lg', {}))
    
    def generate_responsive_classes(self, base_classes: Dict[str, str]) -> str:
        """生成响应式CSS类"""
        css_classes = []
        
        for breakpoint, classes in base_classes.items():
            if breakpoint == 'default':
                css_classes.append(classes)
            else:
                # 添加响应式前缀
                prefixed_classes = ' '.join([
                    f"{breakpoint}:{cls}" for cls in classes.split()
                ])
                css_classes.append(prefixed_classes)
        
        return ' '.join(css_classes)
    
    def create_responsive_grid_config(self, items_count: int, breakpoint: str = None) -> Dict:
        """创建响应式网格配置"""
        if breakpoint is None:
            device_info = self.detect_device_info()
            breakpoint = device_info.get('suggested_breakpoint', 'lg')
        
        grid_config = self.get_component_config('grid', breakpoint)
        
        # 根据项目数量调整列数
        optimal_columns = min(grid_config.get('columns', 3), items_count)
        
        return {
            'columns': optimal_columns,
            'gap': grid_config.get('gap', '1rem'),
            'css_grid': f"repeat({optimal_columns}, 1fr)",
            'grid_template_columns': f"grid-template-columns: repeat({optimal_columns}, 1fr)",
            'gap_style': f"gap: {grid_config.get('gap', '1rem')}"
        }
    
    def get_responsive_image_config(self, breakpoint: str = None) -> Dict:
        """获取响应式图片配置"""
        if breakpoint is None:
            device_info = self.detect_device_info()
            breakpoint = device_info.get('suggested_breakpoint', 'lg')
        
        image_configs = {
            'xs': {'width': '100%', 'max_width': '300px', 'quality': 70},
            'sm': {'width': '100%', 'max_width': '400px', 'quality': 75},
            'md': {'width': '100%', 'max_width': '600px', 'quality': 80},
            'lg': {'width': '100%', 'max_width': '800px', 'quality': 85},
            'xl': {'width': '100%', 'max_width': '1000px', 'quality': 90},
            '2xl': {'width': '100%', 'max_width': '1200px', 'quality': 95}
        }
        
        return image_configs.get(breakpoint, image_configs['lg'])
    
    def optimize_layout_for_device(self, layout_config: Dict, device_info: Dict = None) -> Dict:
        """为设备优化布局配置"""
        if device_info is None:
            device_info = self.detect_device_info()
        
        device_type = device_info.get('device_type', 'desktop')
        breakpoint = device_info.get('suggested_breakpoint', 'lg')
        
        optimized_config = layout_config.copy()
        
        # 移动设备优化
        if device_type == 'mobile':
            optimized_config.update({
                'sidebar_collapsed': True,
                'navigation_style': 'bottom',
                'font_size_scale': 0.9,
                'touch_target_size': '44px',
                'scroll_behavior': 'smooth'
            })
        
        # 平板设备优化
        elif device_type == 'tablet':
            optimized_config.update({
                'sidebar_collapsed': False,
                'navigation_style': 'side',
                'font_size_scale': 1.0,
                'touch_target_size': '40px',
                'two_column_layout': True
            })
        
        # 桌面设备优化
        else:
            optimized_config.update({
                'sidebar_collapsed': False,
                'navigation_style': 'top',
                'font_size_scale': 1.1,
                'hover_effects': True,
                'multi_column_layout': True
            })
        
        # 添加通用响应式配置
        optimized_config['breakpoint'] = breakpoint
        optimized_config['spacing'] = self.get_component_config('spacing', breakpoint)
        optimized_config['typography'] = self.get_component_config('typography', breakpoint)
        
        return optimized_config
    
    def get_viewport_meta_tag(self, device_info: Dict = None) -> str:
        """获取视窗meta标签"""
        if device_info is None:
            device_info = self.detect_device_info()
        
        # 基础视窗配置
        base_config = "width=device-width, initial-scale=1.0"
        
        # 根据设备类型调整
        if device_info.get('is_mobile'):
            # 移动设备：防止缩放，优化触摸体验
            return f"{base_config}, maximum-scale=1.0, user-scalable=no"
        elif device_info.get('is_tablet'):
            # 平板设备：允许适度缩放
            return f"{base_config}, maximum-scale=2.0, user-scalable=yes"
        else:
            # 桌面设备：标准配置
            return base_config
    
    def get_device_specific_styles(self, device_info: Dict = None) -> str:
        """获取设备特定的CSS样式"""
        if device_info is None:
            device_info = self.detect_device_info()
        
        device_type = device_info.get('device_type', 'desktop')
        breakpoint = device_info.get('suggested_breakpoint', 'lg')
        
        styles = []
        
        # 基础响应式样式
        styles.append("""
        /* 响应式基础样式 */
        * {
            box-sizing: border-box;
        }
        
        .responsive-container {
            width: 100%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
        }
        
        .responsive-grid {
            display: grid;
            gap: 1rem;
        }
        
        .responsive-flex {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
        }
        """)
        
        # 移动设备专用样式
        if device_type == 'mobile':
            styles.append("""
            /* 移动设备样式 */
            @media (max-width: 767px) {
                .responsive-container {
                    padding: 0 0.5rem;
                }
                
                .responsive-grid {
                    grid-template-columns: 1fr;
                    gap: 0.5rem;
                }
                
                .mobile-hidden {
                    display: none !important;
                }
                
                .mobile-full-width {
                    width: 100% !important;
                }
                
                .mobile-center {
                    text-align: center !important;
                }
                
                .touch-target {
                    min-height: 44px;
                    min-width: 44px;
                }
            }
            """)
        
        # 平板设备专用样式
        elif device_type == 'tablet':
            styles.append("""
            /* 平板设备样式 */
            @media (min-width: 768px) and (max-width: 1023px) {
                .responsive-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .tablet-hidden {
                    display: none !important;
                }
                
                .tablet-stack {
                    flex-direction: column !important;
                }
            }
            """)
        
        # 桌面设备专用样式
        else:
            styles.append("""
            /* 桌面设备样式 */
            @media (min-width: 1024px) {
                .responsive-grid {
                    grid-template-columns: repeat(3, 1fr);
                }
                
                .desktop-hidden {
                    display: none !important;
                }
                
                .hover-lift:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }
            }
            """)
        
        return '\n'.join(styles)


# 全局响应式设计管理器
responsive_manager = ResponsiveDesignManager()


def init_responsive_design(app):
    """初始化响应式设计功能"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_responsive_context():
        """注入响应式上下文到模板"""
        device_info = responsive_manager.detect_device_info()
        
        return {
            'device_info': device_info,
            'responsive_manager': responsive_manager,
            'breakpoints': responsive_manager.breakpoints,
            'viewport_meta': responsive_manager.get_viewport_meta_tag(device_info),
            'device_styles': responsive_manager.get_device_specific_styles(device_info)
        }
    
    # 注册响应式设计API
    @app.route('/api/responsive/device-info')
    def get_device_info():
        """获取设备信息API"""
        try:
            device_info = responsive_manager.detect_device_info()
            return device_info
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/responsive/layout-config')
    def get_layout_config():
        """获取布局配置API"""
        try:
            device_info = responsive_manager.detect_device_info()
            
            # 获取布局配置参数
            layout_type = request.args.get('type', 'default')
            items_count = int(request.args.get('items', 6))
            
            config = {
                'device_info': device_info,
                'grid_config': responsive_manager.create_responsive_grid_config(items_count),
                'image_config': responsive_manager.get_responsive_image_config(),
                'layout_config': responsive_manager.optimize_layout_for_device({
                    'layout_type': layout_type
                })
            }
            
            return config
        except Exception as e:
            return {'error': str(e)}, 500
    
    app.logger.info("响应式设计功能已初始化")


def get_responsive_manager():
    """获取响应式设计管理器实例"""
    return responsive_manager