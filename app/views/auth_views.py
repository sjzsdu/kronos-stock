# -*- coding: utf-8 -*-
"""
用户认证视图控制器
处理用户登录、注册页面和HTMX交互
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user, logout_user

from app.services.auth_service import AuthService
from app.utils.validators import sanitize_input


auth_views = Blueprint('auth_views', __name__, url_prefix='/auth')


@auth_views.route('/login')
def login_page():
    """登录页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    return render_template('auth/login.html')


@auth_views.route('/register')
def register_page():
    """注册页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    return render_template('auth/register.html')


@auth_views.route('/forgot-password')
def forgot_password_page():
    """忘记密码页面"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    return render_template('auth/forgot_password.html')


@auth_views.route('/reset-password')
def reset_password_page():
    """重置密码页面"""
    token = request.args.get('token')
    if not token:
        flash('无效的重置链接', 'error')
        return redirect(url_for('auth_views.forgot_password_page'))
    
    return render_template('auth/reset_password.html', token=token)


# HTMX 交互端点

@auth_views.route('/htmx/login', methods=['POST'])
def htmx_login():
    """HTMX登录处理"""
    try:
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        if not all([email, password]):
            return render_template('components/form_error.html', 
                                 message='邮箱和密码都是必填项'), 422
        
        success, message, user = AuthService.authenticate_user(email, password, remember)
        
        if success:
            # 返回成功消息和重定向指令
            return render_template('components/login_success.html', 
                                 user=user, redirect_url=url_for('main.index'))
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='登录失败，请稍后重试'), 500


@auth_views.route('/htmx/register', methods=['POST'])
def htmx_register():
    """HTMX注册处理"""
    try:
        email = sanitize_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = sanitize_input(request.form.get('full_name', ''))
        
        # 基本验证
        if not all([email, password, confirm_password, full_name]):
            return render_template('components/form_error.html', 
                                 message='所有字段都是必填项'), 422
        
        if password != confirm_password:
            return render_template('components/form_error.html', 
                                 message='两次输入的密码不一致'), 422
        
        success, message, user = AuthService.register_user(email, password, full_name)
        
        if success:
            # 返回成功消息
            return render_template('components/register_success.html', 
                                 message=message, login_url=url_for('auth_views.login_page'))
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='注册失败，请稍后重试'), 500


@auth_views.route('/htmx/forgot-password', methods=['POST'])
def htmx_forgot_password():
    """HTMX忘记密码处理"""
    try:
        email = sanitize_input(request.form.get('email', ''))
        
        if not email:
            return render_template('components/form_error.html', 
                                 message='请输入邮箱地址'), 422
        
        success, message, token = AuthService.generate_reset_token(email)
        
        if success:
            # TODO: 发送邮件，这里暂时显示成功消息
            return render_template('components/forgot_password_success.html', 
                                 message='重置链接已发送到您的邮箱')
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='处理失败，请稍后重试'), 500


@auth_views.route('/htmx/reset-password', methods=['POST'])
def htmx_reset_password():
    """HTMX重置密码处理"""
    try:
        token = request.form.get('token', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([token, password, confirm_password]):
            return render_template('components/form_error.html', 
                                 message='所有字段都是必填项'), 422
        
        if password != confirm_password:
            return render_template('components/form_error.html', 
                                 message='两次输入的密码不一致'), 422
        
        success, message = AuthService.reset_password_with_token(token, password)
        
        if success:
            return render_template('components/reset_password_success.html', 
                                 message=message, login_url=url_for('auth_views.login_page'))
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='重置失败，请稍后重试'), 500


@auth_views.route('/logout')
@login_required
def logout():
    """用户登出"""
    try:
        AuthService.logout_user_session(current_user)
        flash('已成功登出', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        flash('登出失败，请稍后重试', 'error')
        return redirect(url_for('main.index'))


# 用户状态检查端点（用于前端状态同步）

@auth_views.route('/htmx/check-auth')
def htmx_check_auth():
    """检查用户认证状态（HTMX）"""
    if current_user.is_authenticated:
        return render_template('components/user_status.html', 
                             user=current_user, authenticated=True)
    else:
        return render_template('components/user_status.html', 
                             authenticated=False)


@auth_views.route('/htmx/user-menu')
@login_required
def htmx_user_menu():
    """用户菜单组件（HTMX）"""
    return render_template('components/user_menu.html', user=current_user)