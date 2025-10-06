"""
UI组件HTML视图端点
提供HTMX组件的动态HTML渲染服务
"""
from flask import Blueprint, request, render_template, flash, redirect, url_for, jsonify
from app.services.ui_service import UIService
from app.services.component_render_service import ComponentRenderService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
from datetime import datetime
import json

# 创建视图蓝图
ui_components_views_bp = Blueprint('ui_components_views', __name__, url_prefix='/views/ui-components')

# 初始化服务
ui_service = UIService()
render_service = ComponentRenderService()
performance_service = PerformanceService()


@ui_components_views_bp.route('/list')
def component_list():
    """组件配置列表页面"""
    try:
        start_time = datetime.now()
        
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        component_type = request.args.get('type')
        search = request.args.get('search')
        
        # 查询组件配置
        configs = ui_service.list_component_configs(
            component_type=component_type,
            search=search,
            page=page,
            per_page=per_page
        )
        
        # 获取组件类型列表
        types = ui_service.get_component_types_stats()
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_list_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'page': page, 'component_type': component_type}
        )
        
        return render_template('ui_components/list.html',
                               configs=configs,
                               types=types,
                               current_type=component_type,
                               search=search)
    
    except Exception as e:
        flash(f'加载组件列表失败: {str(e)}', 'error')
        return render_template('ui_components/list.html', configs=None, types=[])


@ui_components_views_bp.route('/create')
def component_create():
    """创建组件配置页面"""
    try:
        # 获取可用的组件类型
        component_types = [
            {'value': 'form', 'label': '表单组件'},
            {'value': 'table', 'label': '表格组件'},
            {'value': 'chart', 'label': '图表组件'},
            {'value': 'modal', 'label': '模态框组件'},
            {'value': 'notification', 'label': '通知组件'},
            {'value': 'navigation', 'label': '导航组件'},
            {'value': 'card', 'label': '卡片组件'},
            {'value': 'button', 'label': '按钮组件'}
        ]
        
        return render_template('ui_components/create.html',
                               component_types=component_types)
    
    except Exception as e:
        flash(f'加载创建页面失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_list'))


@ui_components_views_bp.route('/create', methods=['POST'])
def component_create_post():
    """处理创建组件配置请求"""
    try:
        start_time = datetime.now()
        
        # 获取表单数据
        data = request.form.to_dict()
        
        # 处理JSON字段
        try:
            config_schema = json.loads(data.get('config_schema', '{}'))
        except json.JSONDecodeError:
            flash('配置模式JSON格式不正确', 'error')
            return redirect(url_for('ui_components_views.component_create'))
        
        try:
            default_values = json.loads(data.get('default_values', '{}'))
        except json.JSONDecodeError:
            flash('默认值JSON格式不正确', 'error')
            return redirect(url_for('ui_components_views.component_create'))
        
        try:
            validation_rules = json.loads(data.get('validation_rules', '{}'))
        except json.JSONDecodeError:
            flash('验证规则JSON格式不正确', 'error')
            return redirect(url_for('ui_components_views.component_create'))
        
        # 创建组件配置
        config = ui_service.create_component_config(
            name=data['name'],
            component_type=data['component_type'],
            config_schema=config_schema,
            default_values=default_values,
            validation_rules=validation_rules,
            version=data.get('version', '1.0.0'),
            description=data.get('description', ''),
            is_active=data.get('is_active') == 'on'
        )
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_create_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'component_type': data['component_type']}
        )
        
        flash('组件配置创建成功', 'success')
        
        # 如果是HTMX请求，返回片段
        if request.headers.get('HX-Request'):
            return render_template('ui_components/success_message.html',
                                   message='组件配置创建成功',
                                   redirect_url=url_for('ui_components_views.component_detail', config_id=config.id))
        
        return redirect(url_for('ui_components_views.component_detail', config_id=config.id))
    
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('ui_components_views.component_create'))
    except Exception as e:
        flash(f'创建组件配置失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_create'))


