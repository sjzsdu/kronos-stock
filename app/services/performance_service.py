"""
性能监控服务类

提供系统性能监控和分析功能。
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.models import db, PerformanceMetrics
from app.utils.exceptions import ValidationError, PerformanceError
import statistics


class PerformanceService:
    """性能监控服务类"""
    
    VALID_METRIC_TYPES = ['page_load', 'api_response', 'component_render', 'user_interaction', 'resource_load']
    
    @staticmethod
    def record_metric(session_id: str, metric_type: str, metric_name: str,
                     metric_value: float, user_id: Optional[int] = None,
                     metric_unit: str = 'ms', page_url: Optional[str] = None,
                     user_agent: Optional[str] = None, 
                     additional_data: Optional[Dict[str, Any]] = None) -> PerformanceMetrics:
        """记录性能指标"""
        # 验证参数
        PerformanceService._validate_metric_params(
            session_id, metric_type, metric_name, metric_value
        )
        
        metric = PerformanceMetrics(
            user_id=user_id,
            session_id=session_id,
            metric_type=metric_type,
            metric_name=metric_name,
            metric_value=metric_value,
            metric_unit=metric_unit,
            page_url=page_url,
            user_agent=user_agent,
            additional_data=additional_data or {}
        )
        
        db.session.add(metric)
        db.session.commit()
        return metric
    
    @staticmethod
    def get_metrics_statistics(metric_type: Optional[str] = None,
                             metric_name: Optional[str] = None,
                             start_time: Optional[datetime] = None,
                             end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """获取指标统计信息"""
        query = PerformanceMetrics.query
        
        if metric_type:
            query = query.filter_by(metric_type=metric_type)
        
        if metric_name:
            query = query.filter_by(metric_name=metric_name)
        
        if start_time:
            query = query.filter(PerformanceMetrics.recorded_at >= start_time)
        
        if end_time:
            query = query.filter(PerformanceMetrics.recorded_at <= end_time)
        
        metrics = query.all()
        
        if not metrics:
            return {'count': 0}
        
        values = [m.metric_value for m in metrics]
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'avg': statistics.mean(values),
            'median': statistics.median(values),
            'p95': PerformanceService._percentile(values, 95),
            'p99': PerformanceService._percentile(values, 99)
        }
    
    @staticmethod
    def _validate_metric_params(session_id: str, metric_type: str, 
                              metric_name: str, metric_value: float) -> None:
        """验证指标参数"""
        if not session_id or not session_id.strip():
            raise ValidationError("会话ID不能为空")
        
        if metric_type not in PerformanceService.VALID_METRIC_TYPES:
            raise ValidationError(f"无效的指标类型: {metric_type}")
        
        if not metric_name or not metric_name.strip():
            raise ValidationError("指标名称不能为空")
        
        if metric_value < 0:
            raise ValidationError("指标值不能为负数")
    
    @staticmethod
    def _percentile(data: List[float], percentile: float) -> float:
        """计算百分位数"""
        if not data:
            return 0.0
        
        data_sorted = sorted(data)
        index = (percentile / 100) * (len(data_sorted) - 1)
        
        if index.is_integer():
            return data_sorted[int(index)]
        else:
            lower = data_sorted[int(index)]
            upper = data_sorted[int(index) + 1]
            return lower + (upper - lower) * (index % 1)