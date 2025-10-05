# -*- coding: utf-8 -*-
"""
用户管理视图控制器
处理用户档案、设置、关注列表等页面和HTMX交互
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.utils.validators import sanitize_input


user_views = Blueprint('user_views', __name__, url_prefix='/user')

# 路由修复：已添加settings.html模板


@user_views.route('/dashboard')
@login_required
def dashboard():
    """用户仪表盘页面"""
    return render_template('user/dashboard.html')


@user_views.route('/profile')
@login_required
def profile_page():
    """用户档案页面"""
    profile = UserService.get_user_profile(current_user.id)
    stats = UserService.get_user_statistics(current_user.id)
    
    return render_template('user/profile.html', 
                         user=current_user, profile=profile, stats=stats)


@user_views.route('/settings')
@login_required
def settings_page():
    """用户设置页面"""
    profile = UserService.get_user_profile(current_user.id)
    
    return render_template('user/settings.html', 
                         user=current_user, profile=profile)


@user_views.route('/watchlist')
@login_required
def watchlist_page():
    """关注股票列表页面"""
    watchlist = UserService.get_user_watchlist(current_user.id)
    
    return render_template('user/watchlist.html', 
                         watchlist=watchlist)


@user_views.route('/predictions')
@login_required
def predictions_page():
    """预测记录页面"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    predictions = UserService.get_user_predictions(
        current_user.id, 
        limit=per_page, 
        offset=(page - 1) * per_page
    )
    
    return render_template('user/predictions.html', 
                         predictions=predictions, page=page)


# HTMX 交互端点

@user_views.route('/htmx/profile', methods=['POST'])
@login_required
def htmx_update_profile():
    """HTMX更新用户档案"""
    try:
        # 获取表单数据
        profile_data = {
            'full_name': sanitize_input(request.form.get('full_name', '')),
            'nickname': sanitize_input(request.form.get('nickname', '')),
            'phone': sanitize_input(request.form.get('phone', '')),
            'bio': sanitize_input(request.form.get('bio', ''), 500),
            'location': sanitize_input(request.form.get('location', '')),
            'gender': request.form.get('gender', ''),
            'investment_experience': request.form.get('investment_experience', ''),
            'risk_preference': request.form.get('risk_preference', '')
        }
        
        # 清理空值
        profile_data = {k: v for k, v in profile_data.items() if v}
        
        success, message = UserService.update_user_profile(current_user.id, profile_data)
        
        if success:
            return render_template('components/form_success.html', message=message)
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='更新失败，请稍后重试'), 500


@user_views.route('/htmx/change-password', methods=['POST'])
@login_required
def htmx_change_password():
    """HTMX修改密码"""
    try:
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([current_password, new_password, confirm_password]):
            return render_template('components/form_error.html', 
                                 message='所有字段都是必填项'), 422
        
        if new_password != confirm_password:
            return render_template('components/form_error.html', 
                                 message='两次输入的新密码不一致'), 422
        
        success, message = AuthService.change_password(
            current_user, current_password, new_password
        )
        
        if success:
            return render_template('components/form_success.html', message=message)
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='修改密码失败，请稍后重试'), 500


@user_views.route('/htmx/watchlist/add', methods=['POST'])
@login_required
def htmx_add_watchlist():
    """HTMX添加关注股票"""
    try:
        stock_code = sanitize_input(request.form.get('stock_code', ''))
        stock_name = sanitize_input(request.form.get('stock_name', ''))
        notes = sanitize_input(request.form.get('notes', ''), 500)
        
        if not stock_code:
            return render_template('components/form_error.html', 
                                 message='股票代码是必填项'), 422
        
        success, message = UserService.add_to_watchlist(
            current_user.id, stock_code, stock_name, notes
        )
        
        if success:
            # 返回更新后的关注列表
            watchlist = UserService.get_user_watchlist(current_user.id)
            return render_template('components/watchlist_items.html', 
                                 watchlist=watchlist)
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='添加失败，请稍后重试'), 500


@user_views.route('/htmx/watchlist/remove/<stock_code>', methods=['DELETE'])
@login_required
def htmx_remove_watchlist(stock_code):
    """HTMX移除关注股票"""
    try:
        stock_code = sanitize_input(stock_code)
        
        success, message = UserService.remove_from_watchlist(current_user.id, stock_code)
        
        if success:
            # 返回更新后的关注列表
            watchlist = UserService.get_user_watchlist(current_user.id)
            return render_template('components/watchlist_items.html', 
                                 watchlist=watchlist)
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='移除失败，请稍后重试'), 500


@user_views.route('/htmx/watchlist/reorder', methods=['POST'])
@login_required
def htmx_reorder_watchlist():
    """HTMX重新排序关注列表"""
    try:
        # 从表单获取排序后的股票代码
        stock_codes = request.form.getlist('stock_codes')
        clean_codes = [sanitize_input(code) for code in stock_codes if code]
        
        success, message = UserService.update_watchlist_order(current_user.id, clean_codes)
        
        if success:
            return render_template('components/form_success.html', message=message)
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='排序失败，请稍后重试'), 500


@user_views.route('/htmx/predictions')
@login_required
def htmx_load_predictions():
    """HTMX加载预测记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        predictions = UserService.get_user_predictions(
            current_user.id, 
            limit=per_page, 
            offset=(page - 1) * per_page
        )
        
        return render_template('components/prediction_items.html', 
                             predictions=predictions, current_page=page)
        
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='加载预测记录失败'), 500


@user_views.route('/htmx/statistics')
@login_required
def htmx_load_statistics():
    """HTMX加载用户统计信息"""
    try:
        stats = UserService.get_user_statistics(current_user.id)
        
        return render_template('components/user_statistics.html', stats=stats)
        
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='加载统计信息失败'), 500


@user_views.route('/htmx/preferences', methods=['POST'])
@login_required
def htmx_update_preferences():
    """HTMX更新用户偏好设置"""
    try:
        # 获取偏好设置
        preferences = {
            'theme': request.form.get('theme', 'light'),
            'language': request.form.get('language', 'zh-cn'),
            'auto_refresh': request.form.get('auto_refresh') == 'on',
            'default_model': request.form.get('default_model', 'kronos-mini'),
            'chart_style': request.form.get('chart_style', 'candlestick')
        }
        
        # 获取通知设置
        notification_settings = {
            'email_notifications': request.form.get('email_notifications') == 'on',
            'prediction_alerts': request.form.get('prediction_alerts') == 'on',
            'market_updates': request.form.get('market_updates') == 'on',
            'weekly_summary': request.form.get('weekly_summary') == 'on'
        }
        
        profile_data = {
            'preferences': preferences,
            'notification_settings': notification_settings
        }
        
        success, message = UserService.update_user_profile(current_user.id, profile_data)
        
        if success:
            return render_template('components/form_success.html', message='设置已保存')
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='保存设置失败，请稍后重试'), 500


@user_views.route('/htmx/delete-account', methods=['POST'])
@login_required
def htmx_delete_account():
    """HTMX删除账户确认"""
    try:
        password = request.form.get('password', '')
        
        if not password:
            return render_template('components/form_error.html', 
                                 message='请输入当前密码确认删除'), 422
        
        success, message = UserService.delete_user_account(current_user.id, password)
        
        if success:
            return render_template('components/account_deleted.html', 
                                 message=message, home_url=url_for('main.index'))
        else:
            return render_template('components/form_error.html', message=message), 422
            
    except Exception as e:
        return render_template('components/form_error.html', 
                             message='删除账户失败，请稍后重试'), 500