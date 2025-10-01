# -*- coding: utf-8 -*-
"""
用户认证服务
处理用户登录、注册、会话管理等认证相关功能
"""

import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Dict, Any

import bcrypt
import jwt
from flask import current_app, request
from flask_login import login_user, logout_user

from app.models import db
from app.models.user import User, UserProfile, UserSession
from app.utils.validators import validate_email, validate_password


class AuthService:
    """用户认证服务类"""
    
    @staticmethod
    def register_user(email: str, password: str, full_name: str) -> Tuple[bool, str, Optional[User]]:
        """
        用户注册
        
        Args:
            email: 用户邮箱
            password: 用户密码
            full_name: 用户全名
            
        Returns:
            (成功标志, 消息, 用户对象)
        """
        try:
            # 验证邮箱格式
            if not validate_email(email):
                return False, "邮箱格式无效", None
            
            # 验证密码强度
            is_valid, password_msg = validate_password(password)
            if not is_valid:
                return False, password_msg, None
            
            # 检查邮箱是否已存在
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return False, "该邮箱已被注册", None
            
            # 创建新用户
            user = User(
                email=email.lower().strip(),
                full_name=full_name.strip(),
                role='user'
            )
            user.set_password(password)
            
            # 保存用户
            db.session.add(user)
            db.session.flush()  # 获取用户ID
            
            # 创建用户档案
            profile = UserProfile(user_id=user.id)
            db.session.add(profile)
            
            db.session.commit()
            
            return True, "注册成功", user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"用户注册失败: {str(e)}")
            return False, "注册失败，请稍后重试", None
    
    @staticmethod
    def authenticate_user(email: str, password: str, remember: bool = False) -> Tuple[bool, str, Optional[User]]:
        """
        用户登录认证
        
        Args:
            email: 用户邮箱
            password: 用户密码  
            remember: 是否记住登录状态
            
        Returns:
            (成功标志, 消息, 用户对象)
        """
        try:
            # 查找用户
            user = User.query.filter_by(email=email.lower().strip()).first()
            
            if not user:
                return False, "用户不存在", None
            
            # 检查用户状态
            if not user.is_active:
                return False, "账户已被禁用", None
            
            # 验证密码
            if not user.check_password(password):
                return False, "密码错误", None
            
            # 更新最后登录时间
            user.last_login = datetime.now(timezone.utc)
            
            # 使用 Flask-Login 登录用户
            login_user(user, remember=remember)
            
            # 创建会话记录
            AuthService._create_user_session(user)
            
            db.session.commit()
            
            return True, "登录成功", user
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"用户登录失败: {str(e)}")
            return False, "登录失败，请稍后重试", None
    
    @staticmethod
    def logout_user_session(user: User) -> bool:
        """
        用户登出
        
        Args:
            user: 当前用户对象
            
        Returns:
            是否成功登出
        """
        try:
            # 清理当前会话
            session_token = request.cookies.get('session_token')
            if session_token:
                session = UserSession.query.filter_by(
                    user_id=user.id,
                    session_token=session_token
                ).first()
                if session:
                    db.session.delete(session)
            
            # Flask-Login 登出
            logout_user()
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"用户登出失败: {str(e)}")
            return False
    
    @staticmethod
    def change_password(user: User, current_password: str, new_password: str) -> Tuple[bool, str]:
        """
        修改用户密码
        
        Args:
            user: 用户对象
            current_password: 当前密码
            new_password: 新密码
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 验证当前密码
            if not user.check_password(current_password):
                return False, "当前密码错误"
            
            # 验证新密码强度
            is_valid, password_msg = validate_password(new_password)
            if not is_valid:
                return False, password_msg
            
            # 设置新密码
            user.set_password(new_password)
            db.session.commit()
            
            return True, "密码修改成功"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"密码修改失败: {str(e)}")
            return False, "密码修改失败，请稍后重试"
    
    @staticmethod
    def generate_reset_token(email: str) -> Tuple[bool, str, Optional[str]]:
        """
        生成密码重置令牌
        
        Args:
            email: 用户邮箱
            
        Returns:
            (成功标志, 消息, 重置令牌)
        """
        try:
            user = User.query.filter_by(email=email.lower().strip()).first()
            if not user:
                return False, "用户不存在", None
            
            # 生成JWT令牌
            payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.utcnow() + timedelta(hours=1),  # 1小时过期
                'type': 'password_reset'
            }
            
            token = jwt.encode(
                payload, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithm='HS256'
            )
            
            return True, "重置令牌生成成功", token
            
        except Exception as e:
            current_app.logger.error(f"生成重置令牌失败: {str(e)}")
            return False, "生成重置令牌失败", None
    
    @staticmethod
    def reset_password_with_token(token: str, new_password: str) -> Tuple[bool, str]:
        """
        使用令牌重置密码
        
        Args:
            token: 重置令牌
            new_password: 新密码
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 验证令牌
            payload = jwt.decode(
                token, 
                current_app.config['JWT_SECRET_KEY'], 
                algorithms=['HS256']
            )
            
            if payload.get('type') != 'password_reset':
                return False, "无效的重置令牌"
            
            # 查找用户
            user = User.query.get(payload['user_id'])
            if not user or user.email != payload['email']:
                return False, "用户信息不匹配"
            
            # 验证新密码
            is_valid, password_msg = validate_password(new_password)
            if not is_valid:
                return False, password_msg
            
            # 重置密码
            user.set_password(new_password)
            
            # 清除用户的所有会话
            UserSession.query.filter_by(user_id=user.id).delete()
            
            db.session.commit()
            
            return True, "密码重置成功"
            
        except jwt.ExpiredSignatureError:
            return False, "重置链接已过期"
        except jwt.InvalidTokenError:
            return False, "无效的重置令牌"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"密码重置失败: {str(e)}")
            return False, "密码重置失败，请稍后重试"
    
    @staticmethod
    def _create_user_session(user: User) -> Optional[UserSession]:
        """
        创建用户会话记录
        
        Args:
            user: 用户对象
            
        Returns:
            会话对象或None
        """
        try:
            # 生成会话令牌
            session_token = secrets.token_urlsafe(32)
            session_id = hashlib.sha256(session_token.encode()).hexdigest()
            
            # 创建会话
            expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=current_app.config.get('PERMANENT_SESSION_LIFETIME', 86400)
            )
            
            session = UserSession(
                id=session_id,
                user_id=user.id,
                session_token=session_token,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', ''),
                expires_at=expires_at
            )
            
            db.session.add(session)
            
            # 清理过期会话
            AuthService._cleanup_expired_sessions(user.id)
            
            return session
            
        except Exception as e:
            current_app.logger.error(f"创建用户会话失败: {str(e)}")
            return None
    
    @staticmethod
    def _cleanup_expired_sessions(user_id: Optional[int] = None):
        """
        清理过期会话
        
        Args:
            user_id: 用户ID，如果为None则清理所有过期会话
        """
        try:
            query = UserSession.query.filter(
                UserSession.expires_at < datetime.now(timezone.utc)
            )
            
            if user_id:
                query = query.filter(UserSession.user_id == user_id)
            
            expired_count = query.delete()
            
            if expired_count > 0:
                current_app.logger.info(f"清理了 {expired_count} 个过期会话")
                
        except Exception as e:
            current_app.logger.error(f"清理过期会话失败: {str(e)}")
    
    @staticmethod
    def verify_session_token(token: str) -> Optional[User]:
        """
        验证会话令牌
        
        Args:
            token: 会话令牌
            
        Returns:
            用户对象或None
        """
        try:
            session = UserSession.query.filter_by(session_token=token).first()
            
            if not session or session.is_expired():
                return None
            
            # 更新最后活动时间
            session.last_activity = datetime.now(timezone.utc)
            db.session.commit()
            
            return session.user
            
        except Exception as e:
            current_app.logger.error(f"验证会话令牌失败: {str(e)}")
            return None