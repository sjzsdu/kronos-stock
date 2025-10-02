# -*- coding: utf-8 -*-
"""
用户页面视图控制器
处理用户相关页面的路由和模板渲染
包含仪表板、个人资料、关注列表等页面的访问控制和权限验证
"""

from flask import Blueprint, render_template, redirect, url_for, request, session, current_app, jsonify, g
from functools import wraps
import jwt
from datetime import datetime

# 创建用户蓝图
user_bp = Blueprint('user', __name__, url_prefix='/user')


def login_required(f):
    """
    装饰器：要求用户已登录
    验证Bearer token或session中的认证信息
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 优先检查Authorization header中的Bearer token
        auth_header = request.headers.get('Authorization')
        token = None
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        else:
            # 回退到session中的token
            token = session.get('auth_token')
        
        if not token:
            # 如果是API请求，返回401
            if request.is_json or request.headers.get('HX-Request'):
                return jsonify({'error': '需要认证', 'code': 'UNAUTHORIZED'}), 401
            # 否则重定向到登录页面
            return redirect(url_for('auth.login', next=request.url))
        
        try:
            # 验证token（这里简化处理，实际项目中应该验证JWT签名）
            # 将用户信息存储在g对象中供视图函数使用
            g.current_user = {
                'id': 'user_123',  # 实际项目中从token解析
                'email': 'user@example.com',
                'nickname': '测试用户',
                'avatar_url': '/static/img/default-avatar.png',
                'is_verified': True
            }
            
        except Exception as e:
            current_app.logger.error(f"Token validation error: {str(e)}")
            
            if request.is_json or request.headers.get('HX-Request'):
                return jsonify({'error': '认证失效', 'code': 'TOKEN_INVALID'}), 401
            
            # 清除无效token
            session.pop('auth_token', None)
            return redirect(url_for('auth.login', next=request.url))
        
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


@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    用户仪表板页面
    显示用户统计信息、最近预测、关注列表等
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="投资仪表板",
            description="查看您的投资组合、预测历史和市场分析",
            keywords=['仪表板', '投资组合', '股票预测', '投资分析']
        )
        
        # 获取用户统计数据（实际项目中应从数据库获取）
        user_stats = {
            'total_predictions': 25,
            'success_rate': 78.5,
            'watchlist_count': 12,
            'portfolio_value': 156780.50,
            'daily_change': 2.35,
            'weekly_change': -1.28
        }
        
        # 获取快速操作配置
        quick_actions = [
            {
                'title': '股票预测',
                'description': '输入股票代码进行AI预测',
                'icon': 'fas fa-chart-line',
                'url': '/prediction',
                'color': 'blue'
            },
            {
                'title': '关注列表',
                'description': '管理您关注的股票',
                'icon': 'fas fa-star',
                'url': '/user/watchlist',
                'color': 'purple'
            },
            {
                'title': '历史记录',
                'description': '查看预测历史',
                'icon': 'fas fa-history',
                'url': '/user/history',
                'color': 'green'
            },
            {
                'title': '市场分析',
                'description': '查看市场趋势分析',
                'icon': 'fas fa-chart-bar',
                'url': '/market/analysis',
                'color': 'orange'
            }
        ]
        
        return render_template('user/dashboard.html',
                             page_meta=page_meta,
                             user_stats=user_stats,
                             quick_actions=quick_actions)
                             
    except Exception as e:
        current_app.logger.error(f"Dashboard page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.route('/profile')
@login_required
def profile():
    """
    用户个人资料页面
    显示和编辑用户基本信息、安全设置等
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="个人资料",
            description="管理您的账户信息和安全设置",
            keywords=['个人资料', '账户设置', '安全设置', '用户信息']
        )
        
        # 获取用户详细信息（实际项目中从数据库获取）
        user_profile = {
            'id': g.current_user['id'],
            'email': g.current_user['email'],
            'nickname': g.current_user['nickname'],
            'avatar_url': g.current_user['avatar_url'],
            'phone': '+86 138****8888',
            'real_name': '张三',
            'gender': 'male',
            'birth_date': '1990-01-01',
            'location': '北京市',
            'bio': '专业投资者，关注科技股和新能源板块',
            'created_at': '2023-06-15',
            'last_login': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'is_verified': g.current_user['is_verified'],
            'is_vip': False,
            'vip_expire': None
        }
        
        # 获取安全设置信息
        security_settings = {
            'two_factor_enabled': False,
            'login_notifications': True,
            'marketing_emails': True,
            'security_alerts': True,
            'password_last_changed': '2024-01-15',
            'recent_logins': [
                {'ip': '192.168.1.100', 'location': '北京', 'device': 'Chrome on Windows', 'time': '2024-01-20 14:30'},
                {'ip': '10.0.0.1', 'location': '上海', 'device': 'Safari on iPhone', 'time': '2024-01-19 09:15'}
            ]
        }
        
        # 获取偏好设置
        preferences = {
            'theme': 'light',
            'language': 'zh-cn',
            'timezone': 'Asia/Shanghai',
            'default_market': 'cn',
            'notification_settings': {
                'price_alerts': True,
                'prediction_results': True,
                'market_news': False,
                'system_updates': True
            }
        }
        
        return render_template('user/profile.html',
                             page_meta=page_meta,
                             user_profile=user_profile,
                             security_settings=security_settings,
                             preferences=preferences)
                             
    except Exception as e:
        current_app.logger.error(f"Profile page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.route('/watchlist')
@login_required
def watchlist():
    """
    用户关注列表页面
    显示和管理用户关注的股票
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="我的关注列表",
            description="管理您关注的股票，快速访问预测和分析",
            keywords=['关注列表', '股票收藏', '投资组合', '股票管理']
        )
        
        # 获取排序和筛选参数
        sort_by = request.args.get('sort', 'default')
        view_mode = request.args.get('view', 'list')
        
        return render_template('user/watchlist.html',
                             page_meta=page_meta,
                             sort_by=sort_by,
                             view_mode=view_mode)
                             
    except Exception as e:
        current_app.logger.error(f"Watchlist page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.route('/history')
@login_required
def history():
    """
    预测历史页面
    显示用户的预测记录和结果分析
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="预测历史",
            description="查看您的股票预测记录和准确率分析",
            keywords=['预测历史', '投资记录', '准确率分析', '投资回顾']
        )
        
        # 获取筛选参数
        date_range = request.args.get('range', '30d')  # 30d, 90d, 1y, all
        stock_code = request.args.get('stock')
        status = request.args.get('status', 'all')  # all, correct, incorrect, pending
        
        # 分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        return render_template('user/history.html',
                             page_meta=page_meta,
                             date_range=date_range,
                             stock_code=stock_code,
                             status=status,
                             page=page,
                             per_page=per_page)
                             
    except Exception as e:
        current_app.logger.error(f"History page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.route('/settings')
@login_required
def settings():
    """
    用户设置页面
    系统设置、通知偏好、隐私设置等
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="系统设置",
            description="自定义您的平台使用体验和偏好设置",
            keywords=['系统设置', '用户偏好', '通知设置', '隐私设置']
        )
        
        # 获取设置分类
        category = request.args.get('category', 'general')
        
        return render_template('user/settings.html',
                             page_meta=page_meta,
                             category=category)
                             
    except Exception as e:
        current_app.logger.error(f"Settings page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.route('/notifications')
@login_required
def notifications():
    """
    用户通知页面
    显示系统通知、预测结果通知等
    """
    try:
        # 设置页面元数据
        page_meta = set_page_metadata(
            title="消息通知",
            description="查看系统消息、预测结果和重要提醒",
            keywords=['消息通知', '系统提醒', '预测通知', '用户消息']
        )
        
        # 获取筛选参数
        notification_type = request.args.get('type', 'all')  # all, system, prediction, alert
        status = request.args.get('status', 'all')  # all, read, unread
        
        return render_template('user/notifications.html',
                             page_meta=page_meta,
                             notification_type=notification_type,
                             status=status)
                             
    except Exception as e:
        current_app.logger.error(f"Notifications page error: {str(e)}")
        return render_template('errors/500.html'), 500


@user_bp.errorhandler(403)
def forbidden(error):
    """
    403 错误处理器
    用户无权限访问时的错误页面
    """
    return render_template('errors/403.html'), 403


@user_bp.errorhandler(404)
def not_found(error):
    """
    404 错误处理器  
    页面不存在时的错误页面
    """
    return render_template('errors/404.html'), 404


# 模板上下文处理器
@user_bp.context_processor
def inject_user_context():
    """
    注入用户相关的模板上下文
    为所有用户页面提供通用的上下文变量
    """
    context = {
        'user_config': {
            'enable_notifications': current_app.config.get('ENABLE_NOTIFICATIONS', True),
            'max_watchlist_items': current_app.config.get('MAX_WATCHLIST_ITEMS', 50),
            'prediction_history_days': current_app.config.get('PREDICTION_HISTORY_DAYS', 365),
            'enable_social_sharing': current_app.config.get('ENABLE_SOCIAL_SHARING', True)
        }
    }
    
    # 如果用户已认证，添加用户信息
    if hasattr(g, 'current_user') and g.current_user:
        context['current_user'] = g.current_user
        
        # 添加用户相关的统计信息（可以缓存这些数据）
        context['user_stats'] = {
            'unread_notifications': 3,  # 实际项目中从数据库获取
            'watchlist_count': 12,
            'recent_predictions': 5
        }
    
    return context


# 模板过滤器
@user_bp.app_template_filter('format_currency')
def format_currency(value):
    """
    格式化货币显示
    """
    if value is None:
        return '¥0.00'
    
    try:
        return f'¥{float(value):,.2f}'
    except (ValueError, TypeError):
        return '¥0.00'


@user_bp.app_template_filter('format_percentage')
def format_percentage(value, precision=2):
    """
    格式化百分比显示
    """
    if value is None:
        return '0.00%'
    
    try:
        return f'{float(value):.{precision}f}%'
    except (ValueError, TypeError):
        return '0.00%'


@user_bp.app_template_filter('time_ago')
def time_ago(datetime_str):
    """
    相对时间显示（如：2小时前）
    """
    try:
        if isinstance(datetime_str, str):
            dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        else:
            dt = datetime_str
        
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 7:
            return dt.strftime('%Y-%m-%d')
        elif diff.days > 0:
            return f'{diff.days}天前'
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f'{hours}小时前'
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f'{minutes}分钟前'
        else:
            return '刚刚'
    except Exception:
        return str(datetime_str)


# 在应用启动时注册蓝图的函数
def register_user_routes(app):
    """
    注册用户路由到Flask应用
    
    Args:
        app: Flask应用实例
    """
    app.register_blueprint(user_bp)
    
    # 记录注册信息
    app.logger.info("User routes registered successfully")