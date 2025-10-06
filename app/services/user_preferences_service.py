"""
用户偏好服务类

管理用户界面偏好设置的业务逻辑。
"""
from typing import Dict, Any, Optional, List, Union
from app.models import db, UserUIPreferences
from app.utils.exceptions import ValidationError, NotFoundError
import json


class UserPreferencesService:
    """用户偏好服务类"""
    
    VALID_CATEGORIES = ['theme', 'layout', 'notification', 'component', 'accessibility']
    VALID_VALUE_TYPES = ['string', 'boolean', 'integer', 'float', 'json']
    
    @staticmethod
    def set_preference(user_id: int, preference_category: str, 
                      preference_key: str, preference_value: Any,
                      value_type: Optional[str] = None) -> UserUIPreferences:
        """
        设置用户偏好
        
        Args:
            user_id: 用户ID
            preference_category: 偏好类别
            preference_key: 偏好键名
            preference_value: 偏好值
            value_type: 值类型（可选，自动推断）
            
        Returns:
            用户偏好对象
            
        Raises:
            ValidationError: 验证失败
        """
        # 验证参数
        UserPreferencesService._validate_preference_params(
            user_id, preference_category, preference_key, preference_value
        )
        
        # 自动推断值类型
        if value_type is None:
            value_type = UserPreferencesService._infer_value_type(preference_value)
        
        # 验证值类型
        if value_type not in UserPreferencesService.VALID_VALUE_TYPES:
            raise ValidationError(f"无效的值类型: {value_type}")
        
        # 转换值为字符串存储
        preference_value_str = UserPreferencesService._serialize_value(
            preference_value, value_type
        )
        
        # 查找现有偏好
        existing = UserUIPreferences.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()
        
        if existing:
            # 更新现有偏好
            existing.preference_category = preference_category
            existing.preference_value = preference_value_str
            existing.value_type = value_type
            existing.is_default = False
            db.session.commit()
            return existing
        else:
            # 创建新偏好
            preference = UserUIPreferences(
                user_id=user_id,
                preference_category=preference_category,
                preference_key=preference_key,
                preference_value=preference_value_str,
                value_type=value_type,
                is_default=False
            )
            db.session.add(preference)
            db.session.commit()
            return preference
    
    @staticmethod
    def get_preference(user_id: int, preference_key: str, 
                      default_value: Any = None) -> Any:
        """
        获取用户偏好值
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键名
            default_value: 默认值
            
        Returns:
            偏好值或默认值
        """
        preference = UserUIPreferences.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()
        
        if preference:
            return UserPreferencesService._deserialize_value(
                preference.preference_value, preference.value_type
            )
        
        return default_value
    
    @staticmethod
    def get_preferences_by_category(user_id: int, 
                                  preference_category: str) -> Dict[str, Any]:
        """
        按类别获取用户偏好
        
        Args:
            user_id: 用户ID
            preference_category: 偏好类别
            
        Returns:
            偏好字典
        """
        preferences = UserUIPreferences.query.filter_by(
            user_id=user_id,
            preference_category=preference_category
        ).all()
        
        result = {}
        for pref in preferences:
            result[pref.preference_key] = UserPreferencesService._deserialize_value(
                pref.preference_value, pref.value_type
            )
        
        return result
    
    @staticmethod
    def get_all_preferences(user_id: int) -> Dict[str, Dict[str, Any]]:
        """
        获取用户所有偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            按类别分组的偏好字典
        """
        preferences = UserUIPreferences.query.filter_by(user_id=user_id).all()
        
        result = {}
        for pref in preferences:
            category = pref.preference_category
            if category not in result:
                result[category] = {}
            
            result[category][pref.preference_key] = {
                'value': UserPreferencesService._deserialize_value(
                    pref.preference_value, pref.value_type
                ),
                'type': pref.value_type,
                'is_default': pref.is_default,
                'updated_at': pref.updated_at.isoformat() if pref.updated_at else None
            }
        
        return result
    
    @staticmethod
    def delete_preference(user_id: int, preference_key: str) -> bool:
        """
        删除用户偏好
        
        Args:
            user_id: 用户ID
            preference_key: 偏好键名
            
        Returns:
            是否删除成功
        """
        preference = UserUIPreferences.query.filter_by(
            user_id=user_id,
            preference_key=preference_key
        ).first()
        
        if preference:
            db.session.delete(preference)
            db.session.commit()
            return True
        
        return False
    
    @staticmethod
    def reset_preferences(user_id: int, 
                         preference_category: Optional[str] = None) -> int:
        """
        重置用户偏好
        
        Args:
            user_id: 用户ID
            preference_category: 偏好类别（可选，None表示重置所有）
            
        Returns:
            重置的偏好数量
        """
        query = UserUIPreferences.query.filter_by(user_id=user_id)
        
        if preference_category:
            query = query.filter_by(preference_category=preference_category)
        
        count = query.count()
        query.delete()
        db.session.commit()
        
        return count
    
    @staticmethod
    def export_preferences(user_id: int) -> Dict[str, Any]:
        """
        导出用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            导出数据
        """
        preferences = UserPreferencesService.get_all_preferences(user_id)
        
        return {
            'user_id': user_id,
            'export_time': db.func.now(),
            'preferences': preferences
        }
    
    @staticmethod
    def import_preferences(user_id: int, 
                          preferences_data: Dict[str, Any]) -> List[UserUIPreferences]:
        """
        导入用户偏好
        
        Args:
            user_id: 用户ID
            preferences_data: 偏好数据
            
        Returns:
            导入的偏好列表
        """
        imported_preferences = []
        
        if 'preferences' not in preferences_data:
            raise ValidationError("导入数据缺少preferences字段")
        
        for category, category_prefs in preferences_data['preferences'].items():
            for key, pref_info in category_prefs.items():
                try:
                    value = pref_info['value'] if isinstance(pref_info, dict) else pref_info
                    value_type = pref_info.get('type') if isinstance(pref_info, dict) else None
                    
                    preference = UserPreferencesService.set_preference(
                        user_id=user_id,
                        preference_category=category,
                        preference_key=key,
                        preference_value=value,
                        value_type=value_type
                    )
                    imported_preferences.append(preference)
                except ValidationError:
                    # 跳过无效偏好
                    continue
        
        return imported_preferences
    
    @staticmethod
    def get_preference_statistics(user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        获取偏好统计信息
        
        Args:
            user_id: 用户ID（可选，None表示全局统计）
            
        Returns:
            统计信息
        """
        query = UserUIPreferences.query
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        total_count = query.count()
        
        # 按类别统计
        category_stats = {}
        for category in UserPreferencesService.VALID_CATEGORIES:
            count = query.filter_by(preference_category=category).count()
            category_stats[category] = count
        
        # 按类型统计
        type_stats = {}
        for value_type in UserPreferencesService.VALID_VALUE_TYPES:
            count = query.filter_by(value_type=value_type).count()
            type_stats[value_type] = count
        
        return {
            'total_preferences': total_count,
            'by_category': category_stats,
            'by_type': type_stats
        }
    
    @staticmethod
    def _validate_preference_params(user_id: int, preference_category: str,
                                  preference_key: str, preference_value: Any) -> None:
        """验证偏好参数"""
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("无效的用户ID")
        
        if preference_category not in UserPreferencesService.VALID_CATEGORIES:
            raise ValidationError(f"无效的偏好类别: {preference_category}")
        
        if not preference_key or not preference_key.strip():
            raise ValidationError("偏好键名不能为空")
        
        if len(preference_key) > 100:
            raise ValidationError("偏好键名长度不能超过100字符")
        
        if preference_value is None:
            raise ValidationError("偏好值不能为None")
    
    @staticmethod
    def _infer_value_type(value: Any) -> str:
        """推断值类型"""
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, int):
            return 'integer'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        else:
            return 'json'
    
    @staticmethod
    def _serialize_value(value: Any, value_type: str) -> str:
        """序列化值为字符串"""
        if value_type == 'json':
            return json.dumps(value, ensure_ascii=False)
        else:
            return str(value)
    
    @staticmethod
    def _deserialize_value(value_str: str, value_type: str) -> Any:
        """反序列化字符串值"""
        try:
            if value_type == 'boolean':
                return value_str.lower() in ('true', '1', 'yes', 'on')
            elif value_type == 'integer':
                return int(value_str)
            elif value_type == 'float':
                return float(value_str)
            elif value_type == 'json':
                return json.loads(value_str)
            else:  # string
                return value_str
        except (ValueError, json.JSONDecodeError):
            # 如果反序列化失败，返回原字符串
            return value_str