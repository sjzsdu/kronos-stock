"""
性能监控中间件
用于监控请求性能、数据库查询、组件渲染等关键指标
"""
import time
import functools
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from flask import request, g, current_app, jsonify, session
from werkzeug.wrappers import Response
import os
import threading
from collections import defaultdict, deque

from app.models.performance_metrics import PerformanceMetrics
from app.models import db

# 尝试导入psutil，如果不存在则使用模拟实现
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    # 模拟psutil功能
    class MockProcess:
        def memory_info(self):
            return type('MemoryInfo', (), {'rss': 50 * 1024 * 1024})()  # 50MB模拟值
        
        def cpu_percent(self):
            return 5.0  # 5%模拟值
    
    class MockPsutil:
        def Process(self, pid):
            return MockProcess()
        
        def virtual_memory(self):
            return type('VirtualMemory', (), {'total': 8 * 1024 * 1024 * 1024})()  # 8GB模拟值
    
    psutil = MockPsutil()


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_times = deque(maxlen=1000)  # 保留最近1000个请求的时间
        self.db_query_times = deque(maxlen=1000)  # 数据库查询时间
        self.component_render_times = deque(maxlen=500)  # 组件渲染时间
        self.error_counts = defaultdict(int)  # 错误计数
        self.slow_requests = deque(maxlen=100)  # 慢请求记录
        self._lock = threading.Lock()
        
        # 性能阈值配置
        self.slow_request_threshold = 2.0  # 2秒
        self.slow_query_threshold = 0.5  # 0.5秒
        self.memory_warning_threshold = 80  # 内存使用率80%
        
    def record_request_time(self, duration: float, endpoint: str, method: str):
        """记录请求时间"""
        with self._lock:
            self.request_times.append({
                'duration': duration,
                'endpoint': endpoint,
                'method': method,
                'timestamp': datetime.utcnow()
            })
            
            # 记录慢请求
            if duration > self.slow_request_threshold:
                self.slow_requests.append({
                    'duration': duration,
                    'endpoint': endpoint,
                    'method': method,
                    'timestamp': datetime.utcnow()
                })
    
    def record_db_query_time(self, duration: float, query_type: str):
        """记录数据库查询时间"""
        with self._lock:
            self.db_query_times.append({
                'duration': duration,
                'query_type': query_type,
                'timestamp': datetime.utcnow()
            })
    
    def record_component_render_time(self, duration: float, component_id: str):
        """记录组件渲染时间"""
        with self._lock:
            self.component_render_times.append({
                'duration': duration,
                'component_id': component_id,
                'timestamp': datetime.utcnow()
            })
    
    def record_error(self, error_type: str, endpoint: str):
        """记录错误"""
        with self._lock:
            error_key = f"{error_type}:{endpoint}"
            self.error_counts[error_key] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        with self._lock:
            # 计算平均请求时间
            recent_request_times = [r['duration'] for r in list(self.request_times)[-100:]]
            avg_request_time = sum(recent_request_times) / len(recent_request_times) if recent_request_times else 0
            
            # 计算平均数据库查询时间
            recent_db_times = [q['duration'] for q in list(self.db_query_times)[-100:]]
            avg_db_time = sum(recent_db_times) / len(recent_db_times) if recent_db_times else 0
            
            # 系统资源使用情况
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            cpu_percent = process.cpu_percent()
            
            return {
                'request_performance': {
                    'avg_response_time': round(avg_request_time, 3),
                    'total_requests': len(self.request_times),
                    'slow_requests_count': len(self.slow_requests),
                    'requests_per_minute': self._calculate_rpm()
                },
                'database_performance': {
                    'avg_query_time': round(avg_db_time, 3),
                    'total_queries': len(self.db_query_times),
                    'slow_queries_count': sum(1 for q in self.db_query_times if q['duration'] > self.slow_query_threshold)
                },
                'component_performance': {
                    'total_renders': len(self.component_render_times),
                    'avg_render_time': self._calculate_avg_render_time()
                },
                'system_resources': {
                    'memory_usage_mb': round(memory_info.rss / 1024 / 1024, 2),
                    'memory_percent': round(memory_info.rss / psutil.virtual_memory().total * 100, 2),
                    'cpu_percent': round(cpu_percent, 2)
                },
                'errors': dict(self.error_counts)
            }
    
    def _calculate_rpm(self) -> float:
        """计算每分钟请求数"""
        now = datetime.utcnow()
        one_minute_ago = datetime.fromtimestamp(now.timestamp() - 60)
        
        recent_requests = [r for r in self.request_times if r['timestamp'] >= one_minute_ago]
        return len(recent_requests)
    
    def _calculate_avg_render_time(self) -> float:
        """计算平均组件渲染时间"""
        if not self.component_render_times:
            return 0.0
        
        recent_renders = list(self.component_render_times)[-50:]  # 最近50次渲染
        total_time = sum(r['duration'] for r in recent_renders)
        return round(total_time / len(recent_renders), 3)
    
    def get_slow_requests(self) -> list:
        """获取慢请求列表"""
        with self._lock:
            return list(self.slow_requests)
    
    def clear_stats(self):
        """清除统计数据"""
        with self._lock:
            self.request_times.clear()
            self.db_query_times.clear()
            self.component_render_times.clear()
            self.slow_requests.clear()
            self.error_counts.clear()


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


