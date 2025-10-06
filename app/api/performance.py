"""
性能监控API端点
提供系统性能指标记录和查询REST API
"""
from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.services.performance_service import PerformanceService
from app.utils.exceptions import ValidationError, NotFoundError, UIServiceError
import json
from datetime import datetime, timedelta

# 创建API蓝图
performance_bp = Blueprint('performance_api', __name__, url_prefix='/api/performance')

# 初始化服务
performance_service = PerformanceService()


class PerformanceMetricsAPI(MethodView):
    """性能监控API视图类"""
    
    def get(self, metric_id=None):
        """
        获取性能指标
        GET /api/performance/ - 获取性能指标列表
        GET /api/performance/<id> - 获取指定指标详情
        """
        try:
            start_time = datetime.now()
            
            if metric_id:
                # 获取单个指标详情
                metric = performance_service.get_metric_by_id(metric_id)
                if not metric:
                    return jsonify({'error': '性能指标未找到'}), 404
                
                result = {
                    'success': True,
                    'data': {
                        'id': metric.id,
                        'operation': metric.operation,
                        'duration': metric.duration,
                        'timestamp': metric.timestamp.isoformat() if metric.timestamp else None,
                        'metadata': metric.metadata,
                        'status': metric.status,
                        'error_message': metric.error_message
                    }
                }
            else:
                # 获取指标列表，支持过滤和分页
                operation = request.args.get('operation')
                status = request.args.get('status')
                start_date = request.args.get('start_date')
                end_date = request.args.get('end_date')
                page = request.args.get('page', 1, type=int)
                per_page = request.args.get('per_page', 50, type=int)
                
                # 解析日期参数
                start_datetime = None
                end_datetime = None
                
                if start_date:
                    try:
                        start_datetime = datetime.fromisoformat(start_date)
                    except ValueError:
                        return jsonify({'error': '无效的开始日期格式'}), 400
                
                if end_date:
                    try:
                        end_datetime = datetime.fromisoformat(end_date)
                    except ValueError:
                        return jsonify({'error': '无效的结束日期格式'}), 400
                
                # 查询指标
                metrics = performance_service.query_metrics(
                    operation=operation,
                    status=status,
                    start_time=start_datetime,
                    end_time=end_datetime,
                    page=page,
                    per_page=per_page
                )
                
                result = {
                    'success': True,
                    'data': {
                        'metrics': [{
                            'id': metric.id,
                            'operation': metric.operation,
                            'duration': metric.duration,
                            'timestamp': metric.timestamp.isoformat() if metric.timestamp else None,
                            'status': metric.status,
                            'metadata': metric.metadata
                        } for metric in metrics.items],
                        'pagination': {
                            'page': metrics.page,
                            'pages': metrics.pages,
                            'per_page': metrics.per_page,
                            'total': metrics.total,
                            'has_next': metrics.has_next,
                            'has_prev': metrics.has_prev
                        }
                    }
                }
            
            # 记录API调用性能
            end_time = datetime.now()
            performance_service.record_metric(
                operation='performance_api_get',
                duration=(end_time - start_time).total_seconds(),
                metadata={'metric_id': metric_id, 'method': 'GET'}
            )
            
            return jsonify(result)
            
        except NotFoundError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            return jsonify({'error': f'获取性能指标失败: {str(e)}'}), 500

    def post(self):
        """
        记录新的性能指标
        POST /api/performance/
        """
        try:
            start_time = datetime.now()
            
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400
            
            data = request.get_json()
            required_fields = ['operation', 'duration']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                return jsonify({'error': f'缺少必需字段: {", ".join(missing_fields)}'}), 400
            
            # 记录性能指标
            metric = performance_service.record_metric(
                operation=data['operation'],
                duration=data['duration'],
                metadata=data.get('metadata', {}),
                status=data.get('status', 'success'),
                error_message=data.get('error_message')
            )
            
            result = {
                'success': True,
                'message': '性能指标记录成功',
                'data': {
                    'id': metric.id,
                    'operation': metric.operation,
                    'duration': metric.duration,
                    'status': metric.status,
                    'timestamp': metric.timestamp.isoformat() if metric.timestamp else None
                }
            }
            
            return jsonify(result), 201
            
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            return jsonify({'error': f'记录性能指标失败: {str(e)}'}), 500


# 注册视图类路由
performance_bp.add_url_rule(
    '/', 
    view_func=PerformanceMetricsAPI.as_view('performance_list'),
    methods=['GET', 'POST']
)
performance_bp.add_url_rule(
    '/<int:metric_id>', 
    view_func=PerformanceMetricsAPI.as_view('performance_detail'),
    methods=['GET']
)


