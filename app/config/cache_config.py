"""
Redis组件缓存配置
用于UI组件渲染结果的缓存管理
"""
import redis
from flask import current_app
import json
import pickle
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, List
import hashlib


class RedisConfig:
    """Redis配置类"""
    
    # 默认配置
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 6379
    DEFAULT_DB = 0
    DEFAULT_PASSWORD = None
    
    # 缓存键前缀
    CACHE_PREFIX = 'kronos_ui:'
    COMPONENT_PREFIX = 'component:'
    RENDER_PREFIX = 'render:'
    USER_PREFIX = 'user:'
    
    # 缓存过期时间（秒）
    DEFAULT_EXPIRE = 3600  # 1小时
    COMPONENT_EXPIRE = 1800  # 30分钟
    RENDER_EXPIRE = 900  # 15分钟
    USER_CACHE_EXPIRE = 7200  # 2小时
    
    @classmethod
    def from_app_config(cls, app_config: Dict[str, Any]) -> Dict[str, Any]:
        """从应用配置创建Redis连接配置"""
        return {
            'host': app_config.get('REDIS_HOST', cls.DEFAULT_HOST),
            'port': app_config.get('REDIS_PORT', cls.DEFAULT_PORT),
            'db': app_config.get('REDIS_DB', cls.DEFAULT_DB),
            'password': app_config.get('REDIS_PASSWORD', cls.DEFAULT_PASSWORD),
            'decode_responses': True,
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True
        }