@ui_components_views_bp.route('/<int:config_id>')
def component_detail(config_id):
    """组件配置详情页面"""
    try:
        start_time = datetime.now()
        
        # 获取组件配置
        config = ui_service.get_component_config(config_id)
        if not config:
            flash('组件配置未找到', 'error')
            return redirect(url_for('ui_components_views.component_list'))
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_detail_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        return render_template('ui_components/detail.html', config=config)
    
    except Exception as e:
        flash(f'加载组件详情失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_list'))


@ui_components_views_bp.route('/<int:config_id>/edit')
def component_edit(config_id):
    """编辑组件配置页面"""
    try:
        # 获取组件配置
        config = ui_service.get_component_config(config_id)
        if not config:
            flash('组件配置未找到', 'error')
            return redirect(url_for('ui_components_views.component_list'))
        
        # 获取可用的组件类型
        component_types = [
            {'value': 'form', 'label': '表单组件'},
            {'value': 'table', 'label': '表格组件'},
            {'value': 'chart', 'label': '图表组件'},
            {'value': 'modal', 'label': '模态框组件'},
            {'value': 'notification', 'label': '通知组件'},
            {'value': 'navigation', 'label': '导航组件'},
            {'value': 'card', 'label': '卡片组件'},
            {'value': 'button', 'label': '按钮组件'}
        ]
        
        return render_template('ui_components/edit.html',
                               config=config,
                               component_types=component_types)
    
    except Exception as e:
        flash(f'加载编辑页面失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_detail', config_id=config_id))


@ui_components_views_bp.route('/<int:config_id>/edit', methods=['POST'])
def component_edit_post(config_id):
    """处理编辑组件配置请求"""
    try:
        start_time = datetime.now()
        
        # 获取表单数据
        data = request.form.to_dict()
        
        # 处理JSON字段
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = data['name']
        
        if 'component_type' in data:
            update_data['component_type'] = data['component_type']
        
        if 'version' in data:
            update_data['version'] = data['version']
        
        if 'description' in data:
            update_data['description'] = data['description']
        
        if 'config_schema' in data:
            try:
                update_data['config_schema'] = json.loads(data['config_schema'])
            except json.JSONDecodeError:
                flash('配置模式JSON格式不正确', 'error')
                return redirect(url_for('ui_components_views.component_edit', config_id=config_id))
        
        if 'default_values' in data:
            try:
                update_data['default_values'] = json.loads(data['default_values'])
            except json.JSONDecodeError:
                flash('默认值JSON格式不正确', 'error')
                return redirect(url_for('ui_components_views.component_edit', config_id=config_id))
        
        if 'validation_rules' in data:
            try:
                update_data['validation_rules'] = json.loads(data['validation_rules'])
            except json.JSONDecodeError:
                flash('验证规则JSON格式不正确', 'error')
                return redirect(url_for('ui_components_views.component_edit', config_id=config_id))
        
        update_data['is_active'] = data.get('is_active') == 'on'
        
        # 更新组件配置
        config = ui_service.update_component_config(config_id, **update_data)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_edit_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        flash('组件配置更新成功', 'success')
        
        # 如果是HTMX请求，返回片段
        if request.headers.get('HX-Request'):
            return render_template('ui_components/success_message.html',
                                   message='组件配置更新成功',
                                   redirect_url=url_for('ui_components_views.component_detail', config_id=config_id))
        
        return redirect(url_for('ui_components_views.component_detail', config_id=config_id))
    
    except NotFoundError as e:
        flash(str(e), 'error')
        return redirect(url_for('ui_components_views.component_list'))
    except ValidationError as e:
        flash(str(e), 'error')
        return redirect(url_for('ui_components_views.component_edit', config_id=config_id))
    except Exception as e:
        flash(f'更新组件配置失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_edit', config_id=config_id))


