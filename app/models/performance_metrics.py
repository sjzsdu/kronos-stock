"""
性能监控记录数据模型

记录系统性能指标，用于性能分析和优化。
"""
from datetime import datetime, timedelta
from .prediction import db
from sqlalchemy import Index, CheckConstraint, text, func


class PerformanceMetrics(db.Model):
    """性能监控记录模型"""
    __tablename__ = 'performance_metrics'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='监控ID')
    
    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    session_id = db.Column(db.String(100), nullable=False, comment='会话ID')
    
    # 指标信息
    metric_type = db.Column(db.String(50), nullable=False, comment='监控指标类型')
    metric_name = db.Column(db.String(100), nullable=False, comment='指标名称')
    metric_value = db.Column(db.Float, nullable=False, comment='指标数值')
    metric_unit = db.Column(db.String(20), default='ms', comment='指标单位')
    
    # 上下文信息
    page_url = db.Column(db.String(500), nullable=True, comment='页面URL')
    user_agent = db.Column(db.String(500), nullable=True, comment='用户代理')
    additional_data = db.Column(db.JSON, nullable=True, comment='附加数据JSON')
    
    # 时间戳
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, comment='记录时间')
    
    # 关联关系
    user = db.relationship('User', backref='performance_metrics', lazy='select')
    
    # 索引
    __table_args__ = (
        Index('idx_perf_user', 'user_id'),
        Index('idx_perf_session', 'session_id'),
        Index('idx_perf_type', 'metric_type'),
        Index('idx_perf_name', 'metric_name'),
        Index('idx_perf_recorded', 'recorded_at'),
        Index('idx_perf_type_name', 'metric_type', 'metric_name'),
        
        # 检查约束
        CheckConstraint(
            text("metric_type IN ('page_load', 'api_response', 'component_render', 'user_interaction', 'resource_load')"),
            name='chk_metric_type'
        ),
        CheckConstraint(
            text("metric_value >= 0"),
            name='chk_metric_value_positive'
        ),
    )
    
    def __repr__(self):
        return f'<PerformanceMetrics {self.metric_type}:{self.metric_name}={self.metric_value}{self.metric_unit}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'metric_type': self.metric_type,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'metric_unit': self.metric_unit,
            'page_url': self.page_url,
            'user_agent': self.user_agent,
            'additional_data': self.additional_data,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
    
    @classmethod
    def record_metric(cls, metric_type, metric_name, metric_value, 
                     session_id, user_id=None, metric_unit='ms', 
                     page_url=None, user_agent=None, additional_data=None):
        """记录性能指标
        
        Args:
            metric_type: 指标类型
            metric_name: 指标名称
            metric_value: 指标值
            session_id: 会话ID
            user_id: 用户ID（可选）
            metric_unit: 指标单位
            page_url: 页面URL（可选）
            user_agent: 用户代理（可选）
            additional_data: 附加数据（可选）
            
        Returns:
            PerformanceMetrics: 创建的性能指标记录
        """
        metric = cls(
            metric_type=metric_type,
            metric_name=metric_name,
            metric_value=metric_value,
            session_id=session_id,
            user_id=user_id,
            metric_unit=metric_unit,
            page_url=page_url,
            user_agent=user_agent,
            additional_data=additional_data
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return metric
    
    @classmethod
    def get_average_metric(cls, metric_type, metric_name, hours_back=24):
        """获取指定时间内的平均指标值
        
        Args:
            metric_type: 指标类型
            metric_name: 指标名称
            hours_back: 向前查询的小时数
            
        Returns:
            float: 平均值，如果没有数据则返回None
        """
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        avg_value = db.session.query(func.avg(cls.metric_value)).filter(
            cls.metric_type == metric_type,
            cls.metric_name == metric_name,
            cls.recorded_at >= since
        ).scalar()
        
        return avg_value
    
    @classmethod
    def get_performance_summary(cls, hours_back=24):
        """获取性能摘要报告
        
        Args:
            hours_back: 向前查询的小时数
            
        Returns:
            dict: 性能摘要数据
        """
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        # 获取各类型指标的统计
        metrics_stats = db.session.query(
            cls.metric_type,
            cls.metric_name,
            func.count(cls.id).label('count'),
            func.avg(cls.metric_value).label('avg_value'),
            func.min(cls.metric_value).label('min_value'),
            func.max(cls.metric_value).label('max_value')
        ).filter(
            cls.recorded_at >= since
        ).group_by(
            cls.metric_type, cls.metric_name
        ).all()
        
        summary = {}
        for stat in metrics_stats:
            metric_key = f"{stat.metric_type}.{stat.metric_name}"
            summary[metric_key] = {
                'count': stat.count,
                'average': round(stat.avg_value, 2) if stat.avg_value else 0,
                'minimum': stat.min_value,
                'maximum': stat.max_value
            }
        
        return summary
    
    @classmethod
    def get_slow_pages(cls, threshold_ms=1000, hours_back=24, limit=10):
        """获取慢页面列表
        
        Args:
            threshold_ms: 慢页面阈值（毫秒）
            hours_back: 向前查询的小时数
            limit: 返回数量限制
            
        Returns:
            list: 慢页面列表
        """
        since = datetime.utcnow() - timedelta(hours=hours_back)
        
        slow_pages = db.session.query(
            cls.page_url,
            func.avg(cls.metric_value).label('avg_load_time'),
            func.count(cls.id).label('request_count')
        ).filter(
            cls.metric_type == 'page_load',
            cls.recorded_at >= since,
            cls.metric_value >= threshold_ms,
            cls.page_url.isnot(None)
        ).group_by(
            cls.page_url
        ).order_by(
            func.avg(cls.metric_value).desc()
        ).limit(limit).all()
        
        return [{
            'page_url': page.page_url,
            'average_load_time': round(page.avg_load_time, 2),
            'request_count': page.request_count
        } for page in slow_pages]
    
    @classmethod
    def cleanup_old_metrics(cls, days_back=30):
        """清理旧的性能指标数据
        
        Args:
            days_back: 保留天数
            
        Returns:
            int: 删除的记录数
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        deleted_count = cls.query.filter(cls.recorded_at < cutoff_date).delete()
        db.session.commit()
        
        return deleted_count
    
    def is_slow_metric(self, threshold_multiplier=1.5):
        """判断是否为慢指标
        
        Args:
            threshold_multiplier: 阈值倍数
            
        Returns:
            bool: 是否为慢指标
        """
        # 获取同类型指标的平均值
        avg_value = self.__class__.get_average_metric(self.metric_type, self.metric_name)
        
        if avg_value:
            return self.metric_value > avg_value * threshold_multiplier
        
        return False