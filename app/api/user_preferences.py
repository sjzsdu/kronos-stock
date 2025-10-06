"""
用户偏好API端点
提供用户界面偏好设置的CRUD操作REST API
"""
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.services.user_preferences_service import UserPreferencesService
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
import json
from datetime import datetime

# 创建API蓝图
user_preferences_bp = Blueprint('user_preferences_api', __name__, url_prefix='/api/user-preferences')

# 初始化服务
preferences_service = UserPreferencesService()
performance_service = PerformanceService()


class UserPreferencesAPI(MethodView):
    """用户偏好API视图类"""
    
    def get(self, user_id=None, preference_id=None):
        """
        获取用户偏好设置
        GET /api/user-preferences/<user_id> - 获取用户所有偏好
        GET /api/user-preferences/<user_id>/<preference_id> - 获取特定偏好
        """
        try:
            start_time = datetime.now()
            
            if not user_id:
                return jsonify({'error': '缺少用户ID'}), 400
            
            if preference_id:
                # 获取单个偏好设置
                preference = preferences_service.get_user_preference(user_id, preference_id)
                if not preference:
                    return jsonify({'error': '偏好设置未找到'}), 404
                
                result = {
                    'success': True,
                    'data': {
                        'id': preference.id,
                        'user_id': preference.user_id,
                        'category': preference.category,
                        'key': preference.key,
                        'value': preference.value,
                        'value_type': preference.value_type,
                        'is_active': preference.is_active,
                        'created_at': preference.created_at.isoformat() if preference.created_at else None,
                        'updated_at': preference.updated_at.isoformat() if preference.updated_at else None
                    }
                }
            else:
                # 获取用户所有偏好设置，支持分类过滤
                category = request.args.get('category')
                active_only = request.args.get('active_only', 'true').lower() == 'true'
                
                preferences = preferences_service.get_user_preferences_by_category(
                    user_id, category, active_only=active_only
                )
                
                result = {
                    'success': True,
                    'data': {
                        'preferences': [{
                            'id': pref.id,
                            'category': pref.category,
                            'key': pref.key,
                            'value': pref.value,
                            'value_type': pref.value_type,
                            'is_active': pref.is_active,
                            'created_at': pref.created_at.isoformat() if pref.created_at else None,
                            'updated_at': pref.updated_at.isoformat() if pref.updated_at else None
                        } for pref in preferences],
                        'user_id': user_id,
                        'category': category
                    }
                }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='user_preference_get',
                duration=(end_time - start_time).total_seconds(),
                metadata={'user_id': user_id, 'preference_id': preference_id, 'method': 'GET'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'获取用户偏好失败: {str(e)}'}), 500

    def post(self, user_id):
        """
        创建新的用户偏好设置
        POST /api/user-preferences/<user_id>
        """
        try:
            start_time = datetime.now()
            
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            required_fields = ['category', 'key', 'value']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
            
            # 创建偏好设置
            preference = preferences_service.create_user_preference(
                user_id=user_id,
                category=data['category'],
                key=data['key'],
                value=data['value'],
                value_type=data.get('value_type', 'string'),
                is_active=data.get('is_active', True)
            )
            
            result = {
                'success': True,
                'message': '偏好设置创建成功',
                'data': {
                    'id': preference.id,
                    'user_id': preference.user_id,
                    'category': preference.category,
                    'key': preference.key,
                    'value': preference.value,
                    'value_type': preference.value_type
                }
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='user_preference_create',
                duration=(end_time - start_time).total_seconds(),
                metadata={'user_id': user_id, 'category': data['category'], 'method': 'POST'}
            )
            
            return jsonify(result), 201
            
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except UIServiceError as e:
            return jsonify({'error': str(e)}), 409
        except Exception as e:
            return jsonify({'error': f'创建偏好设置失败: {str(e)}'}), 500

    def put(self, user_id, preference_id):
        """
        更新用户偏好设置
        PUT /api/user-preferences/<user_id>/<preference_id>
        """
        try:
            start_time = datetime.now()
            
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            
            # 更新偏好设置
            preference = preferences_service.update_user_preference(
                user_id, preference_id, **data
            )
            
            result = {
                'success': True,
                'message': '偏好设置更新成功',
                'data': {
                    'id': preference.id,
                    'user_id': preference.user_id,
                    'category': preference.category,
                    'key': preference.key,
                    'value': preference.value,
                    'value_type': preference.value_type,
                    'updated_at': preference.updated_at.isoformat() if preference.updated_at else None
                }
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='user_preference_update',
                duration=(end_time - start_time).total_seconds(),
                metadata={'user_id': user_id, 'preference_id': preference_id, 'method': 'PUT'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'更新偏好设置失败: {str(e)}'}), 500

    def delete(self, user_id, preference_id):
        """
        删除用户偏好设置
        DELETE /api/user-preferences/<user_id>/<preference_id>
        """
        try:
            start_time = datetime.now()
            
            # 删除偏好设置
            preferences_service.delete_user_preference(user_id, preference_id)
            
            result = {
                'success': True,
                'message': '偏好设置删除成功'
            }
            
            # 记录性能监控
            end_time = datetime.now()
            performance_service.record_metric(
                operation='user_preference_delete',
                duration=(end_time - start_time).total_seconds(),
                metadata={'user_id': user_id, 'preference_id': preference_id, 'method': 'DELETE'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'删除偏好设置失败: {str(e)}'}), 500