class PerformanceMiddleware:
    """性能监控中间件"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化应用中间件"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        app.teardown_appcontext(self.teardown_request)
        
        # 注册性能监控路由
        self._register_monitoring_routes(app)
    
    def before_request(self):
        """请求开始前的处理"""
        g.start_time = time.time()
        g.db_query_count = 0
        g.db_query_time = 0
        g.component_renders = []
        
        # 记录请求开始时的系统资源
        g.initial_memory = psutil.Process(os.getpid()).memory_info().rss
    
    def after_request(self, response: Response) -> Response:
        """请求结束后的处理"""
        try:
            # 计算请求总时间
            total_time = time.time() - g.get('start_time', time.time())
            
            # 记录请求性能
            performance_monitor.record_request_time(
                total_time,
                request.endpoint or 'unknown',
                request.method
            )
            
            # 记录数据库查询性能
            if hasattr(g, 'db_query_time'):
                performance_monitor.record_db_query_time(
                    g.db_query_time,
                    'aggregate'
                )
            
            # 记录组件渲染性能
            for render_info in g.get('component_renders', []):
                performance_monitor.record_component_render_time(
                    render_info['duration'],
                    render_info['component_id']
                )
            
            # 添加性能头部信息
            response.headers['X-Response-Time'] = f"{total_time:.3f}s"
            response.headers['X-DB-Queries'] = str(g.get('db_query_count', 0))
            response.headers['X-Component-Renders'] = str(len(g.get('component_renders', [])))
            
            # 检查性能警告
            self._check_performance_warnings(total_time, response)
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"性能监控中间件错误: {e}")
            return response
    
    def teardown_request(self, exception):
        """请求清理"""
        if exception:
            # 记录错误
            performance_monitor.record_error(
                type(exception).__name__,
                request.endpoint or 'unknown'
            )
            
            # 异步保存性能数据到数据库
            self._save_performance_metrics_async(exception=exception)
        else:
            self._save_performance_metrics_async()
    
    def _check_performance_warnings(self, total_time: float, response: Response):
        """检查性能警告"""
        warnings = []
        
        # 慢请求警告
        if total_time > performance_monitor.slow_request_threshold:
            warnings.append(f"slow_request:{total_time:.3f}s")
        
        # 内存使用警告
        current_memory = psutil.Process(os.getpid()).memory_info().rss
        memory_percent = current_memory / psutil.virtual_memory().total * 100
        
        if memory_percent > performance_monitor.memory_warning_threshold:
            warnings.append(f"high_memory:{memory_percent:.1f}%")
        
        # 数据库查询警告
        if g.get('db_query_count', 0) > 20:
            warnings.append(f"many_queries:{g.db_query_count}")
        
        if warnings:
            response.headers['X-Performance-Warnings'] = ','.join(warnings)
            current_app.logger.warning(f"性能警告 [{request.endpoint}]: {warnings}")
    
    def _save_performance_metrics_async(self, exception=None):
        """异步保存性能指标到数据库"""
        try:
            # 在生产环境中，这应该使用后台任务队列
            # 这里为了简化直接在线程中处理
            def save_metrics():
                try:
                    with self.app.app_context():
                        # 获取会话ID
                        session_id = session.get('session_id')
                        if not session_id:
                            session_id = str(uuid.uuid4())
                            session['session_id'] = session_id
                        
                        # 记录请求性能指标
                        PerformanceMetrics.record_metric(
                            metric_type='api_response',
                            metric_name=f"{request.method}:{request.endpoint or 'unknown'}",
                            metric_value=(time.time() - g.get('start_time', time.time())) * 1000,  # 转换为毫秒
                            session_id=session_id,
                            user_id=getattr(g, 'current_user_id', None),
                            metric_unit='ms',
                            page_url=request.url,
                            user_agent=request.headers.get('User-Agent'),
                            additional_data={
                                'db_queries': g.get('db_query_count', 0),
                                'component_renders': len(g.get('component_renders', [])),
                                'has_error': exception is not None,
                                'error_type': type(exception).__name__ if exception else None,
                                'memory_usage_mb': self._get_memory_usage()
                            }
                        )
                        
                except Exception as e:
                    current_app.logger.error(f"保存性能指标失败: {e}")
            
            # 在后台线程中保存（生产环境应使用Celery等任务队列）
            threading.Thread(target=save_metrics, daemon=True).start()
            
        except Exception as e:
            current_app.logger.error(f"异步保存性能指标失败: {e}")
    
    def _get_memory_usage(self) -> float:
        """获取当前内存使用量（MB）"""
        try:
            if HAS_PSUTIL:
                process = psutil.Process(os.getpid())
                return process.memory_info().rss / 1024 / 1024
            else:
                return 50.0  # 模拟值
        except Exception:
            return 0.0
    
    def _register_monitoring_routes(self, app):
        """注册性能监控路由"""
        
        @app.route('/api/performance/stats')
        def performance_stats():
            """获取性能统计信息"""
            try:
                stats = performance_monitor.get_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/performance/slow-requests')
        def slow_requests():
            """获取慢请求列表"""
            try:
                slow_reqs = performance_monitor.get_slow_requests()
                return jsonify(slow_reqs)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/performance/clear', methods=['POST'])
        def clear_performance_stats():
            """清除性能统计数据"""
            try:
                performance_monitor.clear_stats()
                return jsonify({'message': '性能统计数据已清除'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500


def monitor_db_query(query_func: Callable) -> Callable:
    """数据库查询监控装饰器"""
    @functools.wraps(query_func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = query_func(*args, **kwargs)
            query_time = time.time() - start_time
            
            # 更新请求上下文中的查询统计
            if hasattr(g, 'db_query_count'):
                g.db_query_count += 1
                g.db_query_time += query_time
            
            # 记录慢查询
            if query_time > performance_monitor.slow_query_threshold:
                current_app.logger.warning(
                    f"慢查询检测: {query_func.__name__} 耗时 {query_time:.3f}s"
                )
            
            return result
            
        except Exception as e:
            query_time = time.time() - start_time
            current_app.logger.error(f"数据库查询错误: {e}, 耗时: {query_time:.3f}s")
            raise
            
    return wrapper


def monitor_component_render(component_id: str):
    """组件渲染监控装饰器"""
    def decorator(render_func: Callable) -> Callable:
        @functools.wraps(render_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = render_func(*args, **kwargs)
                render_time = time.time() - start_time
                
                # 记录组件渲染时间
                if hasattr(g, 'component_renders'):
                    g.component_renders.append({
                        'component_id': component_id,
                        'duration': render_time
                    })
                
                return result
                
            except Exception as e:
                render_time = time.time() - start_time
                current_app.logger.error(
                    f"组件渲染错误 [{component_id}]: {e}, 耗时: {render_time:.3f}s"
                )
                raise
                
        return wrapper
    return decorator


def get_performance_monitor() -> PerformanceMonitor:
    """获取性能监控器实例"""
    return performance_monitor