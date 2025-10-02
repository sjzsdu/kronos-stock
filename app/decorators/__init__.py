# -*- coding: utf-8 -*-
"""
认证装饰器模块初始化文件
"""

from .auth_decorators import (
    token_required,
    admin_required,
    get_current_user,
    get_current_session
)

# 从优化认证中间件导入登录相关装饰器
from app.middleware.optimized_auth_middleware import (
    login_required,
    current_user_required
)

__all__ = [
    'token_required',
    'admin_required', 
    'login_required',
    'current_user_required',
    'get_current_user',
    'get_current_session'
]