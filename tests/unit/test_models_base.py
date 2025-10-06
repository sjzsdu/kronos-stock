"""
数据模型单元测试基类

为UI系统增强功能的数据模型提供测试基础设施。
"""
import pytest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, UIComponentConfig, ComponentRenderCache, PerformanceMetrics, UserUIPreferences, ComponentUsageStats
import tempfile
import os


class ModelsTestBase:
    """模型测试基类"""
    
    @pytest.fixture(autouse=True)
    def setup_test_app(self):
        """设置测试应用环境"""
        # 创建临时数据库文件
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # 创建测试应用
        self.app = create_app('testing')
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['TESTING'] = True
        
        # 设置应用上下文
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 创建数据库表
        db.create_all()
        
        yield
        
        # 清理
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def create_test_ui_config(self, **kwargs):
        """创建测试用UI配置"""
        default_data = {
            'component_name': 'test_button',
            'component_type': 'button',
            'config_data': {'theme': 'primary', 'size': 'medium'}
        }
        default_data.update(kwargs)
        
        config = UIComponentConfig(**default_data)
        db.session.add(config)
        db.session.commit()
        return config
    
    def create_test_cache(self, **kwargs):
        """创建测试用渲染缓存"""
        default_data = {
            'cache_key': 'test_cache_key',
            'component_type': 'button',
            'template_path': 'components/button.html',
            'rendered_html': '<button class="btn btn-primary">测试</button>',
            'ttl_seconds': 300
        }
        default_data.update(kwargs)
        
        cache = ComponentRenderCache(**default_data)
        db.session.add(cache)
        db.session.commit()
        return cache
    
    def create_test_performance_metric(self, **kwargs):
        """创建测试用性能指标"""
        default_data = {
            'session_id': 'test_session_123',
            'metric_type': 'page_load',
            'metric_name': 'dashboard_load_time',
            'metric_value': 1250.5,
            'metric_unit': 'ms'
        }
        default_data.update(kwargs)
        
        metric = PerformanceMetrics(**default_data)
        db.session.add(metric)
        db.session.commit()
        return metric
    
    def create_test_user_preference(self, **kwargs):
        """创建测试用用户偏好"""
        default_data = {
            'user_id': 1,
            'preference_category': 'theme',
            'preference_key': 'color_scheme',
            'preference_value': 'dark',
            'value_type': 'string'
        }
        default_data.update(kwargs)
        
        preference = UserUIPreferences(**default_data)
        db.session.add(preference)
        db.session.commit()
        return preference
    
    def create_test_usage_stat(self, **kwargs):
        """创建测试用组件使用统计"""
        default_data = {
            'session_id': 'test_session_456',
            'component_name': 'login_form',
            'component_type': 'form',
            'action_type': 'submit',
            'success': True
        }
        default_data.update(kwargs)
        
        stat = ComponentUsageStats(**default_data)
        db.session.add(stat)
        db.session.commit()
        return stat


