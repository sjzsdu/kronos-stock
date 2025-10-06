"""
用户界面偏好数据模型

管理用户的个性化界面设置和偏好。
"""
from datetime import datetime
from .prediction import db
from sqlalchemy import Index, CheckConstraint, text, UniqueConstraint


class UserUIPreferences(db.Model):
    """用户界面偏好模型"""
    __tablename__ = 'user_ui_preferences'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='偏好ID')
    
    # 关联字段
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    
    # 偏好信息
    preference_category = db.Column(db.String(50), nullable=False, comment='偏好类别')
    preference_key = db.Column(db.String(100), nullable=False, comment='偏好键名')
    preference_value = db.Column(db.Text, nullable=False, comment='偏好值')
    value_type = db.Column(db.String(20), default='string', comment='值类型')
    
    # 状态字段
    is_default = db.Column(db.Boolean, default=False, comment='是否为默认值')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='ui_preferences', lazy='select')
    
    # 索引和约束
    __table_args__ = (
        Index('idx_ui_pref_user', 'user_id'),
        Index('idx_ui_pref_category', 'preference_category'),
        Index('idx_ui_pref_key', 'preference_key'),
        Index('idx_ui_pref_user_category', 'user_id', 'preference_category'),
        Index('idx_ui_pref_user_key', 'user_id', 'preference_key'),
        
        # 唯一约束 - 每个用户的每个偏好键只能有一个值
        UniqueConstraint('user_id', 'preference_key', name='uq_user_preference_key'),
        
        # 检查约束
        CheckConstraint(
            text("preference_category IN ('theme', 'layout', 'notification', 'component', 'accessibility')"),
            name='chk_preference_category'
        ),
        CheckConstraint(
            text("value_type IN ('string', 'boolean', 'integer', 'float', 'json')"),
            name='chk_value_type'
        ),
    )
    
    def __repr__(self):
        return f'<UserUIPreferences {self.user_id}:{self.preference_key}={self.preference_value}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'preference_category': self.preference_category,
            'preference_key': self.preference_key,
            'preference_value': self.get_typed_value(),
            'value_type': self.value_type,
            'is_default': self.is_default,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_typed_value(self):
        """根据value_type返回正确类型的值"""
        if self.value_type == 'boolean':
            return self.preference_value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == 'integer':
            try:
                return int(self.preference_value)
            except ValueError:
                return 0
        elif self.value_type == 'float':
            try:
                return float(self.preference_value)
            except ValueError:
                return 0.0
        elif self.value_type == 'json':
            import json
            try:
                return json.loads(self.preference_value)
            except json.JSONDecodeError:
                return {}
        else:
            return self.preference_value
    
    def set_typed_value(self, value):
        """根据值类型设置preference_value"""
        if self.value_type == 'boolean':
            self.preference_value = str(bool(value)).lower()
        elif self.value_type in ('integer', 'float'):
            self.preference_value = str(value)
        elif self.value_type == 'json':
            import json
            self.preference_value = json.dumps(value)
        else:
            self.preference_value = str(value)
    
    @classmethod
    def get_user_preference(cls, user_id, preference_key, default_value=None):
        """获取用户偏好值
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键名
            default_value: 默认值
            
        Returns:
            偏好值，如果不存在则返回默认值
        """
        preference = cls.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()
        
        if preference:
            return preference.get_typed_value()
        
        return default_value
    
    @classmethod
    def set_user_preference(cls, user_id, preference_category, preference_key, 
                          preference_value, value_type='string'):
        """设置用户偏好
        
        Args:
            user_id: 用户ID
            preference_category: 偏好类别
            preference_key: 偏好键名
            preference_value: 偏好值
            value_type: 值类型
            
        Returns:
            UserUIPreferences: 偏好对象
        """
        # 查找现有偏好
        existing_pref = cls.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()
        
        if existing_pref:
            # 更新现有偏好
            existing_pref.preference_category = preference_category
            existing_pref.value_type = value_type
            existing_pref.set_typed_value(preference_value)
            existing_pref.updated_at = datetime.utcnow()
            db.session.commit()
            return existing_pref
        else:
            # 创建新偏好
            new_pref = cls(
                user_id=user_id,
                preference_category=preference_category,
                preference_key=preference_key,
                value_type=value_type
            )
            new_pref.set_typed_value(preference_value)
            
            db.session.add(new_pref)
            db.session.commit()
            return new_pref
    
    @classmethod
    def get_user_preferences_by_category(cls, user_id, category):
        """获取用户指定类别的所有偏好
        
        Args:
            user_id: 用户ID
            category: 偏好类别
            
        Returns:
            dict: 偏好键值对字典
        """
        preferences = cls.query.filter_by(
            user_id=user_id,
            preference_category=category
        ).all()
        
        return {
            pref.preference_key: pref.get_typed_value()
            for pref in preferences
        }
    
    @classmethod
    def get_all_user_preferences(cls, user_id):
        """获取用户所有偏好设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 按类别组织的偏好字典
        """
        preferences = cls.query.filter_by(user_id=user_id).all()
        
        result = {}
        for pref in preferences:
            if pref.preference_category not in result:
                result[pref.preference_category] = {}
            
            result[pref.preference_category][pref.preference_key] = pref.get_typed_value()
        
        return result
    
    @classmethod
    def reset_user_preferences(cls, user_id, category=None):
        """重置用户偏好设置
        
        Args:
            user_id: 用户ID
            category: 偏好类别，为None时重置所有偏好
            
        Returns:
            int: 删除的偏好数量
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if category:
            query = query.filter_by(preference_category=category)
        
        deleted_count = query.delete()
        db.session.commit()
        
        return deleted_count
    
    @classmethod
    def get_default_preferences(cls):
        """获取默认偏好设置模板
        
        Returns:
            dict: 默认偏好设置
        """
        return {
            'theme': {
                'color_scheme': 'light',
                'primary_color': '#3B82F6',
                'font_size': 'medium',
                'compact_mode': False
            },
            'layout': {
                'sidebar_collapsed': False,
                'show_breadcrumbs': True,
                'items_per_page': 20,
                'table_density': 'standard'
            },
            'notification': {
                'email_enabled': True,
                'browser_notifications': True,
                'sound_enabled': False,
                'notification_position': 'top-right'
            },
            'component': {
                'animation_enabled': True,
                'auto_save': True,
                'confirmation_dialogs': True,
                'keyboard_shortcuts': True
            },
            'accessibility': {
                'high_contrast': False,
                'screen_reader_support': False,
                'keyboard_navigation': True,
                'focus_indicators': True
            }
        }
    
    @classmethod
    def initialize_default_preferences(cls, user_id):
        """为新用户初始化默认偏好设置
        
        Args:
            user_id: 用户ID
            
        Returns:
            list: 创建的偏好对象列表
        """
        defaults = cls.get_default_preferences()
        created_preferences = []
        
        for category, preferences in defaults.items():
            for key, value in preferences.items():
                # 确定值类型
                if isinstance(value, bool):
                    value_type = 'boolean'
                elif isinstance(value, int):
                    value_type = 'integer'
                elif isinstance(value, float):
                    value_type = 'float'
                else:
                    value_type = 'string'
                
                pref = cls.set_user_preference(
                    user_id=user_id,
                    preference_category=category,
                    preference_key=key,
                    preference_value=value,
                    value_type=value_type
                )
                pref.is_default = True
                created_preferences.append(pref)
        
        db.session.commit()
        return created_preferences