@performance_bp.route('/statistics', methods=['GET'])
def get_performance_statistics():
    """获取性能统计信息"""
    try:
        start_time = datetime.now()
        
        operation = request.args.get('operation')
        hours = request.args.get('hours', 24, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 获取统计信息
        stats = performance_service.get_operation_statistics(
            operation=operation,
            start_time=start_time_range,
            end_time=end_time
        )
        
        result = {
            'success': True,
            'data': {
                'statistics': stats,
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'operation': operation
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='performance_statistics_api',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'operation_filter': operation, 'hours': hours, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取性能统计失败: {str(e)}'}), 500


@performance_bp.route('/operations', methods=['GET'])
def get_performance_operations():
    """获取所有操作类型的性能概览"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 24, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 获取操作概览
        operations = performance_service.get_operations_overview(
            start_time=start_time_range,
            end_time=end_time
        )
        
        result = {
            'success': True,
            'data': {
                'operations': operations,
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
            operation='performance_operations_api',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取操作概览失败: {str(e)}'}), 500


@performance_bp.route('/trends', methods=['GET'])
def get_performance_trends():
    """获取性能趋势分析"""
    try:
        start_time = datetime.now()
        
        operation = request.args.get('operation')
        hours = request.args.get('hours', 24, type=int)
        interval = request.args.get('interval', 'hour')  # hour, minute
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 获取趋势数据
        trends = performance_service.get_performance_trends(
            operation=operation,
            start_time=start_time_range,
            end_time=end_time,
            interval=interval
        )
        
        result = {
            'success': True,
            'data': {
                'trends': trends,
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'operation': operation,
                'interval': interval
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='performance_trends_api',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'operation': operation, 'hours': hours, 'interval': interval, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取性能趋势失败: {str(e)}'}), 500


@performance_bp.route('/slow-operations', methods=['GET'])
def get_slow_operations():
    """获取慢操作列表"""
    try:
        start_time = datetime.now()
        
        threshold = request.args.get('threshold', 1.0, type=float)  # 秒
        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 获取慢操作
        slow_operations = performance_service.get_slow_operations(
            threshold=threshold,
            start_time=start_time_range,
            end_time=end_time,
            limit=limit
        )
        
        result = {
            'success': True,
            'data': {
                'slow_operations': [{
                    'id': op.id,
                    'operation': op.operation,
                    'duration': op.duration,
                    'timestamp': op.timestamp.isoformat() if op.timestamp else None,
                    'metadata': op.metadata,
                    'status': op.status,
                    'error_message': op.error_message
                } for op in slow_operations],
                'threshold': threshold,
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
            operation='performance_slow_operations_api',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'threshold': threshold, 'hours': hours, 'limit': limit, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取慢操作列表失败: {str(e)}'}), 500


@performance_bp.route('/health', methods=['GET'])
def get_system_health():
    """获取系统健康状况"""
    try:
        start_time = datetime.now()
        
        hours = request.args.get('hours', 1, type=int)
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 获取健康状况
        health = performance_service.get_system_health(
            start_time=start_time_range,
            end_time=end_time
        )
        
        result = {
            'success': True,
            'data': {
                'health': health,
                'time_range': {
                    'start_time': start_time_range.isoformat(),
                    'end_time': end_time.isoformat(),
                    'hours': hours
                },
                'timestamp': end_time.isoformat()
            }
        }
        
        # 记录API调用性能
        api_end_time = datetime.now()
        performance_service.record_metric(
            operation='performance_health_api',
            duration=(api_end_time - start_time).total_seconds(),
            metadata={'hours': hours, 'method': 'GET'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'获取系统健康状况失败: {str(e)}'}), 500


@performance_bp.route('/cleanup', methods=['POST'])
def cleanup_old_metrics():
    """清理旧的性能指标数据"""
    try:
        start_time = datetime.now()
        
        if not request.is_json:
            return jsonify({'error': '请求必须是JSON格式'}), 400
        
        data = request.get_json()
        days = data.get('days', 30)  # 默认保留30天
        
        if days < 1:
            return jsonify({'error': '保留天数必须大于0'}), 400
        
        # 执行清理
        deleted_count = performance_service.cleanup_old_metrics(days=days)
        
        result = {
            'success': True,
            'message': f'成功清理 {deleted_count} 条旧指标数据',
            'data': {
                'deleted_count': deleted_count,
                'retention_days': days
            }
        }
        
        # 记录API调用性能
        end_time = datetime.now()
        performance_service.record_metric(
            operation='performance_cleanup_api',
            duration=(end_time - start_time).total_seconds(),
            metadata={'days': days, 'deleted_count': deleted_count, 'method': 'POST'}
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'清理性能数据失败: {str(e)}'}), 500


@performance_bp.route('/export', methods=['GET'])
def export_performance_metrics():
    """导出性能指标数据"""
    try:
        start_time = datetime.now()
        
        operation = request.args.get('operation')
        hours = request.args.get('hours', 24, type=int)
        format_type = request.args.get('format', 'json')  # json, csv
        
        # 计算时间范围
        end_time = datetime.now()
        start_time_range = end_time - timedelta(hours=hours)
        
        # 导出数据
        export_data = performance_service.export_metrics(
            operation=operation,
            start_time=start_time_range,
            end_time=end_time,
            format_type=format_type
        )
        
        if format_type == 'csv':
            # 返回CSV格式
            from flask import Response
            return Response(
                export_data,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=performance_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
        else:
            # 返回JSON格式
            result = {
                'success': True,
                'message': f'成功导出性能数据',
                'data': {
                    'metrics': export_data,
                    'time_range': {
                        'start_time': start_time_range.isoformat(),
                        'end_time': end_time.isoformat(),
                        'hours': hours
                    },
                    'operation': operation,
                    'format': format_type,
                    'exported_at': datetime.now().isoformat()
                }
            }
            
            # 记录API调用性能
            api_end_time = datetime.now()
            performance_service.record_metric(
                operation='performance_export_api',
                duration=(api_end_time - start_time).total_seconds(),
                metadata={'operation': operation, 'hours': hours, 'format': format_type, 'method': 'GET'}
            )
            
            return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': f'导出性能数据失败: {str(e)}'}), 500