class ComponentCacheManager:
    """组件缓存管理器"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client or self._create_redis_client()
        self.config = RedisConfig()
    
    def _create_redis_client(self) -> redis.Redis:
        """创建Redis客户端"""
        try:
            redis_config = RedisConfig.from_app_config(current_app.config)
            client = redis.Redis(**redis_config)
            
            # 测试连接
            client.ping()
            current_app.logger.info("Redis连接成功建立")
            
            return client
            
        except Exception as e:
            current_app.logger.error(f"Redis连接失败: {e}")
            # 返回一个假的Redis客户端，用于开发环境
            return FakeRedisClient()
    
    def _make_key(self, prefix: str, identifier: str) -> str:
        """生成缓存键"""
        return f"{self.config.CACHE_PREFIX}{prefix}{identifier}"
    
    def _serialize_data(self, data: Any) -> str:
        """序列化数据"""
        try:
            if isinstance(data, (dict, list, str, int, float, bool)):
                return json.dumps(data, ensure_ascii=False)
            else:
                # 对于复杂对象使用pickle
                return pickle.dumps(data).decode('latin-1')
        except Exception as e:
            current_app.logger.error(f"数据序列化失败: {e}")
            return ""
    
    def _deserialize_data(self, data: str) -> Any:
        """反序列化数据"""
        try:
            # 首先尝试JSON反序列化
            return json.loads(data)
        except (json.JSONDecodeError, ValueError):
            try:
                # 如果JSON失败，尝试pickle
                return pickle.loads(data.encode('latin-1'))
            except Exception as e:
                current_app.logger.error(f"数据反序列化失败: {e}")
                return None
    
    def cache_component_config(self, component_id: str, config_data: Dict[str, Any], 
                             expire: Optional[int] = None) -> bool:
        """缓存组件配置"""
        try:
            key = self._make_key(self.config.COMPONENT_PREFIX, f"config:{component_id}")
            serialized_data = self._serialize_data(config_data)
            
            expire_time = expire or self.config.COMPONENT_EXPIRE
            
            return self.redis_client.setex(key, expire_time, serialized_data)
            
        except Exception as e:
            current_app.logger.error(f"组件配置缓存失败: {e}")
            return False
    
    def get_component_config(self, component_id: str) -> Optional[Dict[str, Any]]:
        """获取组件配置缓存"""
        try:
            key = self._make_key(self.config.COMPONENT_PREFIX, f"config:{component_id}")
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                return self._deserialize_data(cached_data)
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"获取组件配置缓存失败: {e}")
            return None
    
    def cache_render_result(self, component_id: str, render_hash: str, 
                          rendered_html: str, expire: Optional[int] = None) -> bool:
        """缓存组件渲染结果"""
        try:
            key = self._make_key(self.config.RENDER_PREFIX, f"{component_id}:{render_hash}")
            
            cache_data = {
                'html': rendered_html,
                'timestamp': datetime.utcnow().isoformat(),
                'component_id': component_id,
                'render_hash': render_hash
            }
            
            serialized_data = self._serialize_data(cache_data)
            expire_time = expire or self.config.RENDER_EXPIRE
            
            return self.redis_client.setex(key, expire_time, serialized_data)
            
        except Exception as e:
            current_app.logger.error(f"渲染结果缓存失败: {e}")
            return False
    
    def get_render_result(self, component_id: str, render_hash: str) -> Optional[str]:
        """获取缓存的渲染结果"""
        try:
            key = self._make_key(self.config.RENDER_PREFIX, f"{component_id}:{render_hash}")
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                cache_obj = self._deserialize_data(cached_data)
                if cache_obj and isinstance(cache_obj, dict):
                    return cache_obj.get('html')
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"获取渲染结果缓存失败: {e}")
            return None
    
    def cache_user_preferences(self, user_id: int, preferences: Dict[str, Any],
                             expire: Optional[int] = None) -> bool:
        """缓存用户偏好设置"""
        try:
            key = self._make_key(self.config.USER_PREFIX, f"prefs:{user_id}")
            
            cache_data = {
                'preferences': preferences,
                'user_id': user_id,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            serialized_data = self._serialize_data(cache_data)
            expire_time = expire or self.config.USER_CACHE_EXPIRE
            
            return self.redis_client.setex(key, expire_time, serialized_data)
            
        except Exception as e:
            current_app.logger.error(f"用户偏好缓存失败: {e}")
            return False
    
    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户偏好设置缓存"""
        try:
            key = self._make_key(self.config.USER_PREFIX, f"prefs:{user_id}")
            cached_data = self.redis_client.get(key)
            
            if cached_data:
                cache_obj = self._deserialize_data(cached_data)
                if cache_obj and isinstance(cache_obj, dict):
                    return cache_obj.get('preferences')
            
            return None
            
        except Exception as e:
            current_app.logger.error(f"获取用户偏好缓存失败: {e}")
            return None
    
    def generate_render_hash(self, component_id: str, props: Dict[str, Any], 
                           user_context: Optional[Dict[str, Any]] = None) -> str:
        """生成渲染哈希值"""
        hash_input = {
            'component_id': component_id,
            'props': props,
            'user_context': user_context or {}
        }
        
        hash_string = json.dumps(hash_input, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(hash_string.encode('utf-8')).hexdigest()
    
    def invalidate_component_cache(self, component_id: str) -> int:
        """清除组件相关的所有缓存"""
        try:
            # 查找所有相关的键
            config_pattern = self._make_key(self.config.COMPONENT_PREFIX, f"config:{component_id}")
            render_pattern = self._make_key(self.config.RENDER_PREFIX, f"{component_id}:*")
            
            deleted_count = 0
            
            # 删除配置缓存
            if self.redis_client.exists(config_pattern):
                self.redis_client.delete(config_pattern)
                deleted_count += 1
            
            # 删除渲染结果缓存
            render_keys = self.redis_client.keys(render_pattern)
            if render_keys:
                self.redis_client.delete(*render_keys)
                deleted_count += len(render_keys)
            
            current_app.logger.info(f"清除组件 {component_id} 缓存，删除 {deleted_count} 个键")
            return deleted_count
            
        except Exception as e:
            current_app.logger.error(f"清除组件缓存失败: {e}")
            return 0
    
    def invalidate_user_cache(self, user_id: int) -> int:
        """清除用户相关缓存"""
        try:
            pattern = self._make_key(self.config.USER_PREFIX, f"prefs:{user_id}")
            
            if self.redis_client.exists(pattern):
                self.redis_client.delete(pattern)
                current_app.logger.info(f"清除用户 {user_id} 缓存")
                return 1
            
            return 0
            
        except Exception as e:
            current_app.logger.error(f"清除用户缓存失败: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            info = self.redis_client.info()
            
            # 统计不同类型的键数量
            component_keys = len(self.redis_client.keys(
                self._make_key(self.config.COMPONENT_PREFIX, "*")
            ))
            render_keys = len(self.redis_client.keys(
                self._make_key(self.config.RENDER_PREFIX, "*")
            ))
            user_keys = len(self.redis_client.keys(
                self._make_key(self.config.USER_PREFIX, "*")
            ))
            
            return {
                'redis_info': {
                    'used_memory': info.get('used_memory_human', 'Unknown'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0)
                },
                'cache_keys': {
                    'component_configs': component_keys,
                    'render_results': render_keys,
                    'user_preferences': user_keys,
                    'total': component_keys + render_keys + user_keys
                }
            }
            
        except Exception as e:
            current_app.logger.error(f"获取缓存统计失败: {e}")
            return {'error': str(e)}
    
    def clear_all_cache(self) -> int:
        """清除所有应用缓存（谨慎使用）"""
        try:
            pattern = self._make_key('', '*')
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                current_app.logger.warning(f"清除所有缓存，删除 {deleted_count} 个键")
                return deleted_count
            
            return 0
            
        except Exception as e:
            current_app.logger.error(f"清除所有缓存失败: {e}")
            return 0


class FakeRedisClient:
    """用于开发环境的假Redis客户端"""
    
    def __init__(self):
        self._data = {}
        self._expires = {}
    
    def ping(self):
        return True
    
    def setex(self, key: str, expire: int, value: str) -> bool:
        self._data[key] = value
        self._expires[key] = datetime.utcnow() + timedelta(seconds=expire)
        return True
    
    def get(self, key: str) -> Optional[str]:
        if key in self._data:
            # 检查是否过期
            if key in self._expires and datetime.utcnow() > self._expires[key]:
                del self._data[key]
                del self._expires[key]
                return None
            return self._data[key]
        return None
    
    def exists(self, key: str) -> bool:
        return key in self._data
    
    def delete(self, *keys: str) -> int:
        deleted = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                self._expires.pop(key, None)
                deleted += 1
        return deleted
    
    def keys(self, pattern: str) -> List[str]:
        import fnmatch
        return [key for key in self._data.keys() if fnmatch.fnmatch(key, pattern)]
    
    def info(self) -> Dict[str, Any]:
        return {
            'used_memory_human': f"{len(self._data) * 100}B",
            'connected_clients': 1,
            'total_commands_processed': 100
        }


# 全局缓存管理器实例
cache_manager: Optional[ComponentCacheManager] = None


def init_cache_manager(app) -> ComponentCacheManager:
    """初始化缓存管理器"""
    global cache_manager
    
    if cache_manager is None:
        with app.app_context():
            cache_manager = ComponentCacheManager()
    
    return cache_manager


def get_cache_manager() -> ComponentCacheManager:
    """获取缓存管理器实例"""
    global cache_manager
    
    if cache_manager is None:
        cache_manager = ComponentCacheManager()
    
    return cache_manager