class TestUIComponentConfig(ModelsTestBase):
    """UI组件配置模型测试"""
    
    def test_create_ui_config(self):
        """测试创建UI组件配置"""
        config = self.create_test_ui_config()
        
        assert config.id is not None
        assert config.component_name == 'test_button'
        assert config.component_type == 'button'
        assert config.config_data == {'theme': 'primary', 'size': 'medium'}
        assert config.is_active is True
        assert config.version == 1
        assert config.created_at is not None
    
    def test_to_dict(self):
        """测试转换为字典格式"""
        config = self.create_test_ui_config()
        data = config.to_dict()
        
        assert 'id' in data
        assert data['component_name'] == 'test_button'
        assert data['component_type'] == 'button'
        assert data['config_data'] == {'theme': 'primary', 'size': 'medium'}
        assert data['is_active'] is True
    
    def test_get_user_config(self):
        """测试获取用户配置"""
        config = self.create_test_ui_config(user_id=1, component_name='user_button')
        
        found_config = UIComponentConfig.get_user_config(1, 'user_button')
        assert found_config is not None
        assert found_config.id == config.id
        
        not_found = UIComponentConfig.get_user_config(2, 'user_button')
        assert not_found is None
    
    def test_get_global_config(self):
        """测试获取全局配置"""
        config = self.create_test_ui_config(user_id=None, component_name='global_button')
        
        found_config = UIComponentConfig.get_global_config('global_button')
        assert found_config is not None
        assert found_config.id == config.id
    
    def test_get_effective_config(self):
        """测试获取有效配置（用户优先于全局）"""
        # 创建全局配置
        global_config = self.create_test_ui_config(
            user_id=None,
            component_name='priority_test',
            config_data={'theme': 'default'}
        )
        
        # 创建用户配置
        user_config = self.create_test_ui_config(
            user_id=1,
            component_name='priority_test',
            config_data={'theme': 'custom'}
        )
        
        # 有用户ID时应返回用户配置
        effective = UIComponentConfig.get_effective_config('priority_test', user_id=1)
        assert effective.id == user_config.id
        assert effective.config_data['theme'] == 'custom'
        
        # 无用户ID时应返回全局配置
        effective = UIComponentConfig.get_effective_config('priority_test')
        assert effective.id == global_config.id
        assert effective.config_data['theme'] == 'default'
    
    def test_validate_config_data(self):
        """测试配置数据验证"""
        # 有效配置
        valid_config = self.create_test_ui_config()
        assert valid_config.validate_config_data() is True
        
        # 无效组件类型
        invalid_type_config = UIComponentConfig(
            component_name='test',
            component_type='invalid_type',
            config_data={}
        )
        assert invalid_type_config.validate_config_data() is False
        
        # 无效组件名称
        invalid_name_config = UIComponentConfig(
            component_name='invalid name with spaces',
            component_type='button',
            config_data={}
        )
        assert invalid_name_config.validate_config_data() is False


class TestComponentRenderCache(ModelsTestBase):
    """组件渲染缓存模型测试"""
    
    def test_create_cache(self):
        """测试创建缓存"""
        cache = self.create_test_cache()
        
        assert cache.id is not None
        assert cache.cache_key == 'test_cache_key'
        assert cache.component_type == 'button'
        assert cache.hit_count == 0
        assert cache.expires_at > datetime.utcnow()
    
    def test_generate_cache_key(self):
        """测试缓存键生成"""
        key1 = ComponentRenderCache.generate_cache_key(
            'button',
            'components/button.html',
            {'theme': 'primary'}
        )
        
        key2 = ComponentRenderCache.generate_cache_key(
            'button',
            'components/button.html',
            {'theme': 'primary'}
        )
        
        # 相同参数应生成相同的key
        assert key1 == key2
        
        key3 = ComponentRenderCache.generate_cache_key(
            'button',
            'components/button.html',
            {'theme': 'secondary'}
        )
        
        # 不同参数应生成不同的key
        assert key1 != key3
    
    def test_cache_operations(self):
        """测试缓存操作"""
        cache_key = 'test_operations_key'
        
        # 设置缓存
        cache = ComponentRenderCache.set_cache(
            cache_key=cache_key,
            component_type='button',
            template_path='test.html',
            rendered_html='<button>test</button>',
            ttl_seconds=300
        )
        
        assert cache is not None
        
        # 获取缓存
        retrieved = ComponentRenderCache.get_cached(cache_key)
        assert retrieved is not None
        assert retrieved.hit_count == 1
        
        # 再次获取，命中次数增加
        retrieved_again = ComponentRenderCache.get_cached(cache_key)
        assert retrieved_again.hit_count == 2
    
    def test_cache_expiration(self):
        """测试缓存过期"""
        # 创建已过期的缓存
        expired_cache = ComponentRenderCache(
            cache_key='expired_key',
            component_type='button',
            template_path='test.html',
            rendered_html='<button>test</button>',
            ttl_seconds=-1  # 立即过期
        )
        db.session.add(expired_cache)
        db.session.commit()
        
        # 尝试获取过期缓存应该返回None
        retrieved = ComponentRenderCache.get_cached('expired_key')
        assert retrieved is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])