# -*- coding: utf-8 -*-
"""
认证中间件
处理Bearer token验证、用户身份识别、权限检查
提供统一的认证和授权机制
"""

from flask import request, jsonify, g, current_app
from functools import wraps
import jwt
from datetime import datetime, timezone
import re
from typing import Optional, Dict, Any, Tuple

from app.services.auth_service import AuthService
from app.models.user import User
from app.models.user_session import UserSession


class AuthMiddleware:
    """
    认证中间件类
    处理JWT token验证、用户身份识别、权限管理
    """
    
    def __init__(self, app=None):
        """
        初始化认证中间件
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化Flask应用配置
        
        Args:
            app: Flask应用实例
        """
        # 设置默认配置
        app.config.setdefault('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        app.config.setdefault('JWT_ALGORITHM', 'HS256')
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRES', 3600)  # 1小时
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRES', 86400 * 30)  # 30天
        
        # 注册请求前处理器
        @app.before_request
        def load_user_from_token():
            """
            在每个请求前尝试从token中加载用户
            """
            self._load_user_from_request()
        
        # 注册错误处理器
        @app.errorhandler(401)
        def handle_unauthorized(error):
            """处理401未授权错误"""
            return jsonify({
                'success': False,
                'message': '认证失败，请重新登录',
                'code': 'UNAUTHORIZED'
            }), 401
        
        @app.errorhandler(403)
        def handle_forbidden(error):
            """处理403禁止访问错误"""
            return jsonify({
                'success': False,
                'message': '权限不足，无法访问此资源',
                'code': 'FORBIDDEN'
            }), 403
    
    def _load_user_from_request(self):
        """
        从请求中提取并验证用户token
        将用户信息存储在Flask的g对象中
        """
        # 清空之前的用户信息
        g.current_user = None
        g.current_user_id = None
        g.auth_token = None
        
        # 获取Authorization头
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return
        
        # 提取Bearer token
        token = self._extract_bearer_token(auth_header)
        if not token:
            return
        
        try:
            # 验证token并获取用户信息
            user_data = self._verify_token(token)
            if user_data:
                g.current_user = user_data
                g.current_user_id = user_data.get('user_id')
                g.auth_token = token
                
                # 记录最后活动时间
                self._update_last_activity(user_data.get('user_id'))
                
        except Exception as e:
            current_app.logger.warning(f"Token验证失败: {str(e)}")
            # 不抛出异常，让请求继续，但用户为未认证状态
    
    def _extract_bearer_token(self, auth_header: str) -> Optional[str]:
        """
        从Authorization头中提取Bearer token
        
        Args:
            auth_header: Authorization头内容
            
        Returns:
            提取的token字符串，如果格式错误返回None
        """
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # 移除 "Bearer " 前缀
        
        # 基本token格式验证
        if not token or len(token) < 10:
            return None
        
        return token
    
    def _verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT token并返回用户数据
        
        Args:
            token: JWT token字符串
            
        Returns:
            用户数据字典，验证失败返回None
        """
        try:
            # 解码JWT token
            payload = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=[current_app.config['JWT_ALGORITHM']]
            )
            
            # 检查token是否过期
            if 'exp' in payload:
                exp_timestamp = payload['exp']
                if datetime.fromtimestamp(exp_timestamp, tz=timezone.utc) < datetime.now(timezone.utc):
                    current_app.logger.warning("Token已过期")
                    return None
            
            # 检查必要字段
            user_id = payload.get('user_id')
            if not user_id:
                current_app.logger.warning("Token中缺少user_id字段")
                return None
            
            # 验证用户是否仍然存在且处于活跃状态
            user = User.query.get(user_id)
            if not user or not user.is_active:
                current_app.logger.warning(f"用户不存在或未激活: user_id={user_id}")
                return None
            
            # 检查session是否有效（如果有session_id）
            session_id = payload.get('session_id')
            if session_id:
                session = UserSession.query.filter_by(
                    id=session_id,
                    user_id=user_id,
                    is_active=True
                ).first()
                
                if not session or session.is_expired():
                    current_app.logger.warning(f"Session无效或已过期: session_id={session_id}")
                    return None
            
            # 返回用户数据
            return {
                'user_id': user_id,
                'email': user.email,
                'nickname': user.nickname,
                'is_verified': user.is_verified,
                'is_admin': user.is_admin,
                'session_id': session_id,
                'token_type': payload.get('type', 'access'),
                'issued_at': payload.get('iat'),
                'expires_at': payload.get('exp')
            }
            
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("JWT token已过期")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"JWT token无效: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Token验证异常: {str(e)}")
            return None
    
    def _update_last_activity(self, user_id: int):
        """
        更新用户最后活动时间
        
        Args:
            user_id: 用户ID
        """
        try:
            # 更新用户最后活动时间
            user = User.query.get(user_id)
            if user:
                user.last_activity_at = datetime.utcnow()
                
                # 更新session活动时间（如果存在）
                if hasattr(g, 'current_user') and g.current_user:
                    session_id = g.current_user.get('session_id')
                    if session_id:
                        session = UserSession.query.get(session_id)
                        if session:
                            session.last_activity_at = datetime.utcnow()
                
                # 提交数据库更改（在请求结束时）
                from app.models import db
                db.session.commit()
                
        except Exception as e:
            current_app.logger.error(f"更新用户活动时间失败: {str(e)}")
            # 不抛出异常，避免影响正常请求处理


# 认证装饰器函数
def login_required(f):
    """
    需要登录的装饰器
    确保用户已认证才能访问端点
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'success': False,
                'message': '需要登录才能访问此资源',
                'code': 'LOGIN_REQUIRED'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    需要管理员权限的装饰器
    确保用户是管理员才能访问端点
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'success': False,
                'message': '需要登录才能访问此资源',
                'code': 'LOGIN_REQUIRED'
            }), 401
        
        if not g.current_user.get('is_admin'):
            return jsonify({
                'success': False,
                'message': '需要管理员权限才能访问此资源',
                'code': 'ADMIN_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def verified_required(f):
    """
    需要邮箱验证的装饰器
    确保用户已验证邮箱才能访问端点
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_user') or not g.current_user:
            return jsonify({
                'success': False,
                'message': '需要登录才能访问此资源',
                'code': 'LOGIN_REQUIRED'
            }), 401
        
        if not g.current_user.get('is_verified'):
            return jsonify({
                'success': False,
                'message': '需要验证邮箱才能访问此资源',
                'code': 'EMAIL_VERIFICATION_REQUIRED'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def api_key_or_login_required(f):
    """
    API密钥或登录装饰器
    支持API密钥认证或用户登录认证
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 首先检查用户登录
        if hasattr(g, 'current_user') and g.current_user:
            return f(*args, **kwargs)
        
        # 检查API密钥
        api_key = request.headers.get('X-API-Key')
        if api_key:
            # 验证API密钥（这里可以扩展为从数据库验证）
            valid_api_keys = current_app.config.get('VALID_API_KEYS', [])
            if api_key in valid_api_keys:
                # 设置API用户信息
                g.current_user = {
                    'user_id': 'api',
                    'email': 'api@system',
                    'nickname': 'API用户',
                    'is_verified': True,
                    'is_admin': False,
                    'token_type': 'api_key'
                }
                return f(*args, **kwargs)
        
        return jsonify({
            'success': False,
            'message': '需要登录或有效的API密钥才能访问此资源',
            'code': 'AUTHENTICATION_REQUIRED'
        }), 401
    
    return decorated_function


def rate_limit_by_user(max_requests: int = 100, window_seconds: int = 3600):
    """
    按用户限制请求频率的装饰器
    
    Args:
        max_requests: 时间窗口内的最大请求数
        window_seconds: 时间窗口长度（秒）
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取用户标识
            user_key = 'anonymous'
            if hasattr(g, 'current_user') and g.current_user:
                user_key = f"user_{g.current_user_id}"
            else:
                # 使用IP作为匿名用户标识
                user_key = f"ip_{request.remote_addr}"
            
            # 这里可以集成Redis等缓存系统实现真正的限流
            # 当前简化实现，仅记录日志
            current_app.logger.info(f"速率限制检查: {user_key} 访问 {request.endpoint}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


# 实用工具函数
def get_current_user() -> Optional[Dict[str, Any]]:
    """
    获取当前认证用户信息
    
    Returns:
        用户信息字典，未认证时返回None
    """
    return getattr(g, 'current_user', None)


def get_current_user_id() -> Optional[int]:
    """
    获取当前认证用户ID
    
    Returns:
        用户ID，未认证时返回None
    """
    return getattr(g, 'current_user_id', None)


def is_authenticated() -> bool:
    """
    检查当前用户是否已认证
    
    Returns:
        是否已认证
    """
    return hasattr(g, 'current_user') and g.current_user is not None


def is_admin() -> bool:
    """
    检查当前用户是否为管理员
    
    Returns:
        是否为管理员
    """
    user = get_current_user()
    return user is not None and user.get('is_admin', False)


def is_verified() -> bool:
    """
    检查当前用户是否已验证邮箱
    
    Returns:
        是否已验证邮箱
    """
    user = get_current_user()
    return user is not None and user.get('is_verified', False)


# 创建中间件实例
auth_middleware = AuthMiddleware()


def init_auth_middleware(app):
    """
    初始化认证中间件
    
    Args:
        app: Flask应用实例
    """
    auth_middleware.init_app(app)
    
    # 记录初始化日志
    app.logger.info("认证中间件已初始化")