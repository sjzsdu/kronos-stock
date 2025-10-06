"""
UI组件配置API端点
提供UI组件配置的CRUD操作REST API
"""
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.services.ui_service import UIService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
import json
from datetime import datetime

# 创建API蓝图
ui_components_bp = Blueprint('ui_components_api', __name__, url_prefix='/api/ui-components')

# 初始化服务
ui_service = UIService()
performance_service = PerformanceService()


class UIComponentConfigAPI(MethodView):
    """UI组件配置API视图类"""
    
    def get(self, config_id=None):
        """
        获取UI组件配置
        GET /api/ui-components/ - 获取所有配置
        GET /api/ui-components/<id> - 获取指定配置
        """
        try:
            # 记录性能监控
            start_time = datetime.now()
            
            if config_id:
                # 获取单个配置
                config = ui_service.get_component_config(config_id)
                if not config:
                    return jsonify({'error': '组件配置未找到'}), 404
                
                result = {
                    'success': True,
                    'data': {
                        'id': config.id,
                        'name': config.name,
                        'component_type': config.component_type,
                        'version': config.version,
                        'config_schema': config.config_schema,
                        'default_values': config.default_values,
                        'validation_rules': config.validation_rules,
                        'is_active': config.is_active,
                        'created_at': config.created_at.isoformat() if config.created_at else None,
                        'updated_at': config.updated_at.isoformat() if config.updated_at else None
                    }
                }
            else:
                # 获取所有配置，支持分页和过滤
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 20, type=int)
                component_type = request.args.get('type')
                is_active = request.args.get('active', type=bool)
                
                configs = ui_service.list_component_configs(
                    component_type=component_type,
                    is_active=is_active,
                    page=page,
                    per_page=per_page
                )
                
                result = {
                    'success': True,
                    'data': {
                        'configs': [{
                            'id': config.id,
                            'name': config.name,
                            'component_type': config.component_type,
                            'version': config.version,
                            'is_active': config.is_active,
                            'created_at': config.created_at.isoformat() if config.created_at else None,
                            'updated_at': config.updated_at.isoformat() if config.updated_at else None
                        } for config in configs.items],
                        'pagination': {
                            'page': configs.page,
                            'pages': configs.pages,
                            'per_page': configs.per_page,
                            'total': configs.total,
                            'has_next': configs.has_next,
                            'has_prev': configs.has_prev
                        }
                    }
                }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='ui_component_get',
                duration=(end_time - start_time).total_seconds(),
                metadata={'config_id': config_id, 'method': 'GET'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'获取组件配置失败: {str(e)}'}), 500

    def post(self):
        """
        创建新的UI组件配置
        POST /api/ui-components/
        """
        try:
            start_time = datetime.now()
            
            # 验证请求数据
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            required_fields = ['name', 'component_type', 'config_schema']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
            
            # 创建组件配置
            config = ui_service.create_component_config(
                name=data['name'],
                component_type=data['component_type'],
                config_schema=data['config_schema'],
                default_values=data.get('default_values', {}),
                validation_rules=data.get('validation_rules', {}),
                version=data.get('version', '1.0.0'),
                description=data.get('description', ''),
                is_active=data.get('is_active', True)
            )
            
            result = {
                'success': True,
                'message': '组件配置创建成功',
                'data': {
                    'id': config.id,
                    'name': config.name,
                    'component_type': config.component_type,
                    'version': config.version
                }
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='ui_component_create',
                duration=(end_time - start_time).total_seconds(),
                metadata={'component_type': data['component_type'], 'method': 'POST'}
            )
            
            return jsonify(result), 201
            
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except UIServiceError as e:
            return jsonify({'error': str(e)}), 409
        except Exception as e:
            return jsonify({'error': f'创建组件配置失败: {str(e)}'}), 500

    def put(self, config_id):
        """
        更新UI组件配置
        PUT /api/ui-components/<id>
        """
        try:
            start_time = datetime.now()
            
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            
            # 更新组件配置
            config = ui_service.update_component_config(config_id, **data)
            
            result = {
                'success': True,
                'message': '组件配置更新成功',
                'data': {
                    'id': config.id,
                    'name': config.name,
                    'component_type': config.component_type,
                    'version': config.version,
                    'updated_at': config.updated_at.isoformat() if config.updated_at else None
                }
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='ui_component_update',
                duration=(end_time - start_time).total_seconds(),
                metadata={'config_id': config_id, 'method': 'PUT'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'更新组件配置失败: {str(e)}'}), 500

    def delete(self, config_id):
        """
        删除UI组件配置
        DELETE /api/ui-components/<id>
        """
        try:
            start_time = datetime.now()
            
            # 删除组件配置
            ui_service.delete_component_config(config_id)
            
            result = {
                'success': True,
                'message': '组件配置删除成功'
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='ui_component_delete',
                duration=(end_time - start_time).total_seconds(),
                metadata={'config_id': config_id, 'method': 'DELETE'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'删除组件配置失败: {str(e)}'}), 500


