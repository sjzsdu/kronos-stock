# -*- coding: utf-8 -*-
"""
认证装饰器
提供Bearer token认证和权限控制装饰器
"""

from functools import wraps
from flask import request, jsonify, current_app
from app.models.user import User, UserSession


def token_required(f):
    """
    Bearer token认证装饰器
    
    用于API端点的token认证，期望Authorization头中的Bearer token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # 从Authorization头获取token
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Bearer token格式: "Bearer <token>"
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'Authorization头格式无效',
                    'errors': {'authorization': ['Bearer token格式错误']}
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': '访问被拒绝，需要认证令牌',
                'errors': {'authorization': ['缺少Authorization头']}
            }), 401
        
        try:
            # 验证token
            session = UserSession.query.filter_by(token=token, is_active=True).first()
            
            if not session:
                return jsonify({
                    'success': False,
                    'message': '无效的认证令牌 (invalid)',
                    'errors': {'token': ['令牌无效或已过期']}
                }), 401
                
            # 检查会话是否过期
            if session.is_expired():
                # 标记会话为过期
                session.is_active = False
                from app.models import db
                db.session.commit()
                
                return jsonify({
                    'success': False,
                    'message': '认证令牌已过期 (expired)',
                    'errors': {'token': ['令牌已过期，请重新登录']}
                }), 401
                
            # 获取用户
            user = User.query.get(session.user_id)
            if not user or not user.is_active:
                return jsonify({
                    'success': False,
                    'message': '用户不存在或已被禁用',
                    'errors': {'user': ['用户账户无效']}
                }), 401
            
            # 将当前用户添加到请求上下文
            request.current_user = user
            request.current_session = session
            
        except Exception as e:
            current_app.logger.error(f"Token认证错误: {str(e)}")
            return jsonify({
                'success': False,
                'message': '认证验证失败',
                'errors': {'server': ['服务器内部错误']}
            }), 500
        
        # 将user_id作为第一个参数传递给被装饰的函数
        return f(user.id, *args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """
    管理员权限装饰器
    
    需要在token_required之后使用
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(request, 'current_user'):
            return jsonify({
                'success': False,
                'message': '需要先进行认证',
                'errors': {'authentication': ['未认证用户']}
            }), 401
        
        if request.current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': '权限不足',
                'errors': {'permission': ['需要管理员权限']}
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def get_current_user():
    """
    获取当前认证用户
    
    Returns:
        当前用户对象，如果未认证则返回None
    """
    return getattr(request, 'current_user', None)


def get_current_session():
    """
    获取当前用户会话
    
    Returns:
        当前会话对象，如果未认证则返回None
    """
    return getattr(request, 'current_session', None)