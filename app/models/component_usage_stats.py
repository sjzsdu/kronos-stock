"""
组件使用统计数据模型

记录用户与UI组件的交互统计，用于用户行为分析。
"""
from datetime import datetime, timedelta
from .prediction import db
from sqlalchemy import Index, CheckConstraint, text, func


class ComponentUsageStats(db.Model):
    """组件使用统计模型"""
    __tablename__ = 'component_usage_stats'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='统计ID')
    
    # 关联信息
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    session_id = db.Column(db.String(100), nullable=False, comment='会话ID')
    
    # 组件信息
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    component_type = db.Column(db.String(50), nullable=False, comment='组件类型')
    action_type = db.Column(db.String(50), nullable=False, comment='操作类型')
    
    # 上下文信息
    page_url = db.Column(db.String(500), nullable=True, comment='页面URL')
    interaction_data = db.Column(db.JSON, nullable=True, comment='交互数据JSON')
    
    # 性能信息
    duration_ms = db.Column(db.Integer, nullable=True, comment='交互持续时间(毫秒)')
    
    # 状态信息
    success = db.Column(db.Boolean, default=True, comment='操作是否成功')
    error_message = db.Column(db.Text, nullable=True, comment='错误信息')
    
    # 时间戳
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, comment='记录时间')
    
    # 关联关系
    user = db.relationship('User', backref='component_usage_stats', lazy='select')
    
    # 索引
    __table_args__ = (
        Index('idx_usage_user', 'user_id'),
        Index('idx_usage_session', 'session_id'),
        Index('idx_usage_component', 'component_name'),
        Index('idx_usage_type', 'component_type'),
        Index('idx_usage_action', 'action_type'),
        Index('idx_usage_recorded', 'recorded_at'),
        Index('idx_usage_success', 'success'),
        Index('idx_usage_component_action', 'component_name', 'action_type'),
        
        # 检查约束
        CheckConstraint(
            text("component_type IN ('form', 'button', 'card', 'navigation', 'modal', 'notification', 'chart', 'table')"),
            name='chk_usage_component_type'
        ),
        CheckConstraint(
            text("action_type IN ('view', 'click', 'submit', 'hover', 'focus', 'scroll', 'expand', 'collapse', 'close')"),
            name='chk_usage_action_type'
        ),
        CheckConstraint(
            text("duration_ms IS NULL OR duration_ms >= 0"),
            name='chk_duration_positive'
        ),
    )
    
    def __repr__(self):
        return f'<ComponentUsageStats {self.component_name}:{self.action_type}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'component_name': self.component_name,
            'component_type': self.component_type,
            'action_type': self.action_type,
            'page_url': self.page_url,
            'interaction_data': self.interaction_data,
            'duration_ms': self.duration_ms,
            'success': self.success,
            'error_message': self.error_message,
            'recorded_at': self.recorded_at.isoformat() if self.recorded_at else None
        }
    
    @classmethod
    def record_usage(cls, component_name, component_type, action_type, session_id,
                    user_id=None, page_url=None, interaction_data=None,
                    duration_ms=None, success=True, error_message=None):
        """记录组件使用统计
        
        Args:
            component_name: 组件名称
            component_type: 组件类型
            action_type: 操作类型
            session_id: 会话ID
            user_id: 用户ID（可选）
            page_url: 页面URL（可选）
            interaction_data: 交互数据（可选）
            duration_ms: 持续时间（可选）
            success: 是否成功
            error_message: 错误信息（可选）
            
        Returns:
            ComponentUsageStats: 创建的统计记录
        """
        usage_stat = cls(
            component_name=component_name,
            component_type=component_type,
            action_type=action_type,
            session_id=session_id,
            user_id=user_id,
            page_url=page_url,
            interaction_data=interaction_data,
            duration_ms=duration_ms,
            success=success,
            error_message=error_message
        )
        
        db.session.add(usage_stat)
        db.session.commit()
        
        return usage_stat


# 更新模型初始化文件