# 注册视图类路由
ui_components_bp.add_url_rule(
    '/', 
    view_func=UIComponentConfigAPI.as_view('ui_component_list'),
    methods=['GET', 'POST']
)
ui_components_bp.add_url_rule(
    '/<int:config_id>', 
    view_func=UIComponentConfigAPI.as_view('ui_component_detail'),
    methods=['GET', 'PUT', 'DELETE']
)


@ui_components_bp.route('/types', methods=['GET'])
def get_component_types():
    """获取所有组件类型"""
    try:
        start_time = datetime.now()
        
        # 获取组件类型统计
        types = ui_service.get_component_types_stats()
        
        result = {
            'success': True,
            'data': {
                'types': types
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_types',
            duration=(end_time - start_time).total_seconds(),
            metadata={'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取组件类型失败: {str(e)}'}), 500


@ui_components_bp.route('/validate', methods=['POST'])
def validate_component_config():
    """验证组件配置"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        config_id = data.get('config_id')
        values = data.get('values', {})
        
        if not config_id:
            return jsonify({'error': '缺少config_id参数'}), 400
        
        # 验证配置值
        is_valid, errors = ui_service.validate_component_values(config_id, values)
        
        result = {
            'success': True,
            'data': {
                'is_valid': is_valid,
                'errors': errors
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_validate',
            duration=(end_time - start_time).total_seconds(),
            metadata={'config_id': config_id, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except NotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'验证组件配置失败: {str(e)}'}), 500


@ui_components_bp.route('/export', methods=['GET'])
def export_component_configs():
    """导出组件配置"""
    try:
        start_time = datetime.now()
        
        component_type = request.args.get('type')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # 导出配置
        configs = ui_service.export_component_configs(
            component_type=component_type,
            active_only=active_only
        )
        
        result = {
            'success': True,
            'message': f'成功导出 {len(configs)} 个组件配置',
            'data': {
                'configs': configs,
                'exported_at': datetime.now().isoformat()
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_export',
            duration=(end_time - start_time).total_seconds(),
            metadata={'count': len(configs), 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'导出组件配置失败: {str(e)}'}), 500


@ui_components_bp.route('/import', methods=['POST'])
def import_component_configs():
    """导入组件配置"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        configs = data.get('configs', [])
        overwrite = data.get('overwrite', False)
        
        if not configs:
            return jsonify({'error': '配置列表不能为空'}), 400
        
        # 导入配置
        imported_count, skipped_count = ui_service.import_component_configs(
            configs, overwrite=overwrite
        )
        
        result = {
            'success': True,
            'message': f'成功导入 {imported_count} 个配置，跳过 {skipped_count} 个',
            'data': {
                'imported_count': imported_count,
                'skipped_count': skipped_count
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='ui_component_import',
            duration=(end_time - start_time).total_seconds(),
            metadata={'imported': imported_count, 'skipped': skipped_count, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'导入组件配置失败: {str(e)}'}), 500