"""
通知列表HTML视图端点
提供HTMX通知组件的动态HTML渲染服务
"""
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from app.services.ui_service import UIService
from app.services.component_render_service import ComponentRenderService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
from datetime import datetime, timedelta
import json

# 创建视图蓝图
ui_notifications_views_bp = Blueprint('ui_notifications_views', __name__, url_prefix='/views/ui-notifications')

# 初始化服务
ui_service = UIService()
render_service = ComponentRenderService()
performance_service = PerformanceService()

# 模拟通知数据存储（实际项目中应该使用数据库）
notifications_store = []
next_notification_id = 1


@ui_notifications_views_bp.route('/list')
def notifications_list():
    """通知列表页面"""
    try:
        start_time = datetime.now()
        
        # 获取查询参数
        notification_type = request.args.get('type', 'all')
        status = request.args.get('status', 'all')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # 过滤通知
        filtered_notifications = notifications_store.copy()
        
        if notification_type != 'all':
            filtered_notifications = [n for n in filtered_notifications if n.get('type') == notification_type]
        
        if status != 'all':
            if status == 'read':
                filtered_notifications = [n for n in filtered_notifications if n.get('read', False)]
            elif status == 'unread':
                filtered_notifications = [n for n in filtered_notifications if not n.get('read', False)]
        
        # 按时间排序
        filtered_notifications.sort(key=lambda x: x.get('created_at', datetime.now()), reverse=True)
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_notifications = filtered_notifications[start_idx:end_idx]
        
        total_pages = (len(filtered_notifications) + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        # 统计信息
        total_count = len(notifications_store)
        unread_count = len([n for n in notifications_store if not n.get('read', False)])
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_list_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={
                'type': notification_type,
                'status': status,
                'total_count': total_count,
                'filtered_count': len(filtered_notifications)
            }
        )
        
        return render_template('ui_notifications/list.html',
                               notifications=page_notifications,
                               notification_type=notification_type,
                               status=status,
                               page=page,
                               total_pages=total_pages,
                               has_prev=has_prev,
                               has_next=has_next,
                               total_count=total_count,
                               unread_count=unread_count)
    
    except Exception as e:
        flash(f'加载通知列表失败: {str(e)}', 'error')
        return render_template('ui_notifications/list.html', notifications=[], total_count=0, unread_count=0)


@ui_notifications_views_bp.route('/add', methods=['POST'])
def notification_add():
    """添加新通知（HTMX片段）"""
    try:
        start_time = datetime.now()
        global next_notification_id
        
        # 获取通知数据
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()
        
        # 验证必需字段
        if not data.get('title'):
            return '<div class="alert alert-danger">通知标题不能为空</div>'
        
        # 创建通知
        notification = {
            'id': next_notification_id,
            'title': data.get('title'),
            'message': data.get('message', ''),
            'type': data.get('type', 'info'),  # success, info, warning, danger
            'icon': data.get('icon', ''),
            'read': False,
            'created_at': datetime.now(),
            'expires_at': None
        }
        
        # 处理过期时间
        if data.get('expires_in'):
            try:
                expires_in = int(data['expires_in'])
                notification['expires_at'] = datetime.now() + timedelta(seconds=expires_in)
            except ValueError:
                pass
        
        notifications_store.insert(0, notification)
        next_notification_id += 1
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notification_add_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'type': notification['type']}
        )
        
        # 如果是HTMX请求，返回新通知HTML
        if request.headers.get('HX-Request'):
            return render_template('ui_notifications/notification_item.html',
                                   notification=notification)
        
        return jsonify({'success': True, 'notification': notification})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">添加通知失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
