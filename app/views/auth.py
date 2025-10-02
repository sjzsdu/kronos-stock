# -*- coding: utf-8 -*-
"""
认证页面视图控制器
处理用户认证相关页面的路由和模板渲染
包含登录、注册、密码重置页面的访问控制
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, current_app
from functools import wraps

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def guest_required(f):
    """
    装饰器：要求用户未登录
    如果用户已登录，重定向到仪表板
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中的token或从请求头获取token
        auth_token = session.get('auth_token') or request.headers.get('Authorization')
        
        if auth_token:
            # 用户已登录，重定向到仪表板
            return redirect(url_for('user.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def set_page_metadata(title, description=None, keywords=None):
    """
    设置页面元数据
    用于SEO和页面标识
    """
    return {
        'title': title,
        'description': description or f"{title} - Kronos 智能投资平台",
        'keywords': keywords or ['Kronos', '智能投资', '股票预测', 'AI投资', '金融科技']
    }


@auth_bp.route('/login')
@guest_required
def login():
    """
    用户登录页面
    显示登录表单，支持邮箱/用户名登录
    """
    try:
        # 获取重定向参数
        next_url = request.args.get('next')
        
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="用户登录",
            description="登录 Kronos 智能投资平台，开启AI驱动的投资之旅",
            keywords=['登录', '用户认证', 'Kronos', '投资平台']
        )
        
        # 检查是否显示注册成功提示
        show_register_success = request.args.get('registered') == '1'
        
        return render_template('auth/login.html',
                             page_meta=page_meta,
                             next_url=next_url,
                             show_register_success=show_register_success)
                             
    except Exception as e:
        current_app.logger.error(f"Login page error: {str(e)}")
        return render_template('errors/500.html'), 500


@auth_bp.route('/register')
@guest_required
def register():
    """
    用户注册页面
    显示注册表单，包含实时验证
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="用户注册",
            description="注册 Kronos 智能投资平台账户，体验专业的AI股票预测服务",
            keywords=['注册', '开户', 'Kronos', '投资平台', 'AI预测']
        )
        
        # 获取邀请码（如果有）
        invite_code = request.args.get('invite')
        
        return render_template('auth/register.html',
                             page_meta=page_meta,
                             invite_code=invite_code)
                             
    except Exception as e:
        current_app.logger.error(f"Register page error: {str(e)}")
        return render_template('errors/500.html'), 500


@auth_bp.route('/reset-password')
@guest_required
def reset_password():
    """
    密码重置页面
    支持通过邮箱重置密码的多步骤流程
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="重置密码",
            description="忘记密码？通过邮箱验证重置您的 Kronos 账户密码",
            keywords=['密码重置', '找回密码', 'Kronos', '账户安全']
        )
        
        # 获取重置令牌（用于验证重置链接）
        reset_token = request.args.get('token')
        
        # 获取步骤参数（用于指示当前处于哪个步骤）
        step = request.args.get('step', '1')
        
        return render_template('auth/reset_password.html',
                             page_meta=page_meta,
                             reset_token=reset_token,
                             current_step=step)
                             
    except Exception as e:
        current_app.logger.error(f"Reset password page error: {str(e)}")
        return render_template('errors/500.html'), 500


@auth_bp.route('/logout')
def logout():
    """
    用户登出
    清除session并重定向到登录页面
    """
    try:
        # 清除session中的认证信息
        session.pop('auth_token', None)
        session.pop('user_id', None)
        session.pop('user_email', None)
        
        # 记录登出日志
        current_app.logger.info("User logged out successfully")
        
        # 重定向到登录页面，带上登出成功提示
        return redirect(url_for('auth.login', logged_out='1'))
        
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email')
@guest_required
def verify_email():
    """
    邮箱验证页面
    用于新用户邮箱验证或邮箱地址变更验证
    """
    try:
        # 获取验证令牌
        verify_token = request.args.get('token')
        
        if not verify_token:
            # 如果没有令牌，显示验证指引页面
            page_meta = set_page_metadata(
                title="邮箱验证",
                description="验证您的邮箱地址以激活 Kronos 账户",
                keywords=['邮箱验证', '账户激活', 'Kronos']
            )
            
            return render_template('auth/verify_email.html',
                                 page_meta=page_meta,
                                 verify_token=None)
        else:
            # 有令牌，进行验证处理
            # 这里应该调用API验证令牌
            page_meta = set_page_metadata(
                title="正在验证邮箱",
                description="正在验证您的邮箱地址...",
                keywords=['邮箱验证', '账户激活']
            )
            
            return render_template('auth/verify_email.html',
                                 page_meta=page_meta,
                                 verify_token=verify_token)
                                 
    except Exception as e:
        current_app.logger.error(f"Email verification page error: {str(e)}")
        return render_template('errors/500.html'), 500


@auth_bp.errorhandler(403)
def forbidden(error):
    """
    403 错误处理器
    用户无权限访问时的错误页面
    """
    return render_template('errors/403.html'), 403


@auth_bp.errorhandler(404)
def not_found(error):
    """
    404 错误处理器  
    页面不存在时的错误页面
    """
    return render_template('errors/404.html'), 404


# 模板上下文处理器
@auth_bp.context_processor
def inject_auth_context():
    """
    注入认证相关的模板上下文
    为所有认证页面提供通用的上下文变量
    """
    return {
        'auth_config': {
            'enable_registration': current_app.config.get('ENABLE_REGISTRATION', True),
            'enable_social_login': current_app.config.get('ENABLE_SOCIAL_LOGIN', False),
            'require_email_verification': current_app.config.get('REQUIRE_EMAIL_VERIFICATION', True),
            'password_min_length': current_app.config.get('PASSWORD_MIN_LENGTH', 8),
            'session_timeout_minutes': current_app.config.get('SESSION_TIMEOUT_MINUTES', 30)
        },
        'social_providers': {
            'google': current_app.config.get('GOOGLE_OAUTH_ENABLED', False),
            'github': current_app.config.get('GITHUB_OAUTH_ENABLED', False),
            'wechat': current_app.config.get('WECHAT_OAUTH_ENABLED', False)
        }
    }


# 在应用启动时注册蓝图的函数
def register_auth_routes(app):
    """
    注册认证路由到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(auth_bp)
    
    # 记录注册信息
    app.logger.info("Auth routes registered successfully")