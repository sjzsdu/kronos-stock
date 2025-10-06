"""
表单HTML视图端点
提供HTMX表单组件的动态HTML渲染服务
"""
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from app.services.ui_service import UIService
from app.services.component_render_service import ComponentRenderService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
from datetime import datetime
import json

# 创建视图蓝图
ui_forms_views_bp = Blueprint('ui_forms_views', __name__, url_prefix='/views/ui-forms')

# 初始化服务
ui_service = UIService()
render_service = ComponentRenderService()
performance_service = PerformanceService()


@ui_forms_views_bp.route('/builder')
def form_builder():
    """表单构建器页面"""
    try:
        start_time = datetime.now()
        
        # 获取可用的表单组件配置
        form_configs = ui_service.list_component_configs(
            component_type='form',
            is_active=True,
            per_page=100
        )
        
        # 获取表单字段类型
        field_types = [
            {'value': 'text', 'label': '文本输入', 'icon': 'fa-font'},
            {'value': 'email', 'label': '邮箱输入', 'icon': 'fa-envelope'},
            {'value': 'password', 'label': '密码输入', 'icon': 'fa-lock'},
            {'value': 'number', 'label': '数字输入', 'icon': 'fa-hashtag'},
            {'value': 'textarea', 'label': '多行文本', 'icon': 'fa-align-left'},
            {'value': 'select', 'label': '下拉选择', 'icon': 'fa-chevron-down'},
            {'value': 'multiselect', 'label': '多选下拉', 'icon': 'fa-list-check'},
            {'value': 'radio', 'label': '单选按钮', 'icon': 'fa-circle-dot'},
            {'value': 'checkbox', 'label': '复选框', 'icon': 'fa-square-check'},
            {'value': 'date', 'label': '日期选择', 'icon': 'fa-calendar'},
            {'value': 'datetime', 'label': '日期时间', 'icon': 'fa-clock'},
            {'value': 'file', 'label': '文件上传', 'icon': 'fa-upload'},
            {'value': 'range', 'label': '滑块输入', 'icon': 'fa-sliders'},
            {'value': 'color', 'label': '颜色选择', 'icon': 'fa-palette'},
            {'value': 'switch', 'label': '开关按钮', 'icon': 'fa-toggle-on'},
            {'value': 'hidden', 'label': '隐藏字段', 'icon': 'fa-eye-slash'}
        ]
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_builder_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'form_configs_count': form_configs.total}
        )
        
        return render_template('ui_forms/builder.html',
                               form_configs=form_configs,
                               field_types=field_types)
    
    except Exception as e:
        flash(f'加载表单构建器失败: {str(e)}', 'error')
        return render_template('ui_forms/builder.html', form_configs=None, field_types=[])


@ui_forms_views_bp.route('/preview', methods=['POST'])
def form_preview():
    """表单预览（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取表单定义
        if request.is_json:
            form_data = request.get_json()
        else:
            form_data = json.loads(request.form.get('form_data', '{}'))
        
        if not form_data:
            return '<div class="alert alert-warning">表单数据为空</div>'
        
        # 生成表单HTML
        form_html = render_service.render_form(form_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_preview_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'fields_count': len(form_data.get('fields', []))}
        )
        
        return form_html
    
    except Exception as e:
        return f'<div class="alert alert-danger">表单预览失败: {str(e)}</div>'


@ui_forms_views_bp.route('/field-editor')
def field_editor():
    """字段编辑器（HTMX片段）"""
    try:
        field_type = request.args.get('type', 'text')
        field_index = request.args.get('index', 0, type=int)
        
        # 获取字段的默认配置
        field_config = {
            'type': field_type,
            'name': f'field_{field_index + 1}',
            'label': f'字段 {field_index + 1}',
            'placeholder': '',
            'required': False,
            'readonly': False,
            'disabled': False,
            'help_text': '',
            'css_class': '',
            'validation': {}
        }
        
        # 根据字段类型添加特定配置
        if field_type == 'select' or field_type == 'multiselect':
            field_config['options'] = []
        elif field_type == 'radio' or field_type == 'checkbox':
            field_config['options'] = []
        elif field_type == 'range':
            field_config['min'] = 0
            field_config['max'] = 100
            field_config['step'] = 1
        elif field_type == 'textarea':
            field_config['rows'] = 3
        elif field_type == 'file':
            field_config['accept'] = ''
            field_config['multiple'] = False
        
        return render_template('ui_forms/field_editor.html',
                               field_config=field_config,
                               field_index=field_index)
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载字段编辑器失败: {str(e)}</div>'


@ui_forms_views_bp.route('/field-preview')
def field_preview():
    """字段预览（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取字段配置
        field_config = {}
        for key, value in request.args.items():
            if key.startswith('field_'):
                field_key = key[6:]  # 移除 'field_' 前缀
                field_config[field_key] = value
        
        if not field_config:
            return '<div class="text-muted">请配置字段属性</div>'
        
        # 处理特殊类型的值
        if 'required' in field_config:
            field_config['required'] = field_config['required'].lower() == 'true'
        if 'readonly' in field_config:
            field_config['readonly'] = field_config['readonly'].lower() == 'true'
        if 'disabled' in field_config:
            field_config['disabled'] = field_config['disabled'].lower() == 'true'
        if 'multiple' in field_config:
            field_config['multiple'] = field_config['multiple'].lower() == 'true'
        
        # 处理选项（如果存在）
        options_str = field_config.get('options', '')
        if options_str:
            try:
                field_config['options'] = [
                    {'value': opt.strip(), 'label': opt.strip()}
                    for opt in options_str.split('\n')
                    if opt.strip()
                ]
            except:
                field_config['options'] = []
        
        # 渲染字段
        field_html = render_service.render_form_field(field_config)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_field_preview_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'field_type': field_config.get('type', 'unknown')}
        )
        
        return field_html
    
    except Exception as e:
        return f'<div class="alert alert-danger">字段预览失败: {str(e)}</div>'


