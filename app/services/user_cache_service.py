# -*- coding: utf-8 -*-
"""
用户缓存服务
实现用户会话数据和档案数据的缓存策略，优化性能
"""

import json
import pickle
import hashlib
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List
from functools import wraps

from flask import current_app
from werkzeug.local import LocalProxy

# 简单的内存缓存实现（生产环境建议使用Redis）
from collections import OrderedDict
import threading
import time


class MemoryCache:
    """简单的内存缓存实现（开发环境使用）"""
    
    def __init__(self, max_size=1000, default_ttl=300):
        """
        初始化内存缓存
        
        Args:
            max_size: 最大缓存条目数
            default_ttl: 默认过期时间（秒）
        """
        self._cache = OrderedDict()
        self._timestamps = {}
        self._ttls = {}
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Any:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None
            
            # 检查是否过期
            if self._is_expired(key):
                self._remove_key(key)
                return None
            
            # 更新访问顺序（LRU）
            value = self._cache.pop(key)
            self._cache[key] = value
            
            return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        with self._lock:
            # 如果缓存已满，删除最旧的条目
            if len(self._cache) >= self._max_size and key not in self._cache:
                self._evict_oldest()
            
            self._cache[key] = value
            self._timestamps[key] = time.time()
            self._ttls[key] = ttl or self._default_ttl
    
    def delete(self, key: str) -> None:
        """删除缓存项"""
        with self._lock:
            self._remove_key(key)
    
    def clear(self) -> None:
        """清空所有缓存"""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
            self._ttls.clear()
    
    def _is_expired(self, key: str) -> bool:
        """检查缓存项是否过期"""
        if key not in self._timestamps:
            return True
        
        elapsed = time.time() - self._timestamps[key]
        ttl = self._ttls.get(key, self._default_ttl)
        return elapsed > ttl
    
    def _remove_key(self, key: str) -> None:
        """移除缓存项及相关元数据"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        self._ttls.pop(key, None)
    
    def _evict_oldest(self) -> None:
        """驱逐最旧的缓存项"""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._remove_key(oldest_key)


class UserCacheService:
    """用户缓存服务类"""
    
    def __init__(self, app=None):
        """
        初始化用户缓存服务
        
        Args:
            app: Flask应用实例
        """
        self.logger = logging.getLogger(__name__)
        self._cache = None
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化Flask应用配置"""
        # 缓存配置
        app.config.setdefault('USER_CACHE_TYPE', 'memory')  # memory, redis
        app.config.setdefault('USER_CACHE_TTL', 300)  # 5分钟
        app.config.setdefault('USER_SESSION_CACHE_TTL', 600)  # 10分钟
        app.config.setdefault('USER_PROFILE_CACHE_TTL', 1800)  # 30分钟
        app.config.setdefault('USER_CACHE_MAX_SIZE', 1000)
        app.config.setdefault('USER_CACHE_KEY_PREFIX', 'user_cache:')
        
        # 初始化缓存后端
        cache_type = app.config.get('USER_CACHE_TYPE', 'memory')
        
        if cache_type == 'redis':
            self._init_redis_cache(app)
        else:
            self._init_memory_cache(app)
        
        self.logger.info(f"用户缓存服务已初始化，使用 {cache_type} 后端")
    
    def _init_memory_cache(self, app):
        """初始化内存缓存"""
        max_size = app.config.get('USER_CACHE_MAX_SIZE', 1000)
        default_ttl = app.config.get('USER_CACHE_TTL', 300)
        
        self._cache = MemoryCache(max_size=max_size, default_ttl=default_ttl)
    
    def _init_redis_cache(self, app):
        """初始化Redis缓存（需要安装redis库）"""
        try:
            import redis
            
            redis_url = app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            self._cache = redis.Redis.from_url(redis_url, decode_responses=True)
            
            # 测试连接
            self._cache.ping()
            self.logger.info("Redis缓存连接成功")
            
        except ImportError:
            self.logger.warning("Redis库未安装，回退到内存缓存")
            self._init_memory_cache(app)
        except Exception as e:
            self.logger.error(f"Redis连接失败: {str(e)}，回退到内存缓存")
            self._init_memory_cache(app)
    
    def _generate_cache_key(self, category: str, identifier: str) -> str:
        """生成缓存键"""
        prefix = current_app.config.get('USER_CACHE_KEY_PREFIX', 'user_cache:')
        return f"{prefix}{category}:{identifier}"
    
    def _serialize_data(self, data: Any) -> str:
        """序列化数据"""
        try:
            if isinstance(data, (dict, list)):
                return json.dumps(data, default=str)
            else:
                return pickle.dumps(data).hex()
        except Exception as e:
            self.logger.error(f"数据序列化失败: {str(e)}")
            return ""
    
    def _deserialize_data(self, serialized_data: str) -> Any:
        """反序列化数据"""
        try:
            # 尝试JSON反序列化
            return json.loads(serialized_data)
        except (json.JSONDecodeError, ValueError):
            try:
                # 尝试pickle反序列化
                return pickle.loads(bytes.fromhex(serialized_data))
            except Exception as e:
                self.logger.error(f"数据反序列化失败: {str(e)}")
                return None
    
    # ===== 用户基础信息缓存 =====
    
    def cache_user_info(self, user_id: int, user_data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """缓存用户基础信息"""
        try:
            key = self._generate_cache_key('user_info', str(user_id))
            ttl = ttl or current_app.config.get('USER_CACHE_TTL', 300)
            
            # 添加缓存时间戳
            cache_data = {
                **user_data,
                '_cached_at': datetime.now(timezone.utc).isoformat(),
                '_cache_ttl': ttl
            }
            
            if hasattr(self._cache, 'set') and hasattr(self._cache, 'get'):
                # Redis缓存
                serialized_data = self._serialize_data(cache_data)
                self._cache.setex(key, ttl, serialized_data)
            else:
                # 内存缓存
                self._cache.set(key, cache_data, ttl)
            
            self.logger.debug(f"用户信息已缓存: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"缓存用户信息失败: {str(e)}")
    
    def get_cached_user_info(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户基础信息"""
        try:
            key = self._generate_cache_key('user_info', str(user_id))
            
            if hasattr(self._cache, 'set') and hasattr(self._cache, 'get'):
                # Redis缓存
                serialized_data = self._cache.get(key)
                if serialized_data:
                    return self._deserialize_data(serialized_data)
            else:
                # 内存缓存
                return self._cache.get(key)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取缓存用户信息失败: {str(e)}")
            return None
    
    def invalidate_user_info(self, user_id: int) -> None:
        """使用户基础信息缓存失效"""
        try:
            key = self._generate_cache_key('user_info', str(user_id))
            
            if hasattr(self._cache, 'delete'):
                self._cache.delete(key)
            else:
                self._cache.delete(key)
            
            self.logger.debug(f"用户信息缓存已失效: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"用户信息缓存失效操作失败: {str(e)}")
    
    # ===== 用户会话缓存 =====
    
    def cache_user_session(self, session_token: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """缓存用户会话数据"""
        try:
            # 对session token进行哈希处理，避免直接暴露
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()[:16]
            key = self._generate_cache_key('session', token_hash)
            
            ttl = ttl or current_app.config.get('USER_SESSION_CACHE_TTL', 600)
            
            cache_data = {
                **session_data,
                '_cached_at': datetime.now(timezone.utc).isoformat(),
                '_cache_ttl': ttl
            }
            
            if hasattr(self._cache, 'setex'):
                # Redis缓存
                serialized_data = self._serialize_data(cache_data)
                self._cache.setex(key, ttl, serialized_data)
            else:
                # 内存缓存
                self._cache.set(key, cache_data, ttl)
            
            self.logger.debug(f"用户会话已缓存: token_hash={token_hash}")
            
        except Exception as e:
            self.logger.error(f"缓存用户会话失败: {str(e)}")
    
    def get_cached_user_session(self, session_token: str) -> Optional[Dict[str, Any]]:
        """获取缓存的用户会话数据"""
        try:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()[:16]
            key = self._generate_cache_key('session', token_hash)
            
            if hasattr(self._cache, 'get'):
                # Redis缓存
                serialized_data = self._cache.get(key)
                if serialized_data:
                    return self._deserialize_data(serialized_data)
            else:
                # 内存缓存
                return self._cache.get(key)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取缓存用户会话失败: {str(e)}")
            return None
    
    def invalidate_user_session(self, session_token: str) -> None:
        """使用户会话缓存失效"""
        try:
            token_hash = hashlib.sha256(session_token.encode()).hexdigest()[:16]
            key = self._generate_cache_key('session', token_hash)
            
            self._cache.delete(key)
            self.logger.debug(f"用户会话缓存已失效: token_hash={token_hash}")
            
        except Exception as e:
            self.logger.error(f"用户会话缓存失效操作失败: {str(e)}")
    
    # ===== 用户档案缓存 =====
    
    def cache_user_profile(self, user_id: int, profile_data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """缓存用户档案数据"""
        try:
            key = self._generate_cache_key('profile', str(user_id))
            ttl = ttl or current_app.config.get('USER_PROFILE_CACHE_TTL', 1800)
            
            cache_data = {
                **profile_data,
                '_cached_at': datetime.now(timezone.utc).isoformat(),
                '_cache_ttl': ttl
            }
            
            if hasattr(self._cache, 'setex'):
                # Redis缓存
                serialized_data = self._serialize_data(cache_data)
                self._cache.setex(key, ttl, serialized_data)
            else:
                # 内存缓存
                self._cache.set(key, cache_data, ttl)
            
            self.logger.debug(f"用户档案已缓存: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"缓存用户档案失败: {str(e)}")
    
    def get_cached_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户档案数据"""
        try:
            key = self._generate_cache_key('profile', str(user_id))
            
            if hasattr(self._cache, 'get'):
                # Redis缓存
                serialized_data = self._cache.get(key)
                if serialized_data:
                    return self._deserialize_data(serialized_data)
            else:
                # 内存缓存
                return self._cache.get(key)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取缓存用户档案失败: {str(e)}")
            return None
    
    def invalidate_user_profile(self, user_id: int) -> None:
        """使用户档案缓存失效"""
        try:
            key = self._generate_cache_key('profile', str(user_id))
            
            self._cache.delete(key)
            self.logger.debug(f"用户档案缓存已失效: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"用户档案缓存失效操作失败: {str(e)}")
    
    # ===== 用户关注列表缓存 =====
    
    def cache_user_watchlist(self, user_id: int, watchlist_data: List[Dict[str, Any]], ttl: Optional[int] = None) -> None:
        """缓存用户关注列表"""
        try:
            key = self._generate_cache_key('watchlist', str(user_id))
            ttl = ttl or current_app.config.get('USER_CACHE_TTL', 300)
            
            cache_data = {
                'watchlist': watchlist_data,
                'count': len(watchlist_data),
                '_cached_at': datetime.now(timezone.utc).isoformat(),
                '_cache_ttl': ttl
            }
            
            if hasattr(self._cache, 'setex'):
                # Redis缓存
                serialized_data = self._serialize_data(cache_data)
                self._cache.setex(key, ttl, serialized_data)
            else:
                # 内存缓存
                self._cache.set(key, cache_data, ttl)
            
            self.logger.debug(f"用户关注列表已缓存: user_id={user_id}, count={len(watchlist_data)}")
            
        except Exception as e:
            self.logger.error(f"缓存用户关注列表失败: {str(e)}")
    
    def get_cached_user_watchlist(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取缓存的用户关注列表"""
        try:
            key = self._generate_cache_key('watchlist', str(user_id))
            
            if hasattr(self._cache, 'get'):
                # Redis缓存
                serialized_data = self._cache.get(key)
                if serialized_data:
                    return self._deserialize_data(serialized_data)
            else:
                # 内存缓存
                return self._cache.get(key)
            
            return None
            
        except Exception as e:
            self.logger.error(f"获取缓存用户关注列表失败: {str(e)}")
            return None
    
    def invalidate_user_watchlist(self, user_id: int) -> None:
        """使用户关注列表缓存失效"""
        try:
            key = self._generate_cache_key('watchlist', str(user_id))
            
            self._cache.delete(key)
            self.logger.debug(f"用户关注列表缓存已失效: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"用户关注列表缓存失效操作失败: {str(e)}")
    
    # ===== 缓存统计和管理 =====
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        try:
            if hasattr(self._cache, 'info'):
                # Redis缓存统计
                redis_info = self._cache.info()
                return {
                    'type': 'redis',
                    'used_memory': redis_info.get('used_memory_human', 'N/A'),
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0)
                }
            else:
                # 内存缓存统计
                return {
                    'type': 'memory',
                    'cache_size': len(self._cache._cache),
                    'max_size': self._cache._max_size,
                    'default_ttl': self._cache._default_ttl
                }
                
        except Exception as e:
            self.logger.error(f"获取缓存统计失败: {str(e)}")
            return {'type': 'unknown', 'error': str(e)}
    
    def clear_all_cache(self) -> None:
        """清空所有用户缓存"""
        try:
            if hasattr(self._cache, 'flushdb'):
                # Redis缓存
                self._cache.flushdb()
            else:
                # 内存缓存
                self._cache.clear()
            
            self.logger.info("所有用户缓存已清空")
            
        except Exception as e:
            self.logger.error(f"清空缓存失败: {str(e)}")
    
    def invalidate_user_all_cache(self, user_id: int) -> None:
        """使指定用户的所有缓存失效"""
        try:
            # 清理用户相关的所有缓存
            self.invalidate_user_info(user_id)
            self.invalidate_user_profile(user_id)
            self.invalidate_user_watchlist(user_id)
            
            self.logger.info(f"用户 {user_id} 的所有缓存已失效")
            
        except Exception as e:
            self.logger.error(f"用户缓存失效操作失败: {str(e)}")


# 创建全局缓存服务实例
user_cache_service = UserCacheService()


def cached_user_method(cache_key_func=None, ttl=None, cache_category='user_info'):
    """
    用户方法缓存装饰器
    
    Args:
        cache_key_func: 缓存键生成函数
        ttl: 缓存时间
        cache_category: 缓存类别
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 尝试从缓存获取
            key = user_cache_service._generate_cache_key(cache_category, cache_key)
            
            if hasattr(user_cache_service._cache, 'get'):
                cached_result = user_cache_service._cache.get(key)
                if cached_result:
                    return user_cache_service._deserialize_data(cached_result)
            else:
                cached_result = user_cache_service._cache.get(key)
                if cached_result is not None:
                    return cached_result
            
            # 缓存未命中，执行原函数
            result = func(*args, **kwargs)
            
            # 缓存结果
            cache_ttl = ttl or current_app.config.get('USER_CACHE_TTL', 300)
            
            if hasattr(user_cache_service._cache, 'setex'):
                serialized_result = user_cache_service._serialize_data(result)
                user_cache_service._cache.setex(key, cache_ttl, serialized_result)
            else:
                user_cache_service._cache.set(key, result, cache_ttl)
            
            return result
        
        return wrapper
    return decorator


def init_user_cache_service(app):
    """初始化用户缓存服务"""
    user_cache_service.init_app(app)
    return user_cache_service