def notification_mark_read(notification_id):
    """标记通知为已读（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 查找通知
        notification = None
        for n in notifications_store:
            if n['id'] == notification_id:
                notification = n
                break
        
        if not notification:
            return '<div class="alert alert-danger">通知未找到</div>'
        
        # 标记为已读
        notification['read'] = True
        notification['read_at'] = datetime.now()
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notification_mark_read_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'notification_id': notification_id}
        )
        
        # 如果是HTMX请求，返回更新的通知HTML
        if request.headers.get('HX-Request'):
            return render_template('ui_notifications/notification_item.html',
                                   notification=notification)
        
        return jsonify({'success': True})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">标记已读失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/mark-unread/<int:notification_id>', methods=['POST'])
def notification_mark_unread(notification_id):
    """标记通知为未读（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 查找通知
        notification = None
        for n in notifications_store:
            if n['id'] == notification_id:
                notification = n
                break
        
        if not notification:
            return '<div class="alert alert-danger">通知未找到</div>'
        
        # 标记为未读
        notification['read'] = False
        if 'read_at' in notification:
            del notification['read_at']
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notification_mark_unread_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'notification_id': notification_id}
        )
        
        # 如果是HTMX请求，返回更新的通知HTML
        if request.headers.get('HX-Request'):
            return render_template('ui_notifications/notification_item.html',
                                   notification=notification)
        
        return jsonify({'success': True})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">标记未读失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/delete/<int:notification_id>', methods=['POST'])
def notification_delete(notification_id):
    """删除通知（HTMX片段）"""
    try:
        start_time = datetime.now()
        global notifications_store
        
        # 查找并删除通知
        notifications_store = [n for n in notifications_store if n['id'] != notification_id]
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notification_delete_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'notification_id': notification_id}
        )
        
        # 如果是HTMX请求，返回空内容
        if request.headers.get('HX-Request'):
            return ''
        
        return jsonify({'success': True})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">删除通知失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/mark-all-read', methods=['POST'])
def notifications_mark_all_read():
    """标记所有通知为已读（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 标记所有未读通知为已读
        read_count = 0
        for notification in notifications_store:
            if not notification.get('read', False):
                notification['read'] = True
                notification['read_at'] = datetime.now()
                read_count += 1
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_mark_all_read_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'marked_count': read_count}
        )
        
        # 如果是HTMX请求，返回成功消息
        if request.headers.get('HX-Request'):
            if read_count > 0:
                return f'<div class="alert alert-success">已标记 {read_count} 条通知为已读</div>'
            else:
                return '<div class="alert alert-info">所有通知都已经是已读状态</div>'
        
        return jsonify({'success': True, 'marked_count': read_count})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">标记所有已读失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/clear-all', methods=['POST'])
def notifications_clear_all():
    """清空所有通知（HTMX片段）"""
    try:
        start_time = datetime.now()
        global notifications_store
        
        cleared_count = len(notifications_store)
        notifications_store.clear()
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_clear_all_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'cleared_count': cleared_count}
        )
        
        # 如果是HTMX请求，返回空列表HTML
        if request.headers.get('HX-Request'):
            return render_template('ui_notifications/empty_list.html',
                                   message=f'已清空 {cleared_count} 条通知')
        
        return jsonify({'success': True, 'cleared_count': cleared_count})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">清空通知失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/toast')
def notification_toast():
    """显示Toast通知（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取Toast参数
        title = request.args.get('title', '通知')
        message = request.args.get('message', '')
        notification_type = request.args.get('type', 'info')  # success, info, warning, danger
        icon = request.args.get('icon', '')
        auto_hide = request.args.get('auto_hide', 'true').lower() == 'true'
        hide_delay = request.args.get('hide_delay', 5000, type=int)
        show_close = request.args.get('show_close', 'true').lower() == 'true'
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notification_toast_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'type': notification_type, 'auto_hide': auto_hide}
        )
        
        return render_template('ui_notifications/toast.html',
                               title=title,
                               message=message,
                               notification_type=notification_type,
                               icon=icon,
                               auto_hide=auto_hide,
                               hide_delay=hide_delay,
                               show_close=show_close)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示Toast通知失败: {str(e)}</div>'


