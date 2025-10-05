# -*- coding: utf-8 -*-
"""
优化的认证中间件
集成用户缓存服务，提升认证性能
"""

import logging
from datetime import datetime, timezone
from functools import wraps
from typing import Optional, Dict, Any

from flask import request, session, g, current_app, redirect, url_for, jsonify
from werkzeug.exceptions import Unauthorized

from app.services.user_cache_service import user_cache_service


class OptimizedAuthMiddleware:
    """优化的认证中间件，集成缓存策略"""
    
    def __init__(self, app=None):
        """
        初始化认证中间件
        
        Args:
            app: Flask应用实例
        """
        self.logger = logging.getLogger(__name__)
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化Flask应用配置"""
        # 认证配置
        app.config.setdefault('AUTH_EXEMPT_ROUTES', [
            'auth.login', 'auth.register', 'auth.forgot_password',
            'auth_api.login', 'auth_api.register', 'auth_api.forgot_password', 'auth_api.reset_password',
            'main.index', 'static',
            'legal.terms', 'legal.privacy'  # 法律页面无需登录
        ])
        app.config.setdefault('AUTH_LOGIN_URL', '/auth/login')
        app.config.setdefault('AUTH_SESSION_KEY', 'user_id')
        app.config.setdefault('AUTH_CACHE_ENABLED', True)
        app.config.setdefault('AUTH_CACHE_TTL', 3600)  # 1小时，与会话保持一致
        
        # 注册请求前处理器
        app.before_request(self._before_request)
        
        self.logger.info("优化认证中间件已初始化")
    
    def _before_request(self):
        """请求前认证检查"""
        # 清除之前的用户状态
        g.current_user = None
        g.user_authenticated = False
        
        # 获取当前路由
        endpoint = request.endpoint
        
        # 检查是否是免认证路由
        exempt_routes = current_app.config.get('AUTH_EXEMPT_ROUTES', [])
        if endpoint in exempt_routes:
            return
        
        # 静态文件免认证
        if endpoint and endpoint.startswith('static'):
            return
        
        # 检查用户认证状态
        user = self._get_current_user()
        
        if not user:
            return self._handle_unauthenticated_request()
        
        # 刷新活跃用户的会话
        self._refresh_active_session()
        
        # 设置全局用户状态
        g.current_user = user
        g.user_authenticated = True
    
    def _get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息（优先使用缓存）"""
        try:
            # 从会话获取用户ID
            session_key = current_app.config.get('AUTH_SESSION_KEY', 'user_id')
            user_id = session.get(session_key)
            
            if not user_id:
                return None
            
            # 检查是否启用缓存
            if current_app.config.get('AUTH_CACHE_ENABLED', True):
                # 尝试从缓存获取用户信息
                cached_user = user_cache_service.get_cached_user_info(user_id)
                if cached_user:
                    self.logger.debug(f"从缓存获取用户信息: user_id={user_id}")
                    return cached_user
            
            # 缓存未命中，从数据库获取
            user = self._load_user_from_database(user_id)
            
            if user and current_app.config.get('AUTH_CACHE_ENABLED', True):
                # 缓存用户信息
                cache_ttl = current_app.config.get('AUTH_CACHE_TTL', 300)
                user_cache_service.cache_user_info(user_id, user, cache_ttl)
                self.logger.debug(f"用户信息已缓存: user_id={user_id}")
            
            return user
            
        except Exception as e:
            self.logger.error(f"获取当前用户失败: {str(e)}")
            return None
    
    def _load_user_from_database(self, user_id: int) -> Optional[Dict[str, Any]]:
        """从数据库加载用户信息"""
        try:
            # 动态导入避免循环依赖
            from app.models.user import User
            
            user = User.query.get(user_id)
            if not user:
                return None
            
            # 检查用户状态
            if not user.is_active:
                self.logger.warning(f"用户账户已停用: user_id={user_id}")
                return None
            
            # 获取用户档案信息
            from app.models.user import UserProfile
            profile = UserProfile.query.filter_by(user_id=user.id).first()
            
            # 返回用户信息字典
            return {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'nickname': profile.nickname if profile else None,
                'avatar_url': profile.avatar_url if profile else None,
                'is_active': user.is_active,
                'role': user.role,
                'is_admin': user.role == 'admin',
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                '_loaded_at': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"从数据库加载用户失败: {str(e)}")
            return None
    
    def _handle_unauthenticated_request(self):
        """处理未认证的请求"""
        # API请求返回JSON错误
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'Authentication required',
                'message': '需要登录认证',
                'code': 'AUTH_REQUIRED'
            }), 401
        
        # AJAX请求返回JSON重定向
        if request.headers.get('HX-Request') or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            login_url = current_app.config.get('AUTH_LOGIN_URL', '/auth/login')
            return jsonify({
                'redirect': login_url,
                'message': '会话已过期，请重新登录'
            }), 401
        
        # 普通请求重定向到登录页面
        login_url = current_app.config.get('AUTH_LOGIN_URL', '/auth/login')
        return redirect(url_for('auth.login', next=request.url))
    
    def invalidate_user_cache(self, user_id: int):
        """使用户缓存失效"""
        try:
            user_cache_service.invalidate_user_all_cache(user_id)
            self.logger.info(f"用户缓存已失效: user_id={user_id}")
        except Exception as e:
            self.logger.error(f"用户缓存失效失败: {str(e)}")
    
    def _refresh_active_session(self):
        """刷新活跃用户的会话时间"""
        try:
            if 'user_id' in session and 'login_timestamp' in session:
                # 检查是否需要刷新（每30分钟刷新一次）
                login_time = session.get('login_timestamp', 0)
                current_time = datetime.now(timezone.utc).timestamp()
                
                if current_time - login_time > 1800:  # 30分钟
                    session['login_timestamp'] = current_time
                    session.permanent = True  # 确保会话持久性
                    self.logger.debug(f"刷新用户会话: user_id={session['user_id']}")
        except Exception as e:
            self.logger.error(f"刷新会话失败: {str(e)}")

    def refresh_user_cache(self, user_id: int):
        """刷新用户缓存"""
        try:
            # 先清除旧缓存
            user_cache_service.invalidate_user_all_cache(user_id)
            
            # 重新加载并缓存用户信息
            user = self._load_user_from_database(user_id)
            if user:
                cache_ttl = current_app.config.get('AUTH_CACHE_TTL', 300)
                user_cache_service.cache_user_info(user_id, user, cache_ttl)
                self.logger.info(f"用户缓存已刷新: user_id={user_id}")
                return user
            
            return None
            
        except Exception as e:
            self.logger.error(f"刷新用户缓存失败: {str(e)}")
            return None


# 创建全局认证中间件实例
optimized_auth_middleware = OptimizedAuthMiddleware()


def init_optimized_auth_middleware(app):
    """初始化优化认证中间件"""
    optimized_auth_middleware.init_app(app)
    return optimized_auth_middleware