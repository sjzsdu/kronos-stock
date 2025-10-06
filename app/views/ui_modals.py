"""
模态框HTML视图端点
提供HTMX模态框组件的动态HTML渲染服务
"""
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from app.services.ui_service import UIService
from app.services.component_render_service import ComponentRenderService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
from datetime import datetime
import json

# 创建视图蓝图
ui_modals_views_bp = Blueprint('ui_modals_views', __name__, url_prefix='/views/ui-modals')

# 初始化服务
ui_service = UIService()
render_service = ComponentRenderService()
performance_service = PerformanceService()


@ui_modals_views_bp.route('/show/<int:config_id>')
def modal_show(config_id):
    """显示模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取模态框配置
        config = ui_service.get_component_config(config_id)
        if not config or config.component_type != 'modal':
            return '<div class="alert alert-danger">模态框配置未找到</div>'
        
        # 获取传入的数据
        modal_data = {}
        for key, value in request.args.items():
            modal_data[key] = value
        
        # 渲染模态框
        modal_html = render_service.render_component(config_id, modal_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_show_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return modal_html
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/close')
def modal_close():
    """关闭模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_close_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={}
        )
        
        # 返回空内容来关闭模态框
        return ''
    
    except Exception as e:
        return f'<div class="alert alert-danger">关闭模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/content/<int:config_id>')
def modal_content(config_id):
    """获取模态框内容（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取模态框配置
        config = ui_service.get_component_config(config_id)
        if not config or config.component_type != 'modal':
            return '<div class="alert alert-danger">模态框配置未找到</div>'
        
        # 获取内容数据
        content_data = {}
        for key, value in request.args.items():
            content_data[key] = value
        
        # 渲染模态框内容
        content_html = render_service.render_modal_content(config_id, content_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_content_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return content_html
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载模态框内容失败: {str(e)}</div>'


@ui_modals_views_bp.route('/confirm')
def modal_confirm():
    """确认模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取确认参数
        title = request.args.get('title', '确认操作')
        message = request.args.get('message', '您确定要执行此操作吗？')
        confirm_url = request.args.get('confirm_url', '')
        cancel_url = request.args.get('cancel_url', '')
        confirm_text = request.args.get('confirm_text', '确认')
        cancel_text = request.args.get('cancel_text', '取消')
        confirm_class = request.args.get('confirm_class', 'btn-primary')
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_confirm_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'confirm_url': bool(confirm_url)}
        )
        
        return render_template('ui_modals/confirm.html',
                               title=title,
                               message=message,
                               confirm_url=confirm_url,
                               cancel_url=cancel_url,
                               confirm_text=confirm_text,
                               cancel_text=cancel_text,
                               confirm_class=confirm_class)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示确认模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/alert')
def modal_alert():
    """警告模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取警告参数
        title = request.args.get('title', '提示')
        message = request.args.get('message', '这是一个提示消息')
        alert_type = request.args.get('type', 'info')  # success, info, warning, danger
        ok_text = request.args.get('ok_text', '确定')
        auto_close = request.args.get('auto_close', 'false').lower() == 'true'
        close_delay = request.args.get('close_delay', 3000, type=int)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_alert_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'alert_type': alert_type, 'auto_close': auto_close}
        )
        
        return render_template('ui_modals/alert.html',
                               title=title,
                               message=message,
                               alert_type=alert_type,
                               ok_text=ok_text,
                               auto_close=auto_close,
                               close_delay=close_delay)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示警告模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/form/<int:config_id>')
def modal_form(config_id):
    """表单模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取表单配置
        form_config = ui_service.get_component_config(config_id)
        if not form_config or form_config.component_type != 'form':
            return '<div class="alert alert-danger">表单配置未找到</div>'
        
        # 获取模态框参数
        modal_title = request.args.get('title', form_config.name)
        submit_url = request.args.get('submit_url', '')
        cancel_url = request.args.get('cancel_url', '')
        
        # 获取表单初始数据
        form_data = {}
        for key, value in request.args.items():
            if not key.startswith(('title', 'submit_url', 'cancel_url')):
                form_data[key] = value
        
        # 渲染表单
        form_html = render_service.render_component(config_id, form_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_form_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return render_template('ui_modals/form.html',
                               modal_title=modal_title,
                               form_html=form_html,
                               form_config=form_config,
                               submit_url=submit_url,
                               cancel_url=cancel_url,
                               form_data=form_data)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示表单模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/loading')
def modal_loading():
    """加载中模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取加载参数
        title = request.args.get('title', '加载中...')
        message = request.args.get('message', '请稍候，正在处理您的请求')
        show_progress = request.args.get('show_progress', 'false').lower() == 'true'
        progress_value = request.args.get('progress', 0, type=int)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_loading_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'show_progress': show_progress}
        )
        
        return render_template('ui_modals/loading.html',
                               title=title,
                               message=message,
                               show_progress=show_progress,
                               progress_value=progress_value)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示加载模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/image')
def modal_image():
    """图片预览模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取图片参数
        image_url = request.args.get('url', '')
        image_title = request.args.get('title', '')
        image_description = request.args.get('description', '')
        show_nav = request.args.get('show_nav', 'false').lower() == 'true'
        prev_url = request.args.get('prev_url', '')
        next_url = request.args.get('next_url', '')
        
        if not image_url:
            return '<div class="alert alert-danger">缺少图片URL</div>'
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_image_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'show_nav': show_nav}
        )
        
        return render_template('ui_modals/image.html',
                               image_url=image_url,
                               image_title=image_title,
                               image_description=image_description,
                               show_nav=show_nav,
                               prev_url=prev_url,
                               next_url=next_url)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示图片模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/video')
