"""
数据库查询优化服务
用于优化数据库查询性能和监控慢查询
"""
import time
import functools
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from flask import current_app, g
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query
from collections import defaultdict, deque
import threading

from app import db
from app.models.performance_metrics import PerformanceMetrics


class QueryOptimizer:
    """查询优化器"""
    
    def __init__(self):
        self.slow_query_threshold = 0.5  # 慢查询阈值（秒）
        self.query_cache = {}  # 简单的查询缓存
        self.query_stats = defaultdict(list)  # 查询统计
        self.slow_queries = deque(maxlen=100)  # 慢查询记录
        self._lock = threading.Lock()
        
        # 注册SQL事件监听器
        self._setup_query_monitoring()
    
    def _setup_query_monitoring(self):
        """设置查询监控"""
        
        @event.listens_for(Engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """查询执行前的处理"""
            context._query_start_time = time.time()
            context._query_statement = statement
            
        @event.listens_for(Engine, "after_cursor_execute")
        def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            """查询执行后的处理"""
            if hasattr(context, '_query_start_time'):
                query_time = time.time() - context._query_start_time
                
                # 记录查询统计
                self.record_query_execution(statement, query_time, parameters)
                
                # 更新Flask上下文中的查询统计
                if hasattr(g, 'db_query_count'):
                    g.db_query_count += 1
                    g.db_query_time += query_time
    
    def record_query_execution(self, statement: str, execution_time: float, parameters=None):
        """记录查询执行情况"""
        with self._lock:
            # 简化SQL语句用于统计
            simplified_statement = self._simplify_sql(statement)
            
            # 记录到统计数据
            self.query_stats[simplified_statement].append({
                'execution_time': execution_time,
                'timestamp': datetime.utcnow(),
                'parameters': parameters
            })
            
            # 检查是否为慢查询
            if execution_time > self.slow_query_threshold:
                self.slow_queries.append({
                    'statement': simplified_statement,
                    'execution_time': execution_time,
                    'timestamp': datetime.utcnow(),
                    'full_statement': statement[:1000]  # 限制长度
                })
                
                # 记录慢查询日志
                current_app.logger.warning(
                    f"慢查询检测: {execution_time:.3f}s - {simplified_statement[:100]}..."
                )
    
    def _simplify_sql(self, statement: str) -> str:
        """简化SQL语句，用于统计分组"""
        # 移除多余空格和换行
        simplified = ' '.join(statement.split())
        
        # 替换参数占位符
        simplified = simplified.replace('?', '%s')
        
        # 截取前200个字符用于分组
        return simplified[:200]
    
    def get_query_stats(self) -> Dict[str, Any]:
        """获取查询统计信息"""
        with self._lock:
            stats = {}
            
            for statement, executions in self.query_stats.items():
                if not executions:
                    continue
                    
                execution_times = [e['execution_time'] for e in executions]
                
                stats[statement] = {
                    'count': len(executions),
                    'avg_time': sum(execution_times) / len(execution_times),
                    'min_time': min(execution_times),
                    'max_time': max(execution_times),
                    'total_time': sum(execution_times),
                    'slow_count': sum(1 for t in execution_times if t > self.slow_query_threshold)
                }
            
            return stats
    
    def get_slow_queries(self, limit: int = 20) -> List[Dict[str, Any]]:
        """获取慢查询列表"""
        with self._lock:
            return list(self.slow_queries)[-limit:]
    
    def optimize_query(self, query: Query) -> Query:
        """优化查询对象"""
        # 这里可以添加查询优化逻辑
        # 例如：自动添加索引提示、优化连接等
        
        # 暂时返回原查询，后续可以扩展优化逻辑
        return query
    
    def clear_stats(self):
        """清空统计数据"""
        with self._lock:
            self.query_stats.clear()
            self.slow_queries.clear()
            self.query_cache.clear()


# 全局查询优化器实例
query_optimizer = QueryOptimizer()


def optimize_query(func: Callable) -> Callable:
    """查询优化装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # 如果返回的是Query对象，尝试优化
            if hasattr(result, 'filter'):  # 简单判断是否为Query对象
                result = query_optimizer.optimize_query(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            current_app.logger.error(f"查询优化装饰器错误: {e}, 耗时: {execution_time:.3f}s")
            raise
            
    return wrapper


def monitor_slow_queries(threshold: float = 0.5):
    """慢查询监控装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 检查是否为慢查询
                if execution_time > threshold:
                    current_app.logger.warning(
                        f"慢查询函数 {func.__name__}: {execution_time:.3f}s"
                    )
                    
                    # 记录到性能指标
                    try:
                        PerformanceMetrics.record_metric(
                            metric_type='api_response',
                            metric_name=f'slow_query:{func.__name__}',
                            metric_value=execution_time * 1000,
                            session_id=getattr(g, 'session_id', 'unknown'),
                            user_id=getattr(g, 'current_user_id', None),
                            metric_unit='ms'
                        )
                    except Exception as e:
                        current_app.logger.error(f"记录慢查询指标失败: {e}")
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                current_app.logger.error(
                    f"查询函数 {func.__name__} 执行失败: {e}, 耗时: {execution_time:.3f}s"
                )
                raise
                
        return wrapper
    return decorator


class DatabaseConnection:
    """数据库连接优化管理器"""
    
    def __init__(self):
        self.connection_pool_stats = {}
        self.connection_monitor_enabled = True
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接池统计信息"""
        try:
            engine = db.get_engine()
            pool = engine.pool
            
            return {
                'pool_size': pool.size(),
                'pool_checked_in': pool.checkedin(),
                'pool_checked_out': pool.checkedout(),
                'pool_overflow': pool.overflow(),
                'pool_invalid': pool.invalid()
            }
        except Exception as e:
            current_app.logger.error(f"获取连接池统计失败: {e}")
            return {}
    
    def optimize_connection_pool(self, app):
        """优化连接池配置"""
        # 根据应用负载动态调整连接池参数
        # 这里可以添加更复杂的优化逻辑
        
        try:
            # 检查当前连接使用情况
            stats = self.get_connection_stats()
            
            if stats:
                utilization = stats.get('pool_checked_out', 0) / max(stats.get('pool_size', 1), 1)
                
                # 记录连接池使用率
                if utilization > 0.8:
                    current_app.logger.warning(f"数据库连接池使用率过高: {utilization:.2%}")
                elif utilization < 0.2:
                    current_app.logger.info(f"数据库连接池使用率较低: {utilization:.2%}")
                    
        except Exception as e:
            current_app.logger.error(f"连接池优化检查失败: {e}")


# 全局数据库连接管理器
db_connection_manager = DatabaseConnection()


def init_query_optimization(app):
    """初始化查询优化功能"""
    
    # 注册查询统计API路由
    @app.route('/api/performance/query-stats')
    def query_stats():
        """获取查询统计信息"""
        try:
            stats = query_optimizer.get_query_stats()
            return {
                'query_stats': stats,
                'slow_queries': query_optimizer.get_slow_queries(),
                'connection_stats': db_connection_manager.get_connection_stats()
            }
        except Exception as e:
            return {'error': str(e)}, 500
    
    @app.route('/api/performance/clear-query-stats', methods=['POST'])
    def clear_query_stats():
        """清空查询统计数据"""
        try:
            query_optimizer.clear_stats()
            return {'message': '查询统计数据已清空'}
        except Exception as e:
            return {'error': str(e)}, 500
    
    # 定期优化连接池
    @app.before_request
    def optimize_db_connections():
        """定期优化数据库连接"""
        # 每100个请求检查一次连接池
        request_count = getattr(g, 'request_count', 0) + 1
        g.request_count = request_count
        
        if request_count % 100 == 0:
            db_connection_manager.optimize_connection_pool(app)
    
    current_app.logger.info("查询优化功能已初始化")