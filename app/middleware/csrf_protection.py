# -*- coding: utf-8 -*-
"""
CSRF保护配置
防止跨站请求伪造攻击
提供Token验证和安全头设置
"""

from flask import request, session, jsonify, render_template_string, g, current_app
from functools import wraps
import secrets
import hmac
import hashlib
import time
from typing import Optional, Dict, Any
import base64
import json


class CSRFProtection:
    """
    CSRF保护类
    实现基于Token的CSRF保护机制
    """
    
    def __init__(self, app=None):
        """
        初始化CSRF保护
        
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
        # 设置默认配置
        app.config.setdefault('CSRF_ENABLED', True)
        app.config.setdefault('CSRF_SECRET_KEY', None)  # 使用应用SECRET_KEY
        app.config.setdefault('CSRF_TOKEN_TIMEOUT', 3600)  # 1小时过期
        app.config.setdefault('CSRF_HEADER_NAME', 'X-CSRFToken')
        app.config.setdefault('CSRF_FIELD_NAME', 'csrf_token')
        app.config.setdefault('CSRF_COOKIE_NAME', 'csrf_token')
        app.config.setdefault('CSRF_COOKIE_SECURE', True)  # HTTPS环境
        app.config.setdefault('CSRF_COOKIE_HTTPONLY', False)  # JS需要访问
        app.config.setdefault('CSRF_COOKIE_SAMESITE', 'Lax')
        
        # 豁免路径（不需要CSRF保护）
        app.config.setdefault('CSRF_EXEMPT_PATHS', [
            '/api/health',
            '/api/status',
            '/auth/login',  # 登录页面GET请求
            '/static',
            '/favicon.ico'
        ])
        
        # 豁免的HTTP方法
        app.config.setdefault('CSRF_EXEMPT_METHODS', ['GET', 'HEAD', 'OPTIONS', 'TRACE'])
        
        # 注册模板全局函数
        @app.template_global()
        def csrf_token():
            """模板中生成CSRF token"""
            return self.generate_csrf_token()
        
        # 注册请求处理器
        @app.before_request
        def csrf_protect():
            """在每个请求前进行CSRF保护检查"""
            if app.config.get('CSRF_ENABLED', True):
                self._protect_request()
        
        # 注册错误处理器
        @app.errorhandler(403)
        def csrf_error_handler(error):
            """处理CSRF验证失败"""
            if hasattr(error, 'csrf_error'):
                return self._handle_csrf_error(error)
            return error
        
        # 注册模板上下文处理器
        @app.context_processor
        def inject_csrf_token():
            """向模板注入CSRF token"""
            return {'csrf_token': self.generate_csrf_token}
        
        current_app.logger.info("CSRF保护已初始化")
    
    def _protect_request(self):
        """
        保护当前请求免受CSRF攻击
        """
        try:
            # 检查是否需要CSRF保护
            if not self._should_protect_request():
                return
            
            # 验证CSRF token
            if not self._validate_csrf_token():
                current_app.logger.warning(f"CSRF验证失败: {request.method} {request.path}")
                self._abort_csrf_error("CSRF token验证失败")
            
        except Exception as e:
            current_app.logger.error(f"CSRF保护异常: {str(e)}")
            if current_app.debug:
                raise
    
    def _should_protect_request(self) -> bool:
        """
        检查当前请求是否需要CSRF保护
        
        Returns:
            是否需要保护
        """
        # 检查HTTP方法
        exempt_methods = current_app.config.get('CSRF_EXEMPT_METHODS', [])
        if request.method in exempt_methods:
            return False
        
        # 检查路径豁免
        exempt_paths = current_app.config.get('CSRF_EXEMPT_PATHS', [])
        for path in exempt_paths:
            if request.path.startswith(path):
                return False
        
        # 检查是否为AJAX请求且同源
        if self._is_same_origin_ajax():
            return False
        
        # 检查内容类型豁免
        content_type = request.content_type or ''
        if content_type.startswith('application/json') and self._is_api_request():
            # API请求使用其他认证方式（如JWT）
            return False
        
        return True
    
    def _is_same_origin_ajax(self) -> bool:
        """
        检查是否为同源AJAX请求
        
        Returns:
            是否为同源AJAX请求
        """
        # 检查X-Requested-With头
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # 检查Referer是否同源
            referer = request.headers.get('Referer', '')
            if referer:
                from urllib.parse import urlparse
                referer_host = urlparse(referer).netloc
                request_host = request.headers.get('Host', '')
                return referer_host == request_host
        
        return False
    
    def _is_api_request(self) -> bool:
        """
        检查是否为API请求
        
        Returns:
            是否为API请求
        """
        return request.path.startswith('/api/')
    
    def _validate_csrf_token(self) -> bool:
        """
        验证CSRF token
        
        Returns:
            验证是否成功
        """
        # 获取token
        token = self._get_csrf_token_from_request()
        if not token:
            return False
        
        # 验证token
        return self._verify_csrf_token(token)
    
    def _get_csrf_token_from_request(self) -> Optional[str]:
        """
        从请求中获取CSRF token
        
        Returns:
            CSRF token字符串
        """
        # 1. 从表单字段获取
        field_name = current_app.config.get('CSRF_FIELD_NAME', 'csrf_token')
        token = request.form.get(field_name)
        if token:
            return token
        
        # 2. 从HTTP头获取
        header_name = current_app.config.get('CSRF_HEADER_NAME', 'X-CSRFToken')
        token = request.headers.get(header_name)
        if token:
            return token
        
        # 3. 从Cookie获取（不推荐，但支持）
        cookie_name = current_app.config.get('CSRF_COOKIE_NAME', 'csrf_token')
        token = request.cookies.get(cookie_name)
        if token:
            return token
        
        # 4. 从JSON数据获取
        if request.is_json and isinstance(request.json, dict):
            token = request.json.get(field_name)
            if token:
                return token
        
        return None
    
    def generate_csrf_token(self) -> str:
        """
        生成CSRF token
        
        Returns:
            CSRF token字符串
        """
        try:
            # 从session获取或生成新的token
            if 'csrf_token' not in session:
                session['csrf_token'] = self._generate_new_token()
                session['csrf_token_time'] = time.time()
            else:
                # 检查token是否过期
                token_time = session.get('csrf_token_time', 0)
                timeout = current_app.config.get('CSRF_TOKEN_TIMEOUT', 3600)
                if time.time() - token_time > timeout:
                    session['csrf_token'] = self._generate_new_token()
                    session['csrf_token_time'] = time.time()
            
            return session['csrf_token']
            
        except Exception as e:
            current_app.logger.error(f"生成CSRF token异常: {str(e)}")
            return self._generate_new_token()
    
    def _generate_new_token(self) -> str:
        """
        生成新的CSRF token
        
        Returns:
            新的token字符串
        """
        # 生成随机数据
        random_data = secrets.token_bytes(32)
        timestamp = str(int(time.time())).encode()
        
        # 获取密钥
        secret_key = current_app.config.get('CSRF_SECRET_KEY') or current_app.secret_key
        if isinstance(secret_key, str):
            secret_key = secret_key.encode()
        
        # 生成签名
        message = random_data + timestamp
        signature = hmac.new(secret_key, message, hashlib.sha256).digest()
        
        # 组合token
        token_data = {
            'data': base64.b64encode(random_data).decode(),
            'timestamp': int(time.time()),
            'signature': base64.b64encode(signature).decode()
        }
        
        # 编码为base64
        token_json = json.dumps(token_data, separators=(',', ':'))
        return base64.b64encode(token_json.encode()).decode()
    
    def _verify_csrf_token(self, token: str) -> bool:
        """
        验证CSRF token
        
        Args:
            token: 要验证的token
            
        Returns:
            验证是否成功
        """
        try:
            # 解码token
            token_json = base64.b64decode(token.encode()).decode()
            token_data = json.loads(token_json)
            
            # 检查token结构
            if not all(key in token_data for key in ['data', 'timestamp', 'signature']):
                return False
            
            # 检查时间戳
            timestamp = token_data['timestamp']
            timeout = current_app.config.get('CSRF_TOKEN_TIMEOUT', 3600)
            if time.time() - timestamp > timeout:
                current_app.logger.warning("CSRF token已过期")
                return False
            
            # 验证签名
            random_data = base64.b64decode(token_data['data'])
            timestamp_bytes = str(timestamp).encode()
            message = random_data + timestamp_bytes
            
            secret_key = current_app.config.get('CSRF_SECRET_KEY') or current_app.secret_key
            if isinstance(secret_key, str):
                secret_key = secret_key.encode()
            
            expected_signature = hmac.new(secret_key, message, hashlib.sha256).digest()
            actual_signature = base64.b64decode(token_data['signature'])
            
            return hmac.compare_digest(expected_signature, actual_signature)
            
        except Exception as e:
            current_app.logger.warning(f"CSRF token验证异常: {str(e)}")
            return False
    
    def _abort_csrf_error(self, message: str = "CSRF验证失败"):
        """
        抛出CSRF错误
        
        Args:
            message: 错误消息
        """
        from flask import abort
        
        # 创建自定义错误
        error = Exception(message)
        error.csrf_error = True
        
        abort(403, description=message)
    
    def _handle_csrf_error(self, error):
        """
        处理CSRF错误
        
        Args:
            error: 错误对象
            
        Returns:
            错误响应
        """
        error_data = {
            'error': 'CSRF验证失败',
            'message': '请求被拒绝，可能是由于安全令牌无效',
            'code': 'CSRF_TOKEN_INVALID'
        }
        
        # API请求返回JSON
        if request.path.startswith('/api/') or request.is_json:
            return jsonify(error_data), 403
        
        # Web请求返回HTML页面
        error_template = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>请求被拒绝</title>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { font-family: Arial, sans-serif; margin: 50px; text-align: center; }
                .error { color: #d73502; }
                .message { margin: 20px 0; }
                .retry { margin-top: 30px; }
                button { padding: 10px 20px; background: #007cba; color: white; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1 class="error">请求被拒绝</h1>
            <p class="message">您的请求由于安全原因被拒绝，请刷新页面后重试。</p>
            <div class="retry">
                <button onclick="location.reload()">刷新页面</button>
                <button onclick="history.back()">返回</button>
            </div>
        </body>
        </html>
        '''
        
        return render_template_string(error_template), 403
    
    def exempt(self, f):
        """
        豁免CSRF保护的装饰器
        
        Args:
            f: 被装饰的视图函数
            
        Returns:
            装饰器函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 标记为豁免CSRF
            g.csrf_exempt = True
            return f(*args, **kwargs)
        
        return decorated_function
    
    def protect(self, f):
        """
        强制CSRF保护的装饰器
        
        Args:
            f: 被装饰的视图函数
            
        Returns:
            装饰器函数
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 强制CSRF保护
            if current_app.config.get('CSRF_ENABLED', True):
                if not self._validate_csrf_token():
                    self._abort_csrf_error("CSRF token验证失败")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    def get_csrf_token(self) -> str:
        """
        获取当前CSRF token
        
        Returns:
            CSRF token字符串
        """
        return self.generate_csrf_token()
    
    def validate_token(self, token: str) -> bool:
        """
        验证给定的CSRF token
        
        Args:
            token: 要验证的token
            
        Returns:
            验证是否成功
        """
        return self._verify_csrf_token(token)


# 全局CSRF保护实例
csrf_protection = CSRFProtection()


def init_csrf_protection(app):
    """
    初始化CSRF保护
    
    Args:
        app: Flask应用实例
    """
    csrf_protection.init_app(app)


# 装饰器快捷方式
def csrf_exempt(f):
    """CSRF豁免装饰器"""
    return csrf_protection.exempt(f)


def csrf_protect(f):
    """CSRF保护装饰器"""
    return csrf_protection.protect(f)


# 实用工具函数
def generate_csrf_token() -> str:
    """
    生成CSRF token
    
    Returns:
        CSRF token字符串
    """
    return csrf_protection.generate_csrf_token()


def validate_csrf_token(token: str) -> bool:
    """
    验证CSRF token
    
    Args:
        token: 要验证的token
        
    Returns:
        验证是否成功
    """
    return csrf_protection.validate_token(token)


def get_csrf_token() -> str:
    """
    获取当前CSRF token
    
    Returns:
        CSRF token字符串
    """
    return csrf_protection.get_csrf_token()