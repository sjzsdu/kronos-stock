"""
使用统计API端点
提供组件使用统计的记录和查询REST API
"""
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.services.performance_service import PerformanceService
from app.models.component_usage_stats import ComponentUsageStats
from app.models.prediction import db
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
from sqlalchemy import func, desc, and_
import json
from datetime import datetime, timedelta

# 创建API蓝图
usage_tracking_bp = Blueprint('usage_tracking_api', __name__, url_prefix='/api/usage-tracking')

# 初始化服务
performance_service = PerformanceService()


class UsageTrackingAPI(MethodView):
    """使用统计API视图类"""
    
    def get(self, stat_id=None):
        """
        获取使用统计
        GET /api/usage-tracking/ - 获取统计列表
        GET /api/usage-tracking/<id> - 获取指定统计详情
        """
        try:
            start_time = datetime.now()
            
            if stat_id:
                # 获取单个统计详情
                stat = ComponentUsageStats.query.get(stat_id)
                if not stat:
                    return jsonify({'error': '使用统计未找到'}), 404
                
                result = {
                    'success': True,
                    'data': {
                        'id': stat.id,
                        'user_id': stat.user_id,
                        'component_config_id': stat.component_config_id,
                        'action_type': stat.action_type,
                        'timestamp': stat.timestamp.isoformat() if stat.timestamp else None,
                        'context_data': stat.context_data,
                        'session_id': stat.session_id,
                        'ip_address': stat.ip_address,
                        'user_agent': stat.user_agent
                    }
                }
            else:
                # 获取统计列表，支持过滤和分页
                user_id = request.args.get('user_id', type=int)
                component_config_id = request.args.get('component_config_id', type=int)
                action_type = request.args.get('action_type')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 50, type=int)
                
                # 构建查询
                query = ComponentUsageStats.query
                
                if user_id:
                    query = query.filter(ComponentUsageStats.user_id == user_id)
                
                if component_config_id:
                    query = query.filter(ComponentUsageStats.component_config_id == component_config_id)
                
                if action_type:
                    query = query.filter(ComponentUsageStats.action_type == action_type)
                
                # 处理日期过滤
                if start_date:
                    try:
                        start_datetime = datetime.fromisoformat(start_date)
                        query = query.filter(ComponentUsageStats.timestamp >= start_datetime)
                    except ValueError:
                        return jsonify({'error': '无效的开始日期格式'}), 400
                
                if end_date:
                    try:
                        end_datetime = datetime.fromisoformat(end_date)
                        query = query.filter(ComponentUsageStats.timestamp <= end_datetime)
                    except ValueError:
                        return jsonify({'error': '无效的结束日期格式'}), 400
                
                # 分页查询
                query = query.order_by(desc(ComponentUsageStats.timestamp))
                stats = query.paginate(
                    page=page, 
                    per_page=per_page, 
                    error_out=False
                )
                
                result = {
                    'success': True,
                    'data': {
                        'statistics': [{
                            'id': stat.id,
                            'user_id': stat.user_id,
                            'component_config_id': stat.component_config_id,
                            'action_type': stat.action_type,
                            'timestamp': stat.timestamp.isoformat() if stat.timestamp else None,
                            'context_data': stat.context_data,
                            'session_id': stat.session_id
                        } for stat in stats.items],
                        'pagination': {
                            'page': stats.page,
                            'pages': stats.pages,
                            'per_page': stats.per_page,
                            'total': stats.total,
                            'has_next': stats.has_next,
                            'has_prev': stats.has_prev
                        }
                    }
                }
            
            # 记录API调用性能
            end_time = datetime.now()
            performance_service.record_metric(
                operation='usage_tracking_get',
                duration=(end_time - start_time).total_seconds(),
                metadata={'stat_id': stat_id, 'method': 'GET'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'获取使用统计失败: {str(e)}'}), 500

    def post(self):
        """
        记录新的使用统计
        POST /api/usage-tracking/
        """
        try:
            start_time = datetime.now()
            
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            required_fields = ['user_id', 'component_config_id', 'action_type']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
            
            # 创建使用统计记录
            stat = ComponentUsageStats(
                user_id=data['user_id'],
                component_config_id=data['component_config_id'],
                action_type=data['action_type'],
                context_data=data.get('context_data', {}),
                session_id=data.get('session_id'),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]  # 限制长度
            )
            
            db.session.add(stat)
            db.session.commit()
            
            result = {
                'success': True,
                'message': '使用统计记录成功',
                'data': {
                    'id': stat.id,
                    'user_id': stat.user_id,
                    'component_config_id': stat.component_config_id,
                    'action_type': stat.action_type,
                    'timestamp': stat.timestamp.isoformat() if stat.timestamp else None
                }
            }
            
            # 记录API调用性能
            end_time = datetime.now()
            performance_service.record_metric(
                operation='usage_tracking_create',
                duration=(end_time - start_time).total_seconds(),
                metadata={'action_type': data['action_type'], 'method': 'POST'}
            )
            
            return jsonify(result), 201
            
        except ValidationError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'记录使用统计失败: {str(e)}'}), 500