@ui_components_views_bp.route('/<int:config_id>/delete', methods=['POST'])
def component_delete(config_id):
    """删除组件配置"""
    try:
        start_time = datetime.now()
        
        # 删除组件配置
        ui_service.delete_component_config(config_id)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_delete_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        flash('组件配置删除成功', 'success')
        
        # 如果是HTMX请求，返回重定向指令
        if request.headers.get('HX-Request'):
            from flask import Response
            response = Response()
            response.headers['HX-Redirect'] = url_for('ui_components_views.component_list')
            return response
        
        return redirect(url_for('ui_components_views.component_list'))
    
    except NotFoundError as e:
        flash(str(e), 'error')
        return redirect(url_for('ui_components_views.component_list'))
    except Exception as e:
        flash(f'删除组件配置失败: {str(e)}', 'error')
        return redirect(url_for('ui_components_views.component_detail', config_id=config_id))


@ui_components_views_bp.route('/<int:config_id>/render')
def component_render(config_id):
    """渲染组件预览"""
    try:
        start_time = datetime.now()
        
        # 获取渲染参数
        values = request.args.to_dict()
        
        # 渲染组件
        rendered_html = render_service.render_component(config_id, values)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_render_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id}
        )
        
        # 如果是HTMX请求，直接返回渲染的HTML
        if request.headers.get('HX-Request'):
            return rendered_html
        
        # 否则包装在预览页面中
        return render_template('ui_components/preview.html',
                               config_id=config_id,
                               rendered_html=rendered_html,
                               values=values)
    
    except NotFoundError as e:
        error_html = f'<div class="alert alert-danger">组件未找到: {str(e)}</div>'
        return error_html if request.headers.get('HX-Request') else render_template('error.html', message=str(e))
    except Exception as e:
        error_html = f'<div class="alert alert-danger">渲染失败: {str(e)}</div>'
        return error_html if request.headers.get('HX-Request') else render_template('error.html', message=str(e))


@ui_components_views_bp.route('/<int:config_id>/validate', methods=['POST'])
def component_validate(config_id):
    """验证组件配置值"""
    try:
        start_time = datetime.now()
        
        # 获取验证数据
        if request.is_json:
            values = request.get_json()
        else:
            values = request.form.to_dict()
        
        # 验证配置
        is_valid, errors = ui_service.validate_component_values(config_id, values)
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_validate_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id, 'is_valid': is_valid}
        )
        
        # 如果是HTMX请求，返回验证结果HTML
        if request.headers.get('HX-Request'):
            return render_template('ui_components/validation_result.html',
                                   is_valid=is_valid,
                                   errors=errors)
        
        # 否则返回JSON
        return jsonify({
            'success': True,
            'data': {
                'is_valid': is_valid,
                'errors': errors
            }
        })
    
    except NotFoundError as e:
        error_html = f'<div class="alert alert-danger">组件未找到: {str(e)}</div>'
        return error_html if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 404
    except Exception as e:
        error_html = f'<div class="alert alert-danger">验证失败: {str(e)}</div>'
        return error_html if request.headers.get('HX-Request') else jsonify({'error': str(e)}), 500


@ui_components_views_bp.route('/search')
def component_search():
    """组件配置搜索（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取搜索参数
        search = request.args.get('search', '').strip()
        component_type = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        if not search and not component_type:
            return '<div class="text-muted">请输入搜索关键字或选择组件类型</div>'
        
        # 执行搜索
        configs = ui_service.list_component_configs(
            component_type=component_type,
            search=search,
            page=page,
            per_page=per_page
        )
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_search_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'search': search, 'component_type': component_type, 'results': configs.total}
        )
        
        return render_template('ui_components/search_results.html',
                               configs=configs,
                               search=search,
                               component_type=component_type)
    
    except Exception as e:
        return f'<div class="alert alert-danger">搜索失败: {str(e)}</div>'


@ui_components_views_bp.route('/types')
def component_types():
    """获取组件类型列表（HTMX片段）"""
    try:
        start_time = datetime.now()
        
        # 获取组件类型统计
        types = ui_service.get_component_types_stats()
        
        # 记录性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_types_view',
            duration=(end_time - start_time).total_seconds(),
            metadata={'types_count': len(types)}
        )
        
        return render_template('ui_components/types_list.html', types=types)
    
    except Exception as e:
        return f'<div class="alert alert-danger">加载组件类型失败: {str(e)}</div>'