# -*- coding: utf-8 -*-
"""
速率限制配置
提供API接口和用户操作的速率限制功能
防止恶意攻击和资源滥用
"""

from flask import request, jsonify, g, current_app
from functools import wraps
import time
import json
import hashlib
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple, Optional
import threading


class RateLimiter:
    """
    速率限制器类
    实现基于IP、用户、API端点的速率限制
    """
    
    def __init__(self, app=None):
        """
        初始化速率限制器
        
        Args:
            app: Flask应用实例
        """
        self.app = app
        self.storage = defaultdict(list)  # 存储访问记录 {key: [(timestamp, count), ...]}
        self.lock = threading.RLock()  # 线程安全锁
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        初始化Flask应用
        
        Args:
            app: Flask应用实例
        """
        # 设置默认配置
        app.config.setdefault('RATE_LIMIT_ENABLED', True)
        app.config.setdefault('RATE_LIMIT_STORAGE_URL', None)  # Redis URL，None表示使用内存
        app.config.setdefault('RATE_LIMIT_STRATEGY', 'sliding-window')  # 滑动窗口策略
        
        # 默认速率限制规则
        app.config.setdefault('RATE_LIMIT_RULES', {
            # 登录相关 - 5次/分钟
            'auth.login': {'limit': 5, 'window': 60, 'per': 'ip'},
            'auth.register': {'limit': 3, 'window': 60, 'per': 'ip'},
            'auth.forgot_password': {'limit': 3, 'window': 300, 'per': 'ip'},  # 5分钟
            'auth.reset_password': {'limit': 5, 'window': 300, 'per': 'ip'},
            
            # API接口 - 60次/分钟
            'api.predict': {'limit': 10, 'window': 60, 'per': 'user'},  # 预测接口限制更严格
            'api.stock_data': {'limit': 60, 'window': 60, 'per': 'user'},
            'api.model_list': {'limit': 100, 'window': 60, 'per': 'user'},
            
            # 管理操作 - 20次/分钟
            'admin.user_management': {'limit': 20, 'window': 60, 'per': 'user'},
            'admin.system_settings': {'limit': 10, 'window': 60, 'per': 'user'},
            
            # 文件上传 - 5次/分钟
            'upload.file': {'limit': 5, 'window': 60, 'per': 'user'},
            
            # 默认规则 - 100次/分钟
            'default': {'limit': 100, 'window': 60, 'per': 'ip'}
        })
        
        # 注册错误处理器
        @app.errorhandler(429)
        def rate_limit_handler(error):
            """处理速率限制错误"""
            return jsonify({
                'error': '请求过于频繁',
                'message': '您的请求速度过快，请稍后再试',
                'code': 'RATE_LIMIT_EXCEEDED',
                'retry_after': getattr(error, 'retry_after', 60)
            }), 429
        
        # 注册清理任务
        @app.cli.command('cleanup-rate-limits')
        def cleanup_rate_limits():
            """清理过期的速率限制记录"""
            self.cleanup_expired_records()
        
        current_app.logger.info("速率限制器已初始化")
    
    def limit(self, rule_name: str = None, limit: int = None, window: int = None, 
              per: str = None, error_message: str = None):
        """
        速率限制装饰器
        
        Args:
            rule_name: 规则名称，用于查找预定义规则
            limit: 限制次数
            window: 时间窗口（秒）
            per: 限制维度 ('ip', 'user', 'endpoint')
            error_message: 自定义错误消息
        
        Returns:
            装饰器函数
        """
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                    return f(*args, **kwargs)
                
                # 获取速率限制规则
                rule = self._get_rate_limit_rule(rule_name, limit, window, per)
                if not rule:
                    return f(*args, **kwargs)
                
                # 检查速率限制
                key = self._generate_rate_limit_key(rule['per'], rule_name)
                allowed, retry_after = self._check_rate_limit(key, rule['limit'], rule['window'])
                
                if not allowed:
                    current_app.logger.warning(f"速率限制触发: {key}, 规则: {rule}")
                    
                    # 返回限制错误
                    error_response = {
                        'error': '请求过于频繁',
                        'message': error_message or f"每{rule['window']}秒最多允许{rule['limit']}次请求",
                        'code': 'RATE_LIMIT_EXCEEDED',
                        'retry_after': retry_after
                    }
                    
                    # 如果是API请求，返回JSON
                    if request.is_json or request.path.startswith('/api/'):
                        response = jsonify(error_response)
                        response.status_code = 429
                        response.headers['Retry-After'] = str(retry_after)
                        return response
                    else:
                        # Web页面请求，可以重定向到错误页面或返回HTML
                        from flask import abort
                        abort(429)
                
                # 记录访问
                self._record_access(key)
                
                return f(*args, **kwargs)
            
            return decorated_function
        return decorator
    
    def _get_rate_limit_rule(self, rule_name: str = None, limit: int = None, 
                           window: int = None, per: str = None) -> Optional[Dict]:
        """
        获取速率限制规则
        
        Args:
            rule_name: 规则名称
            limit: 限制次数
            window: 时间窗口
            per: 限制维度
            
        Returns:
            规则配置字典
        """
        rules = current_app.config.get('RATE_LIMIT_RULES', {})
        
        # 优先使用传入的参数
        if limit is not None and window is not None:
            return {
                'limit': limit,
                'window': window,
                'per': per or 'ip'
            }
        
        # 使用规则名称查找
        if rule_name and rule_name in rules:
            return rules[rule_name]
        
        # 根据端点自动匹配规则
        endpoint = request.endpoint or 'unknown'
        
        # 精确匹配
        if endpoint in rules:
            return rules[endpoint]
        
        # 模糊匹配
        for pattern, rule in rules.items():
            if pattern != 'default' and pattern in endpoint:
                return rule
        
        # 使用默认规则
        return rules.get('default')
    
    def _generate_rate_limit_key(self, per: str, rule_name: str = None) -> str:
        """
        生成速率限制的键
        
        Args:
            per: 限制维度
            rule_name: 规则名称
            
        Returns:
            限制键字符串
        """
        parts = ['rate_limit']
        
        # 添加规则标识
        if rule_name:
            parts.append(rule_name)
        else:
            parts.append(request.endpoint or 'unknown')
        
        # 根据维度添加标识符
        if per == 'ip':
            parts.append(f"ip_{self._get_client_ip()}")
        elif per == 'user':
            user_id = self._get_current_user_id()
            if user_id:
                parts.append(f"user_{user_id}")
            else:
                # 未登录用户使用IP
                parts.append(f"ip_{self._get_client_ip()}")
        elif per == 'endpoint':
            parts.append(f"endpoint_{request.endpoint or 'unknown'}")
        else:
            # 默认使用IP
            parts.append(f"ip_{self._get_client_ip()}")
        
        return ':'.join(parts)
    
    def _get_client_ip(self) -> str:
        """
        获取客户端IP地址
        
        Returns:
            IP地址字符串
        """
        # 优先获取代理转发的真实IP
        forwarded_ips = request.headers.getlist('X-Forwarded-For')
        if forwarded_ips:
            return forwarded_ips[0].split(',')[0].strip()
        
        # 获取其他代理头
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # 使用远程地址
        return request.remote_addr or 'unknown'
    
    def _get_current_user_id(self) -> Optional[int]:
        """
        获取当前用户ID
        
        Returns:
            用户ID，未登录时返回None
        """
        # 从g对象获取
        if hasattr(g, 'current_user_id') and g.current_user_id:
            return g.current_user_id
        
        # 从session获取
        from flask import session
        return session.get('user_id')
    
    def _check_rate_limit(self, key: str, limit: int, window: int) -> Tuple[bool, int]:
        """
        检查是否超过速率限制
        
        Args:
            key: 限制键
            limit: 限制次数
            window: 时间窗口（秒）
            
        Returns:
            (是否允许, 重试间隔秒数)
        """
        with self.lock:
            now = time.time()
            window_start = now - window
            
            # 获取当前记录
            records = self.storage.get(key, [])
            
            # 清理过期记录
            valid_records = [(timestamp, count) for timestamp, count in records 
                           if timestamp > window_start]
            
            # 计算当前窗口内的访问次数
            total_count = sum(count for _, count in valid_records)
            
            # 检查是否超限
            if total_count >= limit:
                # 计算最早记录的剩余时间
                if valid_records:
                    earliest_timestamp = min(timestamp for timestamp, _ in valid_records)
                    retry_after = max(1, int(window - (now - earliest_timestamp)))
                else:
                    retry_after = window
                
                return False, retry_after
            
            # 更新存储
            self.storage[key] = valid_records
            
            return True, 0
    
    def _record_access(self, key: str):
        """
        记录访问
        
        Args:
            key: 限制键
        """
        with self.lock:
            now = time.time()
            
            # 添加新记录
            records = self.storage.get(key, [])
            records.append((now, 1))
            self.storage[key] = records
    
    def cleanup_expired_records(self):
        """
        清理过期的速率限制记录
        """
        with self.lock:
            now = time.time()
            expired_keys = []
            
            for key, records in self.storage.items():
                # 保留最近1小时的记录
                valid_records = [(timestamp, count) for timestamp, count in records 
                               if now - timestamp < 3600]
                
                if valid_records:
                    self.storage[key] = valid_records
                else:
                    expired_keys.append(key)
            
            # 删除空记录
            for key in expired_keys:
                del self.storage[key]
            
            current_app.logger.info(f"清理速率限制记录: 删除 {len(expired_keys)} 个过期键")
    
    def get_rate_limit_status(self, rule_name: str = None) -> Dict:
        """
        获取当前的速率限制状态
        
        Args:
            rule_name: 规则名称
            
        Returns:
            速率限制状态信息
        """
        rule = self._get_rate_limit_rule(rule_name)
        if not rule:
            return {'error': '未找到对应规则'}
        
        key = self._generate_rate_limit_key(rule['per'], rule_name)
        
        with self.lock:
            now = time.time()
            window_start = now - rule['window']
            
            records = self.storage.get(key, [])
            valid_records = [(timestamp, count) for timestamp, count in records 
                           if timestamp > window_start]
            
            current_count = sum(count for _, count in valid_records)
            remaining = max(0, rule['limit'] - current_count)
            
            return {
                'limit': rule['limit'],
                'window': rule['window'],
                'current': current_count,
                'remaining': remaining,
                'reset_time': int(now + rule['window']) if valid_records else int(now)
            }


# 全局速率限制器实例
rate_limiter = RateLimiter()


def init_rate_limiter(app):
    """
    初始化速率限制器
    
    Args:
        app: Flask应用实例
    """
    rate_limiter.init_app(app)


# 常用装饰器
def rate_limit_login(f):
    """登录接口速率限制装饰器"""
    return rate_limiter.limit('auth.login')(f)


def rate_limit_api(f):
    """API接口速率限制装饰器"""
    return rate_limiter.limit('api.default', limit=60, window=60, per='user')(f)


def rate_limit_prediction(f):
    """预测接口速率限制装饰器"""
    return rate_limiter.limit('api.predict')(f)


def rate_limit_upload(f):
    """文件上传速率限制装饰器"""
    return rate_limiter.limit('upload.file')(f)


def rate_limit_admin(f):
    """管理操作速率限制装饰器"""
    return rate_limiter.limit('admin.user_management')(f)


# 自定义速率限制装饰器
def rate_limit(limit: int, window: int = 60, per: str = 'ip', message: str = None):
    """
    自定义速率限制装饰器
    
    Args:
        limit: 限制次数
        window: 时间窗口（秒）
        per: 限制维度
        message: 错误消息
        
    Returns:
        装饰器函数
    """
    return rate_limiter.limit(limit=limit, window=window, per=per, error_message=message)


# 实用工具函数
def get_rate_limit_status(rule_name: str = None) -> Dict:
    """
    获取速率限制状态
    
    Args:
        rule_name: 规则名称
        
    Returns:
        状态信息字典
    """
    return rate_limiter.get_rate_limit_status(rule_name)


def cleanup_rate_limit_records():
    """
    清理速率限制记录
    """
    rate_limiter.cleanup_expired_records()