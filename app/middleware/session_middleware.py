# -*- coding: utf-8 -*-
"""
会话管理中间件
处理用户会话创建、更新、过期清理
提供统一的会话管理机制
"""

from flask import request, session, g, current_app
from datetime import datetime, timedelta
import uuid
import hashlib
import os
from typing import Optional, Dict, Any
import json

from app.models.user import User


class SessionMiddleware:
    """
    会话管理中间件类
    处理用户会话的生命周期管理
    """
    
    def __init__(self, app=None):
        """
        初始化会话中间件
        
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
        app.config.setdefault('SESSION_COOKIE_SECURE', True)  # HTTPS环境下启用
        app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)  # 防止XSS
        app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')  # CSRF保护
        app.config.setdefault('PERMANENT_SESSION_LIFETIME', timedelta(days=30))  # 30天过期
        app.config.setdefault('SESSION_REGENERATE_AFTER', 3600)  # 1小时后重新生成session ID
        app.config.setdefault('SESSION_MAX_IDLE_TIME', 1800)  # 30分钟无活动后过期
        
        # 注册请求处理器
        @app.before_request
        def manage_session():
            """
            在每个请求前处理会话
            """
            self._manage_session()
        
        @app.after_request
        def update_session(response):
            """
            在每个请求后更新会话
            """
            self._update_session()
            return response
        
        # 注册定期清理任务（需要外部调度器）
        self._register_cleanup_task(app)
    
    def _manage_session(self):
        """
        管理当前请求的会话
        检查会话有效性、重新生成过期会话等
        """
        try:
            # 检查会话是否存在
            if 'session_id' not in session:
                # 创建新会话
                self._create_new_session()
                return
            
            # 验证会话有效性
            session_id = session['session_id']
            session_data = self._get_session_data(session_id)
            
            if not session_data:
                # 会话不存在，创建新会话
                current_app.logger.warning(f"会话不存在，创建新会话: {session_id}")
                self._create_new_session()
                return
            
            # 检查会话是否过期
            if self._is_session_expired(session_data):
                current_app.logger.info(f"会话已过期，创建新会话: {session_id}")
                self._cleanup_expired_session(session_id)
                self._create_new_session()
                return
            
            # 检查是否需要重新生成session ID
            if self._should_regenerate_session(session_data):
                current_app.logger.info(f"重新生成会话ID: {session_id}")
                self._regenerate_session_id(session_data)
            
            # 更新最后活动时间
            self._update_session_activity(session_id)
            
            # 将会话数据加载到g对象
            g.session_data = session_data
            
        except Exception as e:
            current_app.logger.error(f"会话管理异常: {str(e)}")
            # 出现异常时创建新会话
            self._create_new_session()
    
    def _update_session(self):
        """
        更新会话信息
        在请求结束时保存会话状态
        """
        try:
            if 'session_id' not in session:
                return
            
            session_id = session['session_id']
            
            # 更新会话元数据
            update_data = {
                'last_activity_at': datetime.utcnow().isoformat(),
                'request_count': session.get('request_count', 0) + 1,
                'last_ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')[:500]  # 限制长度
            }
            
            # 如果用户已登录，更新用户信息
            if hasattr(g, 'current_user') and g.current_user:
                update_data['user_id'] = g.current_user_id
                update_data['user_email'] = g.current_user.get('email')
            
            session.update(update_data)
            session.permanent = True  # 启用永久会话
            
            # 保存到数据库或缓存（简化实现，使用session存储）
            self._save_session_data(session_id, update_data)
            
        except Exception as e:
            current_app.logger.error(f"更新会话异常: {str(e)}")
    
    def _create_new_session(self):
        """
        创建新的会话
        """
        try:
            # 生成新的session ID
            session_id = self._generate_session_id()
            
            # 创建会话数据
            session_data = {
                'session_id': session_id,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity_at': datetime.utcnow().isoformat(),
                'user_id': None,
                'user_email': None,
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')[:500],
                'request_count': 0,
                'is_active': True
            }
            
            # 保存会话
            session.clear()
            session['session_id'] = session_id
            session['created_at'] = session_data['created_at']
            session.permanent = True
            
            # 保存到存储
            self._save_session_data(session_id, session_data)
            
            current_app.logger.info(f"创建新会话: {session_id}")
            
        except Exception as e:
            current_app.logger.error(f"创建会话异常: {str(e)}")
    
    def _generate_session_id(self) -> str:
        """
        生成安全的session ID
        
        Returns:
            session ID字符串
        """
        # 生成随机数据
        random_data = os.urandom(32)
        timestamp = str(datetime.utcnow().timestamp())
        remote_addr = request.remote_addr or 'unknown'
        
        # 组合数据并生成hash
        combined_data = f"{random_data.hex()}{timestamp}{remote_addr}"
        session_id = hashlib.sha256(combined_data.encode()).hexdigest()
        
        return session_id
    
    def _get_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        获取会话数据
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话数据字典，不存在时返回None
        """
        try:
            # 简化实现：从Flask session中获取
            # 实际项目中可以从数据库或Redis获取
            if session.get('session_id') == session_id:
                return {
                    'session_id': session_id,
                    'created_at': session.get('created_at'),
                    'last_activity_at': session.get('last_activity_at'),
                    'user_id': session.get('user_id'),
                    'user_email': session.get('user_email'),
                    'ip_address': session.get('ip_address'),
                    'user_agent': session.get('user_agent'),
                    'request_count': session.get('request_count', 0),
                    'is_active': True
                }
            return None
            
        except Exception as e:
            current_app.logger.error(f"获取会话数据异常: {str(e)}")
            return None
    
    def _save_session_data(self, session_id: str, data: Dict[str, Any]):
        """
        保存会话数据
        
        Args:
            session_id: 会话ID
            data: 会话数据
        """
        try:
            # 简化实现：保存到Flask session
            # 实际项目中应该保存到数据库或Redis
            for key, value in data.items():
                if key != 'session_id':  # session_id已经设置
                    session[key] = value
                    
        except Exception as e:
            current_app.logger.error(f"保存会话数据异常: {str(e)}")
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """
        检查会话是否过期
        
        Args:
            session_data: 会话数据
            
        Returns:
            是否过期
        """
        try:
            # 检查绝对过期时间
            created_at = datetime.fromisoformat(session_data['created_at'])
            max_lifetime = current_app.config.get('PERMANENT_SESSION_LIFETIME', timedelta(days=30))
            if datetime.utcnow() - created_at > max_lifetime:
                return True
            
            # 检查空闲超时
            last_activity_str = session_data.get('last_activity_at')
            if last_activity_str:
                last_activity = datetime.fromisoformat(last_activity_str)
                max_idle = timedelta(seconds=current_app.config.get('SESSION_MAX_IDLE_TIME', 1800))
                if datetime.utcnow() - last_activity > max_idle:
                    return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"检查会话过期异常: {str(e)}")
            return True  # 出现异常时认为过期
    
    def _should_regenerate_session(self, session_data: Dict[str, Any]) -> bool:
        """
        检查是否应该重新生成session ID
        
        Args:
            session_data: 会话数据
            
        Returns:
            是否需要重新生成
        """
        try:
            last_activity_str = session_data.get('last_activity_at')
            if not last_activity_str:
                return True
            
            last_activity = datetime.fromisoformat(last_activity_str)
            regenerate_interval = current_app.config.get('SESSION_REGENERATE_AFTER', 3600)
            
            return (datetime.utcnow() - last_activity).total_seconds() > regenerate_interval
            
        except Exception as e:
            current_app.logger.error(f"检查会话重新生成异常: {str(e)}")
            return False
    
    def _regenerate_session_id(self, old_session_data: Dict[str, Any]):
        """
        重新生成session ID
        
        Args:
            old_session_data: 旧会话数据
        """
        try:
            # 生成新的session ID
            new_session_id = self._generate_session_id()
            
            # 清理旧会话
            old_session_id = old_session_data['session_id']
            self._cleanup_expired_session(old_session_id)
            
            # 创建新会话，保留用户数据
            new_session_data = {
                **old_session_data,
                'session_id': new_session_id,
                'created_at': datetime.utcnow().isoformat(),
                'last_activity_at': datetime.utcnow().isoformat()
            }
            
            # 更新session
            session['session_id'] = new_session_id
            self._save_session_data(new_session_id, new_session_data)
            
            current_app.logger.info(f"会话ID重新生成: {old_session_id} -> {new_session_id}")
            
        except Exception as e:
            current_app.logger.error(f"重新生成会话ID异常: {str(e)}")
    
    def _update_session_activity(self, session_id: str):
        """
        更新会话活动时间
        
        Args:
            session_id: 会话ID
        """
        try:
            session['last_activity_at'] = datetime.utcnow().isoformat()
        except Exception as e:
            current_app.logger.error(f"更新会话活动时间异常: {str(e)}")
    
    def _cleanup_expired_session(self, session_id: str):
        """
        清理过期会话
        
        Args:
            session_id: 会话ID
        """
        try:
            # 简化实现：清除Flask session
            # 实际项目中应该从数据库删除
            if session.get('session_id') == session_id:
                session.clear()
            
            current_app.logger.info(f"清理过期会话: {session_id}")
            
        except Exception as e:
            current_app.logger.error(f"清理过期会话异常: {str(e)}")
    
    def _register_cleanup_task(self, app):
        """
        注册定期清理任务
        需要外部调度器（如Celery）来定期执行
        
        Args:
            app: Flask应用实例
        """
        @app.cli.command('cleanup-sessions')
        def cleanup_sessions_command():
            """清理过期会话的CLI命令"""
            self.cleanup_expired_sessions()
    
    def cleanup_expired_sessions(self):
        """
        清理所有过期会话
        这个方法可以被外部调度器调用
        """
        try:
            current_app.logger.info("开始清理过期会话")
            
            # 实际项目中应该查询数据库中的所有会话
            # 并删除过期的会话记录
            
            # 这里简化处理，仅记录日志
            cleanup_count = 0  # 实际删除的会话数量
            
            current_app.logger.info(f"会话清理完成，清理了 {cleanup_count} 个过期会话")
            
        except Exception as e:
            current_app.logger.error(f"清理过期会话异常: {str(e)}")
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        获取当前会话信息
        
        Returns:
            会话信息字典
        """
        try:
            if 'session_id' not in session:
                return None
            
            session_id = session['session_id']
            return self._get_session_data(session_id)
            
        except Exception as e:
            current_app.logger.error(f"获取会话信息异常: {str(e)}")
            return None
    
    def invalidate_session(self):
        """
        使当前会话失效
        通常在用户登出时调用
        """
        try:
            if 'session_id' in session:
                session_id = session['session_id']
                self._cleanup_expired_session(session_id)
                current_app.logger.info(f"会话已失效: {session_id}")
            
        except Exception as e:
            current_app.logger.error(f"使会话失效异常: {str(e)}")
    
    def update_user_session(self, user_id: int, user_email: str):
        """
        更新会话的用户信息
        通常在用户登录时调用
        
        Args:
            user_id: 用户ID
            user_email: 用户邮箱
        """
        try:
            session['user_id'] = user_id
            session['user_email'] = user_email
            session['login_at'] = datetime.utcnow().isoformat()
            
            current_app.logger.info(f"更新用户会话: user_id={user_id}, session_id={session.get('session_id')}")
            
        except Exception as e:
            current_app.logger.error(f"更新用户会话异常: {str(e)}")


# 创建中间件实例
session_middleware = SessionMiddleware()


def init_session_middleware(app):
    """
    初始化会话中间件
    
    Args:
        app: Flask应用实例
    """
    session_middleware.init_app(app)
    
    # 记录初始化日志
    app.logger.info("会话中间件已初始化")


# 实用工具函数
def get_current_session() -> Optional[Dict[str, Any]]:
    """
    获取当前会话信息
    
    Returns:
        会话信息字典
    """
    return session_middleware.get_session_info()


def invalidate_current_session():
    """
    使当前会话失效
    """
    session_middleware.invalidate_session()


def update_session_user(user_id: int, user_email: str):
    """
    更新会话用户信息
    
    Args:
        user_id: 用户ID
        user_email: 用户邮箱
    """
    session_middleware.update_user_session(user_id, user_email)