@ui_forms_views_bp.route('/save', methods=['POST'])
def form_save():
    """保存表单配置"""
    try:
        start_time = datetime.now()
        
        # 获取表单数据
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                'name': request.form.get('name'),
                'description': request.form.get('description'),
                'form_data': json.loads(request.form.get('form_data', '{}'))
            }
        
        if not data.get('name'):
            flash('表单名称不能为空', 'error')
            return redirect(url_for('ui_forms_views.form_builder'))
        
        # 构建组件配置
        config_schema = {
            'type': 'object',
            'properties': {
                'fields': {
                    'type': 'array',
                    'items': {'type': 'object'}
                }
            }
        }
        
        default_values = data.get('form_data', {})
        
        # 创建表单组件配置
        config = ui_service.create_component_config(
            name=data['name'],
            component_type='form',
            config_schema=config_schema,
            default_values=default_values,
            description=data.get('description', ''),
            version='1.0.0',
            is_active=True
        )
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_save_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'form_name': data['name'], 'fields_count': len(default_values.get('fields', []))}
        )
        
        flash('表单配置保存成功', 'success')
        
        # 如果是HTMX请求，返回成功消息
        if request.headers.get('HX-Request'):
            return render_template('ui_forms/save_success.html',
                                   config=config)
        
        return redirect(url_for('ui_components_views.component_detail', config_id=config.id))
    
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('ui_forms_views.form_builder'))
    except Exception as e:
        flash(f'保存表单配置失败: {str(e)}', 'error')
        return redirect(url_for('ui_forms_views.form_builder'))


@ui_forms_views_bp.route('/load/<int:config_id>')
def form_load(config_id):
    """加载表单配置（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取表单配置
        config = ui_service.get_component_config(config_id)
        if not config or config.component_type != 'form':
            return '<div class="alert alert-danger">表单配置未找到</div>'
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_load_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return render_template('ui_forms/load_form.html', config=config)
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载表单配置失败: {str(e)}</div>'


@ui_forms_views_bp.route('/validate', methods=['POST'])
def form_validate():
    """表单验证（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取表单数据和配置ID
        config_id = request.form.get('config_id', type=int)
        form_values = {}
        
        # 提取表单字段值
        for key, value in request.form.items():
            if not key.startswith('config_id'):
                form_values[key] = value
        
        if not config_id:
            return '<div class="alert alert-danger">缺少表单配置ID</div>'
        
        # 验证表单
        is_valid, errors = ui_service.validate_component_values(config_id, form_values)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_validate_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id, 'is_valid': is_valid, 'fields_count': len(form_values)}
        )
        
        return render_template('ui_forms/validation_result.html',
                               is_valid=is_valid,
                               errors=errors,
                               form_values=form_values)
    
    except Exception as e:
        return f'<div class="alert alert-danger">表单验证失败: {str(e)}</div>'


