# -*- coding: utf-8 -*-
"""
安全响应头配置
设置各种安全相关的HTTP响应头
防护XSS、点击劫持、内容类型嗅探等安全威胁
"""

from flask import request, g, current_app
from typing import Dict, Any, Optional, Callable
import re


class SecurityHeaders:
    """
    安全响应头中间件类
    自动为响应添加安全相关的HTTP头
    """
    
    def __init__(self, app=None):
        """
        初始化安全头中间件
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化Flask应用
        
        Args:
            app: Flask应用实例
        """
        # 设置默认安全头配置
        app.config.setdefault('SECURITY_HEADERS_ENABLED', True)
        
        # 内容安全策略 (CSP)
        app.config.setdefault('SECURITY_CSP_ENABLED', True)
        app.config.setdefault('SECURITY_CSP_POLICY', {
            'default-src': ["'self'"],
            'script-src': [
                "'self'", 
                "'unsafe-inline'",  # 允许内联脚本（开发时）
                "https://unpkg.com",  # HTMX CDN
                "https://cdn.tailwindcss.com",  # TailwindCSS CDN
                "https://cdnjs.cloudflare.com"  # 其他CDN资源
            ],
            'style-src': [
                "'self'", 
                "'unsafe-inline'",  # 允许内联样式
                "https://fonts.googleapis.com",
                "https://cdn.tailwindcss.com"
            ],
            'font-src': [
                "'self'", 
                "https://fonts.gstatic.com"
            ],
            'img-src': [
                "'self'", 
                "data:",  # 允许base64图片
                "https:"  # 允许HTTPS图片
            ],
            'connect-src': [
                "'self'",
                "https://api.example.com"  # API域名
            ],
            'frame-ancestors': ["'none'"],  # 防止iframe嵌入
            'object-src': ["'none'"],  # 禁用object/embed
            'base-uri': ["'self'"]  # 限制base标签
        })
        
        # X-Frame-Options
        app.config.setdefault('SECURITY_X_FRAME_OPTIONS', 'DENY')  # DENY, SAMEORIGIN
        
        # X-Content-Type-Options
        app.config.setdefault('SECURITY_X_CONTENT_TYPE_OPTIONS', 'nosniff')
        
        # X-XSS-Protection (已弃用，但某些旧浏览器需要)
        app.config.setdefault('SECURITY_X_XSS_PROTECTION', '1; mode=block')
        
        # Referrer Policy
        app.config.setdefault('SECURITY_REFERRER_POLICY', 'strict-origin-when-cross-origin')
        
        # Permissions Policy (Feature Policy)
        app.config.setdefault('SECURITY_PERMISSIONS_POLICY', {
            'geolocation': [],  # 禁用地理位置
            'microphone': [],   # 禁用麦克风
            'camera': [],       # 禁用摄像头
            'fullscreen': ["'self'"],  # 允许全屏
            'payment': []       # 禁用支付API
        })
        
        # Strict-Transport-Security (HSTS)
        app.config.setdefault('SECURITY_HSTS_ENABLED', True)
        app.config.setdefault('SECURITY_HSTS_MAX_AGE', 31536000)  # 1年
        app.config.setdefault('SECURITY_HSTS_INCLUDE_SUBDOMAINS', True)
        app.config.setdefault('SECURITY_HSTS_PRELOAD', True)
        
        # Cross-Origin相关
        app.config.setdefault('SECURITY_CROSS_ORIGIN_EMBEDDER_POLICY', 'require-corp')
        app.config.setdefault('SECURITY_CROSS_ORIGIN_OPENER_POLICY', 'same-origin')
        app.config.setdefault('SECURITY_CROSS_ORIGIN_RESOURCE_POLICY', 'same-origin')
        
        # 自定义头
        app.config.setdefault('SECURITY_CUSTOM_HEADERS', {
            'X-Powered-By': None,  # 移除X-Powered-By头
            'Server': 'Kronos-Stock',  # 自定义服务器标识
        })
        
        # 豁免路径（不应用某些安全头）
        app.config.setdefault('SECURITY_EXEMPT_PATHS', [
            '/api/webhook',  # Webhook可能需要特殊处理
        ])
        
        # 注册响应处理器
        @app.after_request
        def add_security_headers(response):
            """为所有响应添加安全头"""
            if app.config.get('SECURITY_HEADERS_ENABLED', True):
                self._add_security_headers(response)
            return response
        
        current_app.logger.info("安全响应头中间件已初始化")
    
    def _add_security_headers(self, response):
        """
        为响应添加安全头
        
        Args:
            response: Flask响应对象
        """
        try:
            # 检查是否豁免
            if self._is_exempt_path():
                return
            
            # 添加各种安全头
            self._add_csp_header(response)
            self._add_frame_options_header(response)
            self._add_content_type_options_header(response)
            self._add_xss_protection_header(response)
            self._add_referrer_policy_header(response)
            self._add_permissions_policy_header(response)
            self._add_hsts_header(response)
            self._add_cross_origin_headers(response)
            self._add_custom_headers(response)
            
        except Exception as e:
            current_app.logger.error(f"添加安全响应头异常: {str(e)}")
    
    def _is_exempt_path(self) -> bool:
        """
        检查当前路径是否豁免安全头
        
        Returns:
            是否豁免
        """
        exempt_paths = current_app.config.get('SECURITY_EXEMPT_PATHS', [])
        for path in exempt_paths:
            if request.path.startswith(path):
                return True
        return False
    
    def _add_csp_header(self, response):
        """
        添加内容安全策略头
        
        Args:
            response: Flask响应对象
        """
        if not current_app.config.get('SECURITY_CSP_ENABLED', True):
            return
        
        csp_policy = current_app.config.get('SECURITY_CSP_POLICY', {})
        if not csp_policy:
            return
        
        # 构建CSP字符串
        csp_parts = []
        for directive, sources in csp_policy.items():
            if sources:
                sources_str = ' '.join(sources)
                csp_parts.append(f"{directive} {sources_str}")
            else:
                csp_parts.append(f"{directive} 'none'")
        
        if csp_parts:
            csp_value = '; '.join(csp_parts)
            response.headers['Content-Security-Policy'] = csp_value
            
            # 同时设置X-Content-Security-Policy（向后兼容）
            response.headers['X-Content-Security-Policy'] = csp_value
    
    def _add_frame_options_header(self, response):
        """
        添加X-Frame-Options头
        
        Args:
            response: Flask响应对象
        """
        frame_options = current_app.config.get('SECURITY_X_FRAME_OPTIONS')
        if frame_options:
            response.headers['X-Frame-Options'] = frame_options
    
    def _add_content_type_options_header(self, response):
        """
        添加X-Content-Type-Options头
        
        Args:
            response: Flask响应对象
        """
        content_type_options = current_app.config.get('SECURITY_X_CONTENT_TYPE_OPTIONS')
        if content_type_options:
            response.headers['X-Content-Type-Options'] = content_type_options
    
    def _add_xss_protection_header(self, response):
        """
        添加X-XSS-Protection头
        
        Args:
            response: Flask响应对象
        """
        xss_protection = current_app.config.get('SECURITY_X_XSS_PROTECTION')
        if xss_protection:
            response.headers['X-XSS-Protection'] = xss_protection
    
    def _add_referrer_policy_header(self, response):
        """
        添加Referrer-Policy头
        
        Args:
            response: Flask响应对象
        """
        referrer_policy = current_app.config.get('SECURITY_REFERRER_POLICY')
        if referrer_policy:
            response.headers['Referrer-Policy'] = referrer_policy
    
    def _add_permissions_policy_header(self, response):
        """
        添加Permissions-Policy头
        
        Args:
            response: Flask响应对象
        """
        permissions_policy = current_app.config.get('SECURITY_PERMISSIONS_POLICY', {})
        if not permissions_policy:
            return
        
        # 构建Permissions Policy字符串
        policy_parts = []
        for feature, allowlist in permissions_policy.items():
            if allowlist:
                allowlist_str = ' '.join(f'"{item}"' if not item.startswith('"') else item 
                                       for item in allowlist)
                policy_parts.append(f"{feature}=({allowlist_str})")
            else:
                policy_parts.append(f"{feature}=()")
        
        if policy_parts:
            policy_value = ', '.join(policy_parts)
            response.headers['Permissions-Policy'] = policy_value
    
    def _add_hsts_header(self, response):
        """
        添加Strict-Transport-Security头
        
        Args:
            response: Flask响应对象
        """
        if not current_app.config.get('SECURITY_HSTS_ENABLED', True):
            return
        
        # 只在HTTPS连接时添加HSTS
        if not request.is_secure and not current_app.debug:
            return
        
        max_age = current_app.config.get('SECURITY_HSTS_MAX_AGE', 31536000)
        hsts_parts = [f"max-age={max_age}"]
        
        if current_app.config.get('SECURITY_HSTS_INCLUDE_SUBDOMAINS', True):
            hsts_parts.append('includeSubDomains')
        
        if current_app.config.get('SECURITY_HSTS_PRELOAD', True):
            hsts_parts.append('preload')
        
        hsts_value = '; '.join(hsts_parts)
        response.headers['Strict-Transport-Security'] = hsts_value
    
    def _add_cross_origin_headers(self, response):
        """
        添加跨域相关安全头
        
        Args:
            response: Flask响应对象
        """
        # Cross-Origin-Embedder-Policy
        coep = current_app.config.get('SECURITY_CROSS_ORIGIN_EMBEDDER_POLICY')
        if coep:
            response.headers['Cross-Origin-Embedder-Policy'] = coep
        
        # Cross-Origin-Opener-Policy
        coop = current_app.config.get('SECURITY_CROSS_ORIGIN_OPENER_POLICY')
        if coop:
            response.headers['Cross-Origin-Opener-Policy'] = coop
        
        # Cross-Origin-Resource-Policy
        corp = current_app.config.get('SECURITY_CROSS_ORIGIN_RESOURCE_POLICY')
        if corp:
            response.headers['Cross-Origin-Resource-Policy'] = corp
    
    def _add_custom_headers(self, response):
        """
        添加自定义头
        
        Args:
            response: Flask响应对象
        """
        custom_headers = current_app.config.get('SECURITY_CUSTOM_HEADERS', {})
        for header_name, header_value in custom_headers.items():
            if header_value is None:
                # 移除头（如果存在）
                response.headers.pop(header_name, None)
            else:
                response.headers[header_name] = header_value
    
    def update_csp_policy(self, updates: Dict[str, list]):
        """
        更新CSP策略
        
        Args:
            updates: CSP策略更新
        """
        current_policy = current_app.config.get('SECURITY_CSP_POLICY', {})
        current_policy.update(updates)
        current_app.config['SECURITY_CSP_POLICY'] = current_policy
        
        current_app.logger.info(f"CSP策略已更新: {updates}")
    
    def add_csp_source(self, directive: str, source: str):
        """
        为CSP指令添加源
        
        Args:
            directive: CSP指令名
            source: 要添加的源
        """
        current_policy = current_app.config.get('SECURITY_CSP_POLICY', {})
        if directive not in current_policy:
            current_policy[directive] = []
        
        if source not in current_policy[directive]:
            current_policy[directive].append(source)
            current_app.config['SECURITY_CSP_POLICY'] = current_policy
            current_app.logger.info(f"CSP源已添加: {directive} {source}")
    
    def remove_csp_source(self, directive: str, source: str):
        """
        从CSP指令中移除源
        
        Args:
            directive: CSP指令名
            source: 要移除的源
        """
        current_policy = current_app.config.get('SECURITY_CSP_POLICY', {})
        if directive in current_policy and source in current_policy[directive]:
            current_policy[directive].remove(source)
            current_app.config['SECURITY_CSP_POLICY'] = current_policy
            current_app.logger.info(f"CSP源已移除: {directive} {source}")


