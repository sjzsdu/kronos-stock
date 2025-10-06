"""
UI组件配置数据模型

支持用户和全局级别的UI组件个性化配置。
"""
from datetime import datetime
from .prediction import db
from sqlalchemy import Index, CheckConstraint, text


class UIComponentConfig(db.Model):
    """UI组件配置模型"""
    __tablename__ = 'ui_component_configs'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='配置ID')
    
    # 关联字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID，空表示全局配置')
    
    # 组件信息
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    component_type = db.Column(db.String(50), nullable=False, comment='组件类型')
    
    # 配置数据
    config_data = db.Column(db.JSON, nullable=False, comment='配置数据JSON')
    
    # 状态字段
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    version = db.Column(db.Integer, default=1, comment='配置版本')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='ui_configs', lazy='select')
    
    # 索引
    __table_args__ = (
        Index('idx_ui_config_user_component', 'user_id', 'component_name'),
        Index('idx_ui_config_type', 'component_type'),
        Index('idx_ui_config_active', 'is_active'),
        
        # 检查约束
        CheckConstraint(
            text("component_type IN ('form', 'button', 'card', 'navigation', 'modal', 'notification')"),
            name='chk_component_type'
        ),
        # 注意：SQLite不支持正则表达式约束，在应用层验证组件名称格式
    )
    
    def __repr__(self):
        return f'<UIComponentConfig {self.component_name}:{self.component_type}>'
    
    def to_dict(self):
        """转换为字典格式，用于API响应"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'component_name': self.component_name,
            'component_type': self.component_type,
            'config_data': self.config_data,
            'is_active': self.is_active,
            'version': self.version,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_config_for_user(cls, component_name, user_id=None):
        """获取用户或全局组件配置
        
        Args:
            component_name: 组件名称
            user_id: 用户ID，为None时获取全局配置
            
        Returns:
            UIComponentConfig: 配置对象，优先返回用户配置，其次全局配置
        """
        # 首先尝试获取用户特定配置
        if user_id:
            user_config = cls.query.filter_by(
                component_name=component_name,
                user_id=user_id,
                is_active=True
            ).first()
            
            if user_config:
                return user_config
        
        # 如果没有用户配置，获取全局配置
        global_config = cls.query.filter_by(
            component_name=component_name,
            user_id=None,
            is_active=True
        ).first()
        
        return global_config
    
    @classmethod
    def create_or_update_config(cls, component_name, component_type, config_data, user_id=None, is_active=True):
        """创建或更新组件配置
        
        Args:
            component_name: 组件名称
            component_type: 组件类型
            config_data: 配置数据字典
            user_id: 用户ID，为None表示全局配置
            is_active: 是否启用
            
        Returns:
            UIComponentConfig: 创建或更新的配置对象
        """
        # 查找现有配置
        existing_config = cls.query.filter_by(
            component_name=component_name,
            user_id=user_id
        ).first()
        
        if existing_config:
            # 更新现有配置
            existing_config.component_type = component_type
            existing_config.config_data = config_data
            existing_config.is_active = is_active
            existing_config.version += 1
            existing_config.updated_at = datetime.utcnow()
            db.session.commit()
            return existing_config
        else:
            # 创建新配置
            new_config = cls(
                component_name=component_name,
                component_type=component_type,
                config_data=config_data,
                user_id=user_id,
                is_active=is_active
            )
            db.session.add(new_config)
            db.session.commit()
            return new_config
    
    def validate_component_type(self):
        """验证组件类型是否有效"""
        valid_types = ['form', 'button', 'card', 'navigation', 'modal', 'notification']
        return self.component_type in valid_types
    
    def validate_component_name(self):
        """验证组件名称格式是否正确"""
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]+$', self.component_name or ''))
    
    def validate_config_data_size(self):
        """验证配置数据大小是否在限制内（10KB）"""
        import json
        config_json = json.dumps(self.config_data) if self.config_data else '{}'
        return len(config_json.encode('utf-8')) <= 10240  # 10KB限制