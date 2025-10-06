"""
UI组件服务类

提供UI组件配置管理的业务逻辑。
"""
from typing import Dict, Any, Optional, List
from app.models import db, UIComponentConfig
from app.utils.exceptions import ValidationError, NotFoundError
import json
import re


class UIService:
    """UI组件服务类"""
    
    @staticmethod
    def create_component_config(component_name: str, component_type: str, 
                              config_data: Dict[str, Any], 
                              user_id: Optional[int] = None,
                              is_active: bool = True) -> UIComponentConfig:
        """
        创建组件配置
        
        Args:
            component_name: 组件名称
            component_type: 组件类型
            config_data: 配置数据
            user_id: 用户ID（可选，None表示全局配置）
            is_active: 是否启用
            
        Returns:
            创建的组件配置对象
            
        Raises:
            ValidationError: 数据验证失败
        """
        # 验证输入数据
        UIService._validate_component_data(component_name, component_type, config_data)
        
        # 检查是否已存在相同配置
        existing = UIComponentConfig.query.filter_by(
            component_name=component_name,
            user_id=user_id,
            is_active=True
        ).first()
        
        if existing:
            raise ValidationError(f"组件配置已存在: {component_name} (用户ID: {user_id})")
        
        # 创建新配置
        config = UIComponentConfig(
            component_name=component_name,
            component_type=component_type,
            config_data=config_data,
            user_id=user_id,
            is_active=is_active
        )
        
        db.session.add(config)
        db.session.commit()
        
        return config
    
    @staticmethod
    def update_component_config(config_id: int, 
                              component_type: Optional[str] = None,
                              config_data: Optional[Dict[str, Any]] = None,
                              is_active: Optional[bool] = None) -> UIComponentConfig:
        """
        更新组件配置
        
        Args:
            config_id: 配置ID
            component_type: 组件类型（可选）
            config_data: 配置数据（可选）
            is_active: 是否启用（可选）
            
        Returns:
            更新后的配置对象
            
        Raises:
            NotFoundError: 配置不存在
            ValidationError: 数据验证失败
        """
        config = UIComponentConfig.query.get(config_id)
        if not config:
            raise NotFoundError(f"组件配置不存在: ID {config_id}")
        
        # 更新字段
        if component_type is not None:
            UIService._validate_component_type(component_type)
            config.component_type = component_type
        
        if config_data is not None:
            UIService._validate_config_data(config_data)
            config.config_data = config_data
            config.increment_version()
        
        if is_active is not None:
            config.is_active = is_active
        
        db.session.commit()
        return config
    
    @staticmethod
    def get_component_config(component_name: str, user_id: Optional[int] = None) -> Optional[UIComponentConfig]:
        """
        获取组件配置
        
        Args:
            component_name: 组件名称
            user_id: 用户ID（可选）
            
        Returns:
            组件配置对象或None
        """
        return UIComponentConfig.get_effective_config(component_name, user_id)
    
    @staticmethod
    def list_component_configs(user_id: Optional[int] = None, 
                             component_type: Optional[str] = None,
                             is_active: Optional[bool] = True) -> List[UIComponentConfig]:
        """
        列出组件配置
        
        Args:
            user_id: 用户ID（可选）
            component_type: 组件类型（可选）
            is_active: 是否启用（可选）
            
        Returns:
            配置列表
        """
        query = UIComponentConfig.query
        
        if user_id is not None:
            query = query.filter_by(user_id=user_id)
        
        if component_type:
            query = query.filter_by(component_type=component_type)
        
        if is_active is not None:
            query = query.filter_by(is_active=is_active)
        
        return query.order_by(UIComponentConfig.created_at.desc()).all()
    
    @staticmethod
    def delete_component_config(config_id: int) -> bool:
        """
        删除组件配置
        
        Args:
            config_id: 配置ID
            
        Returns:
            是否删除成功
            
        Raises:
            NotFoundError: 配置不存在
        """
        config = UIComponentConfig.query.get(config_id)
        if not config:
            raise NotFoundError(f"组件配置不存在: ID {config_id}")
        
        db.session.delete(config)
        db.session.commit()
        return True
    
    @staticmethod
    def get_user_component_count(user_id: int) -> int:
        """获取用户组件配置数量"""
        return UIComponentConfig.query.filter_by(user_id=user_id, is_active=True).count()
    
    @staticmethod
    def get_global_component_count() -> int:
        """获取全局组件配置数量"""
        return UIComponentConfig.query.filter_by(user_id=None, is_active=True).count()
    
    @staticmethod
    def _validate_component_data(component_name: str, component_type: str, 
                               config_data: Dict[str, Any]) -> None:
        """验证组件数据"""
        UIService._validate_component_name(component_name)
        UIService._validate_component_type(component_type)
        UIService._validate_config_data(config_data)
    
    @staticmethod
    def _validate_component_name(component_name: str) -> None:
        """验证组件名称"""
        if not component_name:
            raise ValidationError("组件名称不能为空")
        
        if len(component_name) > 100:
            raise ValidationError("组件名称长度不能超过100字符")
        
        # 验证名称格式（字母、数字、下划线、连字符）
        if not re.match(r'^[a-zA-Z0-9_-]+$', component_name):
            raise ValidationError("组件名称只能包含字母、数字、下划线和连字符")
    
    @staticmethod
    def _validate_component_type(component_type: str) -> None:
        """验证组件类型"""
        valid_types = ['form', 'button', 'card', 'navigation', 'modal', 'notification']
        if component_type not in valid_types:
            raise ValidationError(f"无效的组件类型: {component_type}，有效类型: {valid_types}")
    
    @staticmethod
    def _validate_config_data(config_data: Dict[str, Any]) -> None:
        """验证配置数据"""
        if not isinstance(config_data, dict):
            raise ValidationError("配置数据必须是字典格式")
        
        # 检查数据大小（限制10KB）
        try:
            config_size = len(json.dumps(config_data).encode('utf-8'))
            if config_size > 10 * 1024:  # 10KB
                raise ValidationError("配置数据大小不能超过10KB")
        except (TypeError, ValueError) as e:
            raise ValidationError(f"配置数据格式错误: {str(e)}")
    
    @staticmethod
    def export_user_configs(user_id: int) -> Dict[str, Any]:
        """导出用户配置"""
        configs = UIService.list_component_configs(user_id=user_id)
        return {
            'user_id': user_id,
            'export_time': db.func.now(),
            'configs': [config.to_dict() for config in configs]
        }
    
    @staticmethod
    def import_user_configs(user_id: int, config_data: Dict[str, Any]) -> List[UIComponentConfig]:
        """导入用户配置"""
        imported_configs = []
        
        if 'configs' not in config_data:
            raise ValidationError("导入数据缺少configs字段")
        
        for config_item in config_data['configs']:
            try:
                config = UIService.create_component_config(
                    component_name=config_item['component_name'],
                    component_type=config_item['component_type'],
                    config_data=config_item['config_data'],
                    user_id=user_id
                )
                imported_configs.append(config)
            except ValidationError:
                # 跳过无效配置，继续导入其他配置
                continue
        
        return imported_configs