@ui_notifications_views_bp.route('/dropdown')
def notifications_dropdown():
    """通知下拉菜单（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取最近的通知
        limit = request.args.get('limit', 5, type=int)
        recent_notifications = sorted(
            notifications_store,
            key=lambda x: x.get('created_at', datetime.now()),
            reverse=True
        )[:limit]
        
        # 统计未读数量
        unread_count = len([n for n in notifications_store if not n.get('read', False)])
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_dropdown_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'limit': limit, 'unread_count': unread_count}
        )
        
        return render_template('ui_notifications/dropdown.html',
                               notifications=recent_notifications,
                               unread_count=unread_count,
                               total_count=len(notifications_store))
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载通知下拉菜单失败: {str(e)}</div>'


@ui_notifications_views_bp.route('/badge')
def notifications_badge():
    """通知徽章（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 统计未读数量
        unread_count = len([n for n in notifications_store if not n.get('read', False)])
        
        # 获取徽章样式参数
        badge_style = request.args.get('style', 'primary')  # primary, secondary, success, danger, warning, info
        show_zero = request.args.get('show_zero', 'false').lower() == 'true'
        max_count = request.args.get('max_count', 99, type=int)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_badge_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'unread_count': unread_count}
        )
        
        return render_template('ui_notifications/badge.html',
                               unread_count=unread_count,
                               badge_style=badge_style,
                               show_zero=show_zero,
                               max_count=max_count)
    
    except Exception as e:
        return f'<span class="badge badge-danger">错误</span>'


@ui_notifications_views_bp.route('/cleanup-expired', methods=['POST'])
def notifications_cleanup_expired():
    """清理过期通知（HTMX片段）"""
    try:
        start_time = datetime.now()
        global notifications_store
        
        now = datetime.now()
        initial_count = len(notifications_store)
        
        # 移除过期通知
        notifications_store = [
            n for n in notifications_store
            if n.get('expires_at') is None or n['expires_at'] > now
        ]
        
        expired_count = initial_count - len(notifications_store)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_cleanup_expired_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'expired_count': expired_count}
        )
        
        # 如果是HTMX请求，返回清理结果
        if request.headers.get('HX-Request'):
            if expired_count > 0:
                return f'<div class="alert alert-success">已清理 {expired_count} 条过期通知</div>'
            else:
                return '<div class="alert alert-info">没有过期的通知需要清理</div>'
        
        return jsonify({'success': True, 'expired_count': expired_count})
    
    except Exception as e:
        error_msg = f'<div class="alert alert-danger">清理过期通知失败: {str(e)}</div>'
        return error_msg if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_notifications_views_bp.route('/init-sample-data', methods=['POST'])
def init_sample_data():
    """初始化示例通知数据（用于演示）"""
    try:
        start_time = datetime.now()
        global notifications_store, next_notification_id
        
        # 清空现有数据
        notifications_store.clear()
        next_notification_id = 1
        
        # 创建示例通知
        sample_notifications = [
            {
                'title': '系统更新',
                'message': '系统将在今晚22:00进行维护更新，预计耗时2小时',
                'type': 'info',
                'icon': 'fa-info-circle'
            },
            {
                'title': '新用户注册',
                'message': '用户 zhang_san 已成功注册',
                'type': 'success',
                'icon': 'fa-user-plus'
            },
            {
                'title': '磁盘空间不足',
                'message': '服务器磁盘使用率已达到85%，请及时清理',
                'type': 'warning',
                'icon': 'fa-exclamation-triangle'
            },
            {
                'title': '登录异常',
                'message': '检测到异常登录活动，请检查账户安全',
                'type': 'danger',
                'icon': 'fa-shield-alt'
            },
            {
                'title': '数据备份完成',
                'message': '每日数据备份已成功完成',
                'type': 'success',
                'icon': 'fa-check-circle'
            }
        ]
        
        for i, sample in enumerate(sample_notifications):
            notification = {
                'id': next_notification_id,
                'title': sample['title'],
                'message': sample['message'],
                'type': sample['type'],
                'icon': sample['icon'],
                'read': i % 3 == 0,  # 部分设为已读
                'created_at': datetime.now() - timedelta(hours=i),
                'expires_at': None
            }
            if notification['read']:
                notification['read_at'] = datetime.now() - timedelta(hours=i-1)
            
            notifications_store.append(notification)
            next_notification_id += 1
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_notifications_init_sample_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'sample_count': len(sample_notifications)}
        )
        
        flash('示例通知数据初始化完成', 'success')
        return redirect(url_for('ui_notifications_views.notifications_list'))
    
    except Exception as e:
        flash(f'初始化示例数据失败: {str(e)}', 'error')
        return redirect(url_for('ui_notifications_views.notifications_list'))