def modal_video():
    """视频播放模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取视频参数
        video_url = request.args.get('url', '')
        video_title = request.args.get('title', '')
        video_poster = request.args.get('poster', '')
        autoplay = request.args.get('autoplay', 'false').lower() == 'true'
        controls = request.args.get('controls', 'true').lower() == 'true'
        
        if not video_url:
            return '<div class="alert alert-danger">缺少视频URL</div>'
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_video_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'autoplay': autoplay}
        )
        
        return render_template('ui_modals/video.html',
                               video_url=video_url,
                               video_title=video_title,
                               video_poster=video_poster,
                               autoplay=autoplay,
                               controls=controls)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示视频模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/iframe')
def modal_iframe():
    """iframe内容模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取iframe参数
        iframe_url = request.args.get('url', '')
        iframe_title = request.args.get('title', '')
        width = request.args.get('width', '800px')
        height = request.args.get('height', '600px')
        
        if not iframe_url:
            return '<div class="alert alert-danger">缺少iframe URL</div>'
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_iframe_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'iframe_url': bool(iframe_url)}
        )
        
        return render_template('ui_modals/iframe.html',
                               iframe_url=iframe_url,
                               iframe_title=iframe_title,
                               width=width,
                               height=height)
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示iframe模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/custom/<int:config_id>')
def modal_custom(config_id):
    """自定义模态框（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取模态框配置
        config = ui_service.get_component_config(config_id)
        if not config or config.component_type != 'modal':
            return '<div class="alert alert-danger">模态框配置未找到</div>'
        
        # 获取自定义数据
        custom_data = {}
        for key, value in request.args.items():
            custom_data[key] = value
        
        # 渲染自定义模态框
        modal_html = render_service.render_component(config_id, custom_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_custom_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return modal_html
    
    except Exception as e:
        return f'<div class="alert alert-danger">显示自定义模态框失败: {str(e)}</div>'


@ui_modals_views_bp.route('/builder')
def modal_builder():
    """模态框构建器页面"""
    try:
        start_time = datetime.now()
        
        # 获取可用的模态框配置
        modal_configs = ui_service.list_component_configs(
            component_type='modal',
            is_active=True,
            per_page=100
        )
        
        # 模态框类型
        modal_types = [
            {'value': 'alert', 'label': '提示框', 'description': '用于显示简单的提示信息'},
            {'value': 'confirm', 'label': '确认框', 'description': '用于确认用户操作'},
            {'value': 'form', 'label': '表单框', 'description': '在模态框中显示表单'},
            {'value': 'content', 'label': '内容框', 'description': '显示自定义内容'},
            {'value': 'image', 'label': '图片预览', 'description': '预览图片'},
            {'value': 'video', 'label': '视频播放', 'description': '播放视频内容'},
            {'value': 'iframe', 'label': 'iframe嵌入', 'description': '嵌入外部页面'},
            {'value': 'loading', 'label': '加载框', 'description': '显示加载状态'}
        ]
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_modal_builder_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'modal_configs_count': modal_configs.total}
        )
        
        return render_template('ui_modals/builder.html',
                               modal_configs=modal_configs,
                               modal_types=modal_types)
    
    except Exception as e:
        flash(f'加载模态框构建器失败: {str(e)}', 'error')
        return render_template('ui_modals/builder.html', modal_configs=None, modal_types=[])