# 注册视图类路由
user_preferences_bp.add_url_rule(
    '/<int:user_id>/', 
    view_func=UserPreferencesAPI.as_view('user_preference_list'),
    methods=['GET', 'POST']
)
user_preferences_bp.add_url_rule(
    '/<int:user_id>/<int:preference_id>', 
    view_func=UserPreferencesAPI.as_view('user_preference_detail'),
    methods=['GET', 'PUT', 'DELETE']
)


@user_preferences_bp.route('/<int:user_id>/batch', methods=['POST'])
def batch_update_preferences(user_id):
    """批量更新用户偏好设置"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        preferences = data.get('preferences', [])
        
        if not preferences:
            return jsonify({'error': '偏好设置列表不能为空'}), 400
        
        # 批量更新
        updated_count = preferences_service.batch_update_preferences(user_id, preferences)
        
        result = {
            'success': True,
            'message': f'成功更新 {updated_count} 个偏好设置',
            'data': {
                'updated_count': updated_count
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_batch_update',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'count': updated_count, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'批量更新偏好设置失败: {str(e)}'}), 500


@user_preferences_bp.route('/<int:user_id>/categories', methods=['GET'])
def get_user_preference_categories(user_id):
    """获取用户所有偏好分类"""
    try:
        start_time = datetime.now()
        
        # 获取分类统计
        categories = preferences_service.get_user_preference_categories(user_id)
        
        result = {
            'success': True,
            'data': {
                'categories': categories,
                'user_id': user_id
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_categories',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取偏好分类失败: {str(e)}'}), 500


@user_preferences_bp.route('/<int:user_id>/export', methods=['GET'])
def export_user_preferences(user_id):
    """导出用户偏好设置"""
    try:
        start_time = datetime.now()
        
        category = request.args.get('category')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # 导出偏好设置
        preferences = preferences_service.export_user_preferences(
            user_id, category=category, active_only=active_only
        )
        
        result = {
            'success': True,
            'message': f'成功导出 {len(preferences)} 个偏好设置',
            'data': {
                'preferences': preferences,
                'user_id': user_id,
                'category': category,
                'exported_at': datetime.now().isoformat()
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_export',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'count': len(preferences), 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'导出偏好设置失败: {str(e)}'}), 500


@user_preferences_bp.route('/<int:user_id>/import', methods=['POST'])
def import_user_preferences(user_id):
    """导入用户偏好设置"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        preferences = data.get('preferences', [])
        overwrite = data.get('overwrite', False)
        
        if not preferences:
            return jsonify({'error': '偏好设置列表不能为空'}), 400
        
        # 导入偏好设置
        imported_count, skipped_count = preferences_service.import_user_preferences(
            user_id, preferences, overwrite=overwrite
        )
        
        result = {
            'success': True,
            'message': f'成功导入 {imported_count} 个偏好设置，跳过 {skipped_count} 个',
            'data': {
                'imported_count': imported_count,
                'skipped_count': skipped_count
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_import',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'imported': imported_count, 'skipped': skipped_count, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'导入偏好设置失败: {str(e)}'}), 500


@user_preferences_bp.route('/<int:user_id>/reset', methods=['POST'])
def reset_user_preferences(user_id):
    """重置用户偏好设置为默认值"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        category = data.get('category')
        
        # 重置偏好设置
        reset_count = preferences_service.reset_user_preferences_to_default(
            user_id, category=category
        )
        
        result = {
            'success': True,
            'message': f'成功重置 {reset_count} 个偏好设置',
            'data': {
                'reset_count': reset_count,
                'category': category
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_reset',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'count': reset_count, 'category': category, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'重置偏好设置失败: {str(e)}'}), 500


@user_preferences_bp.route('/<int:user_id>/statistics', methods=['GET'])
def get_user_preference_statistics(user_id):
    """获取用户偏好设置统计信息"""
    try:
        start_time = datetime.now()
        
        # 获取统计信息
        stats = preferences_service.get_user_preference_statistics(user_id)
        
        result = {
            'success': True,
            'data': {
                'statistics': stats,
                'user_id': user_id
            }
        }
        
        # 记录性能监控
        end_time = datetime.now()
        performance_service.record_metric(
            operation='user_preference_statistics',
            duration=(end_time - start_time).total_seconds(),
            metadata={'user_id': user_id, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取偏好统计失败: {str(e)}'}), 500