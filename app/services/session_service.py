# -*- coding: utf-8 -*-
"""
会话管理服务
处理用户会话的创建、验证、清理等功能
"""

import secrets
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List

from flask import current_app, request
from sqlalchemy import and_, or_

from app.models import db
from app.models.user import UserSession, User


class SessionService:
    """会话管理服务类"""
    
    def __init__(self):
        """初始化会话服务"""
        self.default_session_timeout = timedelta(hours=24)  # 默认24小时过期
        self.max_sessions_per_user = 5  # 每个用户最多5个活跃会话
        self.token_length = 32  # 会话令牌长度
    
    def create_session(self, user_id: int, remember_me: bool = False) -> Dict[str, Any]:
        """
        创建新的用户会话
        
        Args:
            user_id: 用户ID
            remember_me: 是否为记住我登录（延长过期时间）
            
        Returns:
            Dict: 包含会话信息的字典
        """
        try:
            # 清理该用户的过期会话
            self.cleanup_expired_sessions(user_id)
            
            # 检查并限制用户的活跃会话数量
            self._limit_user_sessions(user_id)
            
            # 生成会话令牌
            session_token = self._generate_session_token()
            
            # 设置过期时间
            expires_at = self._calculate_expiry_time(remember_me)
            
            # 获取客户端信息
            client_info = self._get_client_info()
            
            # 创建会话记录
            session = UserSession(
                user_id=user_id,
                session_token=session_token,
                expires_at=expires_at,
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                is_active=True,
                remember_me=remember_me
            )
            
            db.session.add(session)
            db.session.commit()
            
            return {
                'success': True,
                'session_token': session_token,
                'expires_at': expires_at,
                'session_id': session.id,
                'message': '会话创建成功'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': '会话创建失败'
            }
    
    def validate_session(self, session_token: str) -> Dict[str, Any]:
        """
        验证会话令牌的有效性
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Dict: 验证结果
        """
        if not session_token:
            return {
                'valid': False,
                'error': 'missing_token',
                'message': '会话令牌缺失'
            }
        
        # 查询会话记录
        session = UserSession.query.filter_by(
            session_token=session_token,
            is_active=True
        ).first()
        
        if not session:
            return {
                'valid': False,
                'error': 'invalid_token',
                'message': '无效的会话令牌'
            }
        
        # 检查是否过期
        now = datetime.now(timezone.utc)
        if session.expires_at <= now:
            # 标记会话为过期
            session.is_active = False
            session.ended_at = now
            db.session.commit()
            
            return {
                'valid': False,
                'error': 'expired_token',
                'message': '会话已过期'
            }
        
        # 更新最后访问时间
        session.last_accessed_at = now
        
        # 可选：检查IP地址是否匹配（安全性考虑）
        current_ip = self._get_client_ip()
        if session.ip_address != current_ip:
            # 记录安全警告但不阻止访问
            current_app.logger.warning(f'用户 {session.user_id} 的会话从不同IP地址访问: '
                                     f'原始IP: {session.ip_address}, 当前IP: {current_ip}')
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'更新会话访问时间失败: {str(e)}')
        
        return {
            'valid': True,
            'user_id': session.user_id,
            'session_id': session.id,
            'expires_at': session.expires_at,
            'remember_me': session.remember_me
        }
    
    def end_session(self, session_token: str) -> Dict[str, Any]:
        """
        结束指定的会话
        
        Args:
            session_token: 会话令牌
            
        Returns:
            Dict: 操作结果
        """
        try:
            session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'error': 'session_not_found',
                    'message': '会话不存在'
                }
            
            # 标记会话为结束
            session.is_active = False
            session.ended_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return {
                'success': True,
                'message': '会话已结束'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': '结束会话失败'
            }
    
    def end_all_sessions(self, user_id: int, except_session_token: str = None) -> Dict[str, Any]:
        """
        结束用户的所有会话
        
        Args:
            user_id: 用户ID
            except_session_token: 要保留的会话令牌（通常是当前会话）
            
        Returns:
            Dict: 操作结果
        """
        try:
            # 构建查询条件
            query = UserSession.query.filter_by(user_id=user_id, is_active=True)
            
            if except_session_token:
                query = query.filter(UserSession.session_token != except_session_token)
            
            # 更新所有匹配的会话
            ended_count = query.update({
                'is_active': False,
                'ended_at': datetime.now(timezone.utc)
            })
            
            db.session.commit()
            
            return {
                'success': True,
                'ended_sessions_count': ended_count,
                'message': f'已结束 {ended_count} 个会话'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': '批量结束会话失败'
            }
    
    def get_active_sessions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        获取用户的活跃会话列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 活跃会话列表
        """
        sessions = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).order_by(UserSession.created_at.desc()).all()
        
        session_list = []
        for session in sessions:
            session_list.append({
                'id': session.id,
                'created_at': session.created_at,
                'last_accessed_at': session.last_accessed_at,
                'expires_at': session.expires_at,
                'ip_address': session.ip_address,
                'user_agent': session.user_agent,
                'remember_me': session.remember_me,
                'is_current': session.session_token == request.headers.get('Authorization', '').replace('Bearer ', '')
            })
        
        return session_list
    
    def cleanup_expired_sessions(self, user_id: int = None) -> Dict[str, Any]:
        """
        清理过期的会话
        
        Args:
            user_id: 可选，只清理指定用户的会话
            
        Returns:
            Dict: 清理结果
        """
        try:
            now = datetime.now(timezone.utc)
            
            # 构建查询条件
            query = UserSession.query.filter(
                and_(
                    UserSession.is_active == True,
                    UserSession.expires_at <= now
                )
            )
            
            if user_id:
                query = query.filter(UserSession.user_id == user_id)
            
            # 更新过期会话
            cleaned_count = query.update({
                'is_active': False,
                'ended_at': now
            })
            
            db.session.commit()
            
            return {
                'success': True,
                'cleaned_count': cleaned_count,
                'message': f'已清理 {cleaned_count} 个过期会话'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': '清理过期会话失败'
            }
    
    def extend_session(self, session_token: str, additional_time: timedelta = None) -> Dict[str, Any]:
        """
        延长会话过期时间
        
        Args:
            session_token: 会话令牌
            additional_time: 延长的时间，默认为原过期时间的一半
            
        Returns:
            Dict: 操作结果
        """
        try:
            session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not session:
                return {
                    'success': False,
                    'error': 'session_not_found',
                    'message': '会话不存在'
                }
            
            # 计算新的过期时间
            if additional_time is None:
                # 默认延长当前剩余时间的一半
                remaining_time = session.expires_at - datetime.now(timezone.utc)
                additional_time = remaining_time / 2
            
            new_expires_at = session.expires_at + additional_time
            session.expires_at = new_expires_at
            
            db.session.commit()
            
            return {
                'success': True,
                'new_expires_at': new_expires_at,
                'message': '会话时间已延长'
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': str(e),
                'message': '延长会话失败'
            }
    
    def get_session_stats(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户会话统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 会话统计信息
        """
        # 活跃会话数量
        active_sessions = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).count()
        
        # 历史会话总数
        total_sessions = UserSession.query.filter_by(user_id=user_id).count()
        
        # 最后登录时间
        last_session = UserSession.query.filter_by(
            user_id=user_id
        ).order_by(UserSession.created_at.desc()).first()
        
        last_login_at = last_session.created_at if last_session else None
        
        return {
            'active_sessions_count': active_sessions,
            'total_sessions_count': total_sessions,
            'last_login_at': last_login_at,
            'max_sessions_allowed': self.max_sessions_per_user
        }
    
    def _generate_session_token(self) -> str:
        """生成安全的会话令牌"""
        # 生成随机字节
        random_bytes = secrets.token_bytes(self.token_length)
        
        # 添加时间戳信息以增加唯一性
        timestamp = str(datetime.now(timezone.utc).timestamp())
        
        # 合并并哈希
        combined = random_bytes + timestamp.encode('utf-8')
        token_hash = hashlib.sha256(combined).hexdigest()
        
        return token_hash
    
    def _calculate_expiry_time(self, remember_me: bool) -> datetime:
        """计算会话过期时间"""
        if remember_me:
            # 记住我登录：30天
            return datetime.now(timezone.utc) + timedelta(days=30)
        else:
            # 普通登录：24小时
            return datetime.now(timezone.utc) + self.default_session_timeout
    
    def _get_client_info(self) -> Dict[str, str]:
        """获取客户端信息"""
        return {
            'ip_address': self._get_client_ip(),
            'user_agent': request.headers.get('User-Agent', '')[:500]  # 限制长度
        }
    
    def _get_client_ip(self) -> str:
        """获取客户端IP地址"""
        # 考虑代理服务器的情况
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    
    def _limit_user_sessions(self, user_id: int):
        """限制用户的活跃会话数量"""
        # 获取用户当前活跃会话
        active_sessions = UserSession.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            UserSession.expires_at > datetime.now(timezone.utc)
        ).order_by(UserSession.last_accessed_at.asc()).all()
        
        # 如果超过限制，结束最旧的会话
        if len(active_sessions) >= self.max_sessions_per_user:
            sessions_to_end = active_sessions[:len(active_sessions) - self.max_sessions_per_user + 1]
            
            for session in sessions_to_end:
                session.is_active = False
                session.ended_at = datetime.now(timezone.utc)
            
            db.session.commit()