# 注册视图类路由
usage_tracking_bp.add_url_rule(
    '/', 
    view_func=UsageTrackingAPI.as_view('usage_tracking_list'),
    methods=['GET', 'POST']
)
usage_tracking_bp.add_url_rule(
    '/<int:stat_id>', 
    view_func=UsageTrackingAPI.as_view('usage_tracking_detail'),
    methods=['GET']
)


@usage_tracking_bp.route('/batch', methods=['POST'])
def batch_record_usage():
    """批量记录使用统计"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        stats_data = data.get('statistics', [])
        
        if not stats_data:
            return jsonify({'error': '统计数据列表不能为空'}), 400
        
        # 批量创建统计记录
        created_stats = []
        for stat_data in stats_data:
            stat = ComponentUsageStats(
                user_id=stat_data.get('user_id'),
                component_config_id=stat_data.get('component_config_id'),
                action_type=stat_data.get('action_type'),
                context_data=stat_data.get('context_data', {}),
                session_id=stat_data.get('session_id'),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:500]
            )
            db.session.add(stat)
            created_stats.append(stat)
        
        db.session.commit()
        
        result = {
            'success': True,
            'message': f'成功记录 {len(created_stats)} 条使用统计',
            'data': {
                'created_count': len(created_stats),
                'statistics': [{
                    'id': stat.id,
                    'user_id': stat.user_id,
                    'component_config_id': stat.component_config_id,
                    'action_type': stat.action_type,
                    'timestamp': stat.timestamp.isoformat() if stat.timestamp else None
                } for stat in created_stats]
            }
        }
        
        # 记录API调用性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_tracking_batch_create',
            duration=(end_time - start_time).total_seconds(),
            metadata={'count': len(created_stats), 'method': 'POST'}
        )
        
        return jsonify(result), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'批量记录使用统计失败: {str(e)}'}), 500


@usage_tracking_bp.route('/statistics/components', methods=['GET'])
def get_component_usage_statistics():
    """获取组件使用统计汇总"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 查询组件使用统计
        stats = db.session.query(
            ComponentUsageStats.component_config_id,
            func.count(ComponentUsageStats.id).label('usage_count'),
            func.count(func.distinct(ComponentUsageStats.user_id)).label('unique_users'),
            func.count(func.distinct(ComponentUsageStats.session_id)).label('unique_sessions')
        ).filter(
            ComponentUsageStats.timestamp >= start_time_range
        ).group_by(
            ComponentUsageStats.component_config_id
        ).order_by(
            desc('usage_count')
        ).limit(limit).all()
        
        result = {
            'success': True,
            'data': {
                'component_statistics': [{
                    'component_config_id': stat.component_config_id,
                    'usage_count': stat.usage_count,
                    'unique_users': stat.unique_users,
                    'unique_sessions': stat.unique_sessions
                } for stat in stats],
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'limit': limit
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_component_statistics',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'limit': limit, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取组件使用统计失败: {str(e)}'}), 500