@ui_forms_views_bp.route('/submit', methods=['POST'])
def form_submit():
    """表单提交处理（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取表单数据
        config_id = request.form.get('config_id', type=int)
        form_values = {}
        
        # 提取表单字段值
        for key, value in request.form.items():
            if not key.startswith('config_id'):
                form_values[key] = value
        
        if not config_id:
            return '<div class="alert alert-danger">缺少表单配置ID</div>'
        
        # 先验证表单
        is_valid, errors = ui_service.validate_component_values(config_id, form_values)
        
        if not is_valid:
            return render_template('ui_forms/validation_result.html',
                                   is_valid=False,
                                   errors=errors,
                                   form_values=form_values)
        
        # TODO: 这里可以添加实际的表单处理逻辑
        # 例如：保存到数据库、发送邮件、调用API等
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_submit_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id, 'fields_count': len(form_values)}
        )
        
        return render_template('ui_forms/submit_success.html',
                               form_values=form_values)
    
    except Exception as e:
        return f'<div class="alert alert-danger">表单提交失败: {str(e)}</div>'


@ui_forms_views_bp.route('/templates')
def form_templates():
    """表单模板列表（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 预定义的表单模板
        templates = [
            {
                'name': '用户注册表单',
                'description': '包含用户名、邮箱、密码等基本注册字段',
                'fields': [
                    {'type': 'text', 'name': 'username', 'label': '用户名', 'required': True},
                    {'type': 'email', 'name': 'email', 'label': '邮箱地址', 'required': True},
                    {'type': 'password', 'name': 'password', 'label': '密码', 'required': True},
                    {'type': 'password', 'name': 'confirm_password', 'label': '确认密码', 'required': True},
                    {'type': 'checkbox', 'name': 'agree_terms', 'label': '同意服务条款', 'required': True}
                ]
            },
            {
                'name': '联系我们表单',
                'description': '客户联系表单，包含姓名、联系方式和消息',
                'fields': [
                    {'type': 'text', 'name': 'name', 'label': '姓名', 'required': True},
                    {'type': 'email', 'name': 'email', 'label': '邮箱地址', 'required': True},
                    {'type': 'text', 'name': 'phone', 'label': '联系电话', 'required': False},
                    {'type': 'select', 'name': 'subject', 'label': '主题', 'required': True,
                     'options': [
                         {'value': 'general', 'label': '一般咨询'},
                         {'value': 'support', 'label': '技术支持'},
                         {'value': 'sales', 'label': '销售咨询'},
                         {'value': 'other', 'label': '其他'}
                     ]},
                    {'type': 'textarea', 'name': 'message', 'label': '消息内容', 'required': True, 'rows': 5}
                ]
            },
            {
                'name': '产品反馈表单',
                'description': '用于收集用户对产品的反馈和建议',
                'fields': [
                    {'type': 'text', 'name': 'product_name', 'label': '产品名称', 'required': True},
                    {'type': 'radio', 'name': 'rating', 'label': '整体评分', 'required': True,
                     'options': [
                         {'value': '1', 'label': '1星 - 很差'},
                         {'value': '2', 'label': '2星 - 较差'},
                         {'value': '3', 'label': '3星 - 一般'},
                         {'value': '4', 'label': '4星 - 良好'},
                         {'value': '5', 'label': '5星 - 优秀'}
                     ]},
                    {'type': 'multiselect', 'name': 'features', 'label': '喜欢的功能', 'required': False,
                     'options': [
                         {'value': 'ui', 'label': '界面设计'},
                         {'value': 'performance', 'label': '性能表现'},
                         {'value': 'features', 'label': '功能丰富'},
                         {'value': 'support', 'label': '客户支持'},
                         {'value': 'price', 'label': '价格合理'}
                     ]},
                    {'type': 'textarea', 'name': 'suggestions', 'label': '改进建议', 'required': False, 'rows': 4},
                    {'type': 'checkbox', 'name': 'recommend', 'label': '愿意推荐给朋友', 'required': False}
                ]
            },
            {
                'name': '活动报名表单',
                'description': '活动或会议报名表单',
                'fields': [
                    {'type': 'text', 'name': 'full_name', 'label': '姓名', 'required': True},
                    {'type': 'email', 'name': 'email', 'label': '邮箱地址', 'required': True},
                    {'type': 'text', 'name': 'company', 'label': '公司/组织', 'required': False},
                    {'type': 'text', 'name': 'job_title', 'label': '职位', 'required': False},
                    {'type': 'select', 'name': 'experience_level', 'label': '经验水平', 'required': True,
                     'options': [
                         {'value': 'beginner', 'label': '初级'},
                         {'value': 'intermediate', 'label': '中级'},
                         {'value': 'advanced', 'label': '高级'},
                         {'value': 'expert', 'label': '专家'}
                     ]},
                    {'type': 'textarea', 'name': 'expectations', 'label': '参会期望', 'required': False, 'rows': 3},
                    {'type': 'checkbox', 'name': 'newsletter', 'label': '订阅活动通知', 'required': False}
                ]
            }
        ]
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_templates_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'templates_count': len(templates)}
        )
        
        return render_template('ui_forms/templates.html', templates=templates)
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载表单模板失败: {str(e)}</div>'


@ui_forms_views_bp.route('/export/<int:config_id>')
def form_export(config_id):
    """导出表单配置"""
    try:
        start_time = datetime.now()
        
        # 获取表单配置
        config = ui_service.get_component_config(config_id)
        if not config or config.component_type != 'form':
            flash('表单配置未找到', 'error')
            return redirect(url_for('ui_forms_views.form_builder'))
        
        # 生成导出数据
        export_data = {
            'name': config.name,
            'description': config.description,
            'version': config.version,
            'form_data': config.default_values,
            'exported_at': datetime.now().isoformat()
        }
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_form_export_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        # 返回JSON下载
        from flask import Response
        import json
        
        response = Response(
            json.dumps(export_data, indent=2, ensure_ascii=False),
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename=form_config_{config_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            }
        )
        
        return response
    
    except Exception as e:
        flash(f'导出表单配置失败: {str(e)}', 'error')
        return redirect(url_for('ui_forms_views.form_builder'))