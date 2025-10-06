"""
组件渲染服务类

提供组件模板渲染和缓存管理功能。
"""
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import time
import hashlib
import json
from flask import render_template_string, render_template, current_app
from app.models import db, ComponentRenderCache
from app.utils.exceptions import RenderError, TemplateError, CacheError, ValidationError


class ComponentRenderService:
    """组件渲染服务类"""
    
    DEFAULT_CACHE_TTL = 300  # 5分钟
    
    @staticmethod
    def render_component(component_name: str, component_type: str, 
                        template_path: str, render_data: Optional[Dict[str, Any]] = None,
                        use_cache: bool = True, cache_ttl: int = DEFAULT_CACHE_TTL) -> Dict[str, Any]:
        """
        渲染组件
        
        Args:
            component_name: 组件名称
            component_type: 组件类型
            template_path: 模板路径
            render_data: 渲染数据
            use_cache: 是否使用缓存
            cache_ttl: 缓存过期时间（秒）
            
        Returns:
            包含渲染结果的字典
            
        Raises:
            ValidationError: 参数验证失败
            TemplateError: 模板渲染失败
            RenderError: 渲染过程失败
        """
        start_time = time.time()
        
        # 验证参数
        ComponentRenderService._validate_render_params(
            component_name, component_type, template_path
        )
        
        render_data = render_data or {}
        cache_info = {'cached': False, 'cache_key': None}
        
        # 尝试从缓存获取
        if use_cache:
            cache_key = ComponentRenderService._generate_cache_key(
                component_name, template_path, render_data
            )
            cache_info['cache_key'] = cache_key
            
            cached_result = ComponentRenderCache.get_cached(cache_key)
            if cached_result:
                render_time = (time.time() - start_time) * 1000
                cache_info['cached'] = True
                
                return {
                    'rendered_html': cached_result.rendered_html,
                    'component_name': component_name,
                    'render_time_ms': render_time,
                    'cache_info': cache_info
                }
        
        # 执行渲染
        try:
            rendered_html = ComponentRenderService._execute_render(
                template_path, render_data
            )
        except Exception as e:
            raise RenderError(f"组件渲染失败: {str(e)}")
        
        render_time = (time.time() - start_time) * 1000
        
        # 保存到缓存
        if use_cache and cache_info['cache_key']:
            try:
                ComponentRenderCache.set_cache(
                    cache_key=cache_info['cache_key'],
                    component_type=component_type,
                    template_path=template_path,
                    rendered_html=rendered_html,
                    render_data=render_data,
                    ttl_seconds=cache_ttl
                )
            except Exception as e:
                # 缓存失败不影响渲染结果
                current_app.logger.warning(f"缓存保存失败: {str(e)}")
        
        return {
            'rendered_html': rendered_html,
            'component_name': component_name,
            'render_time_ms': render_time,
            'cache_info': cache_info
        }
    
    @staticmethod
    def render_template_string_component(component_name: str, 
                                       template_string: str,
                                       render_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        渲染字符串模板组件（不缓存）
        
        Args:
            component_name: 组件名称
            template_string: 模板字符串
            render_data: 渲染数据
            
        Returns:
            包含渲染结果的字典
        """
        start_time = time.time()
        render_data = render_data or {}
        
        try:
            rendered_html = render_template_string(template_string, **render_data)
        except Exception as e:
            raise TemplateError(f"模板字符串渲染失败: {str(e)}")
        
        render_time = (time.time() - start_time) * 1000
        
        return {
            'rendered_html': rendered_html,
            'component_name': component_name,
            'render_time_ms': render_time,
            'cache_info': {'cached': False, 'cache_key': None}
        }
    
    @staticmethod
    def clear_component_cache(component_name: Optional[str] = None,
                            component_type: Optional[str] = None) -> int:
        """
        清理组件缓存
        
        Args:
            component_name: 组件名称（可选）
            component_type: 组件类型（可选）
            
        Returns:
            清理的缓存条目数量
        """
        query = ComponentRenderCache.query
        
        if component_name:
            # 需要根据cache_key中的组件名称进行模糊匹配
            query = query.filter(ComponentRenderCache.cache_key.like(f'%{component_name}%'))
        
        if component_type:
            query = query.filter_by(component_type=component_type)
        
        count = query.count()
        query.delete()
        db.session.commit()
        
        return count
    
    @staticmethod
    def get_cache_statistics() -> Dict[str, Any]:
        """获取缓存统计信息"""
        return ComponentRenderCache.get_cache_stats()
    
    @staticmethod
    def cleanup_expired_cache() -> int:
        """清理过期缓存"""
        return ComponentRenderCache.cleanup_expired()
    
    @staticmethod
    def warm_cache(components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        预热缓存
        
        Args:
            components: 组件列表，每个包含name, type, template_path, render_data
            
        Returns:
            预热结果统计
        """
        results = {
            'total': len(components),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for component in components:
            try:
                ComponentRenderService.render_component(
                    component_name=component['name'],
                    component_type=component['type'],
                    template_path=component['template_path'],
                    render_data=component.get('render_data', {}),
                    use_cache=True
                )
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'component': component['name'],
                    'error': str(e)
                })
        
        return results
    
    @staticmethod
    def _validate_render_params(component_name: str, component_type: str, 
                              template_path: str) -> None:
        """验证渲染参数"""
        if not component_name or not component_name.strip():
            raise ValidationError("组件名称不能为空")
        
        if not component_type or not component_type.strip():
            raise ValidationError("组件类型不能为空")
        
        if not template_path or not template_path.strip():
            raise ValidationError("模板路径不能为空")
        
        # 验证模板路径格式
        if not template_path.endswith('.html'):
            raise ValidationError("模板路径必须以.html结尾")
    
    @staticmethod
    def _generate_cache_key(component_name: str, template_path: str, 
                          render_data: Dict[str, Any]) -> str:
        """生成缓存键"""
        return ComponentRenderCache.generate_cache_key(
            component_name, template_path, render_data
        )
    
    @staticmethod
    def _execute_render(template_path: str, render_data: Dict[str, Any]) -> str:
        """执行模板渲染"""
        try:
            return render_template(template_path, **render_data)
        except FileNotFoundError:
            raise TemplateError(f"模板文件不存在: {template_path}")
        except Exception as e:
            raise TemplateError(f"模板渲染错误: {str(e)}")
    
    @staticmethod
    def get_component_render_history(component_name: Optional[str] = None,
                                   limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取组件渲染历史
        
        Args:
            component_name: 组件名称（可选）
            limit: 返回条目限制
            
        Returns:
            渲染历史列表
        """
        query = ComponentRenderCache.query
        
        if component_name:
            query = query.filter(ComponentRenderCache.cache_key.like(f'%{component_name}%'))
        
        caches = query.order_by(ComponentRenderCache.created_at.desc()).limit(limit).all()
        
        return [
            {
                'cache_key': cache.cache_key,
                'component_type': cache.component_type,
                'template_path': cache.template_path,
                'hit_count': cache.hit_count,
                'created_at': cache.created_at.isoformat(),
                'expires_at': cache.expires_at.isoformat()
            }
            for cache in caches
        ]