@usage_tracking_bp.route('/statistics/users', methods=['GET'])
def get_user_usage_statistics():
    """获取用户使用统计汇总"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 查询用户使用统计
        stats = db.session.query(
            ComponentUsageStats.user_id,
            func.count(ComponentUsageStats.id).label('total_actions'),
            func.count(func.distinct(ComponentUsageStats.component_config_id)).label('unique_components'),
            func.count(func.distinct(ComponentUsageStats.session_id)).label('sessions'),
            func.min(ComponentUsageStats.timestamp).label('first_action'),
            func.max(ComponentUsageStats.timestamp).label('last_action')
        ).filter(
            ComponentUsageStats.timestamp >= start_time_range
        ).group_by(
            ComponentUsageStats.user_id
        ).order_by(
            desc('total_actions')
        ).limit(limit).all()
        
        result = {
            'success': True,
            'data': {
                'user_statistics': [{
                    'user_id': stat.user_id,
                    'total_actions': stat.total_actions,
                    'unique_components': stat.unique_components,
                    'sessions': stat.sessions,
                    'first_action': stat.first_action.isoformat() if stat.first_action else None,
                    'last_action': stat.last_action.isoformat() if stat.last_action else None
                } for stat in stats],
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'limit': limit
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_user_statistics',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'limit': limit, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取用户使用统计失败: {str(e)}'}), 500


@usage_tracking_bp.route('/statistics/actions', methods=['GET'])
def get_action_usage_statistics():
    """获取操作类型使用统计"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 24, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 查询操作类型统计
        stats = db.session.query(
            ComponentUsageStats.action_type,
            func.count(ComponentUsageStats.id).label('count'),
            func.count(func.distinct(ComponentUsageStats.user_id)).label('unique_users')
        ).filter(
            ComponentUsageStats.timestamp >= start_time_range
        ).group_by(
            ComponentUsageStats.action_type
        ).order_by(
            desc('count')
        ).all()
        
        result = {
            'success': True,
            'data': {
                'action_statistics': [{
                    'action_type': stat.action_type,
                    'count': stat.count,
                    'unique_users': stat.unique_users
                } for stat in stats],
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                }
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_action_statistics',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取操作统计失败: {str(e)}'}), 500


@usage_tracking_bp.route('/trends', methods=['GET'])
def get_usage_trends():
    """获取使用趋势分析"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 24, type=int)
        interval = request.args.get('interval', 'hour')  # hour, day
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 根据间隔类型生成时间分组
        if interval == 'hour':
            time_format = '%Y-%m-%d %H:00:00'
        elif interval == 'day':
            time_format = '%Y-%m-%d 00:00:00'
        else:
            return jsonify({'error': '无效的时间间隔类型'}), 400
        
        # 查询趋势数据
        trends = db.session.query(
            func.strftime(time_format, ComponentUsageStats.timestamp).label('time_period'),
            func.count(ComponentUsageStats.id).label('usage_count'),
            func.count(func.distinct(ComponentUsageStats.user_id)).label('unique_users')
        ).filter(
            ComponentUsageStats.timestamp >= start_time_range
        ).group_by(
            'time_period'
        ).order_by(
            'time_period'
        ).all()
        
        result = {
            'success': True,
            'data': {
                'trends': [{
                    'time_period': trend.time_period,
                    'usage_count': trend.usage_count,
                    'unique_users': trend.unique_users
                } for trend in trends],
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'interval': interval
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_trends',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'interval': interval, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取使用趋势失败: {str(e)}'}), 500


@usage_tracking_bp.route('/cleanup', methods=['POST'])
def cleanup_old_usage_data():
    """清理旧的使用统计数据"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        days = data.get('days', 90)  # 默认保留90天
        
        if days < 1:
            return jsonify({'error': '保留天数必须大于0'}), 400
        
        # 计算截止时间
        cutoff_time = datetime.now() - timedelta(days=days)
        
        # 删除旧数据
        deleted_count = ComponentUsageStats.query.filter(
            ComponentUsageStats.timestamp < cutoff_time
        ).delete()
        
        db.session.commit()
        
        result = {
            'success': True,
            'message': f'成功清理 {deleted_count} 条旧使用数据',
            'data': {
                'deleted_count': deleted_count,
                'retention_days': days,
                'cutoff_time': cutoff_time.isoformat()
            }
        }
        
        # 记录API调用性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='usage_cleanup',
            duration=(end_time - start_time).total_seconds(),
            metadata={'days': days, 'deleted_count': deleted_count, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'清理使用数据失败: {str(e)}'}), 500