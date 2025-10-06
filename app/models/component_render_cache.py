"""
组件渲染缓存数据模型

提升组件渲染性能，减少模板重复处理时间。
"""
from datetime import datetime, timedelta
from .prediction import db
from sqlalchemy import Index, text


class ComponentRenderCache(db.Model):
    """组件渲染缓存模型"""
    __tablename__ = 'component_render_cache'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True, comment='缓存ID')
    
    # 缓存标识
    cache_key = db.Column(db.String(255), nullable=False, unique=True, comment='缓存键')
    
    # 组件信息
    component_type = db.Column(db.String(50), nullable=False, comment='组件类型')
    template_path = db.Column(db.String(255), nullable=False, comment='模板路径')
    
    # 渲染结果
    rendered_html = db.Column(db.Text, nullable=False, comment='渲染后的HTML')
    render_data = db.Column(db.JSON, nullable=True, comment='渲染数据JSON')
    
    # 缓存管理
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    hit_count = db.Column(db.Integer, default=0, comment='缓存命中次数')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 索引
    __table_args__ = (
        Index('idx_cache_key', 'cache_key'),
        Index('idx_cache_component_type', 'component_type'),
        Index('idx_cache_expires', 'expires_at'),
        Index('idx_cache_template', 'template_path'),
    )
    
    def __repr__(self):
        return f'<ComponentRenderCache {self.cache_key}>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'cache_key': self.cache_key,
            'component_type': self.component_type,
            'template_path': self.template_path,
            'rendered_html': self.rendered_html,
            'render_data': self.render_data,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'hit_count': self.hit_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def generate_cache_key(cls, component_name, component_type, template_path, render_data):
        """生成缓存键
        
        Args:
            component_name: 组件名称
            component_type: 组件类型  
            template_path: 模板路径
            render_data: 渲染数据
            
        Returns:
            str: 生成的缓存键
        """
        import hashlib
        import json
        
        # 创建用于生成缓存键的数据
        cache_source = {
            'component_name': component_name,
            'component_type': component_type,
            'template_path': template_path,
            'render_data': render_data
        }
        
        # 生成哈希
        cache_string = json.dumps(cache_source, sort_keys=True, separators=(',', ':'))
        cache_hash = hashlib.md5(cache_string.encode('utf-8')).hexdigest()
        
        return f"comp_{component_type}_{cache_hash[:16]}"
    
    @classmethod
    def get_cached_render(cls, cache_key):
        """获取缓存的渲染结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            ComponentRenderCache: 缓存对象，如果缓存有效
            None: 如果缓存不存在或已过期
        """
        cache_entry = cls.query.filter_by(cache_key=cache_key).first()
        
        if cache_entry and cache_entry.expires_at > datetime.utcnow():
            # 增加命中次数
            cache_entry.hit_count += 1
            db.session.commit()
            return cache_entry
        elif cache_entry:
            # 缓存已过期，删除
            db.session.delete(cache_entry)
            db.session.commit()
        
        return None
    
    @classmethod
    def cache_render_result(cls, cache_key, component_type, template_path, 
                           rendered_html, render_data, cache_ttl=300):
        """缓存渲染结果
        
        Args:
            cache_key: 缓存键
            component_type: 组件类型
            template_path: 模板路径
            rendered_html: 渲染后的HTML
            render_data: 渲染数据
            cache_ttl: 缓存时间（秒），默认5分钟
            
        Returns:
            ComponentRenderCache: 创建的缓存对象
        """
        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(seconds=cache_ttl)
        
        # 删除现有缓存（如果存在）
        existing_cache = cls.query.filter_by(cache_key=cache_key).first()
        if existing_cache:
            db.session.delete(existing_cache)
        
        # 创建新缓存
        cache_entry = cls(
            cache_key=cache_key,
            component_type=component_type,
            template_path=template_path,
            rendered_html=rendered_html,
            render_data=render_data,
            expires_at=expires_at
        )
        
        db.session.add(cache_entry)
        db.session.commit()
        
        return cache_entry
    
    @classmethod
    def cleanup_expired_cache(cls):
        """清理过期缓存"""
        expired_count = cls.query.filter(cls.expires_at <= datetime.utcnow()).delete()
        db.session.commit()
        return expired_count
    
    @classmethod
    def get_cache_stats(cls):
        """获取缓存统计信息"""
        total_entries = cls.query.count()
        active_entries = cls.query.filter(cls.expires_at > datetime.utcnow()).count()
        total_hits = db.session.query(db.func.sum(cls.hit_count)).scalar() or 0
        
        return {
            'total_entries': total_entries,
            'active_entries': active_entries,
            'expired_entries': total_entries - active_entries,
            'total_hits': total_hits,
            'hit_rate': total_hits / total_entries if total_entries > 0 else 0
        }
    
    def is_expired(self):
        """检查缓存是否已过期"""
        return self.expires_at <= datetime.utcnow()
    
    def extend_expiry(self, additional_seconds=300):
        """延长缓存过期时间"""
        self.expires_at = self.expires_at + timedelta(seconds=additional_seconds)
        db.session.commit()