# 全局安全头实例
security_headers = SecurityHeaders()


def init_security_headers(app):
    """
    初始化安全响应头中间件
    
    Args:
        app: Flask应用实例
    """
    security_headers.init_app(app)


# 装饰器：临时修改CSP策略
def with_csp_policy(**policy_updates):
    """
    临时修改CSP策略的装饰器
    
    Args:
        **policy_updates: CSP策略更新
        
    Returns:
        装饰器函数
    """
    def decorator(f):
        from functools import wraps
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 保存原始策略
            original_policy = current_app.config.get('SECURITY_CSP_POLICY', {}).copy()
            
            try:
                # 临时更新策略
                security_headers.update_csp_policy(policy_updates)
                return f(*args, **kwargs)
            finally:
                # 恢复原始策略
                current_app.config['SECURITY_CSP_POLICY'] = original_policy
        
        return decorated_function
    return decorator


# 实用工具函数
def update_csp_policy(updates: Dict[str, list]):
    """
    更新CSP策略
    
    Args:
        updates: CSP策略更新
    """
    security_headers.update_csp_policy(updates)


def add_csp_source(directive: str, source: str):
    """
    添加CSP源
    
    Args:
        directive: CSP指令
        source: 源地址
    """
    security_headers.add_csp_source(directive, source)


def remove_csp_source(directive: str, source: str):
    """
    移除CSP源
    
    Args:
        directive: CSP指令
        source: 源地址
    """
    security_headers.remove_csp_source(directive, source)


def get_current_csp_policy() -> Dict[str, list]:
    """
    获取当前CSP策略
    
    Returns:
        CSP策略字典
    """
    return current_app.config.get('SECURITY_CSP_POLICY', {}).copy()


def is_secure_request() -> bool:
    """
    检查当前请求是否为安全连接
    
    Returns:
        是否为HTTPS请求
    """
    return request.is_secure or current_app.debug