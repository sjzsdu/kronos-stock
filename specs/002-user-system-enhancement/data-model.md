# 用户系统优化 - 数据模型设计

## 概述

本文档定义了用户系统优化功能的数据模型，包括现有实体的扩展和新增实体的设计。基于现有Flask+SQLAlchemy架构进行增量设计。

## 核心实体

### 1. UI组件配置 (UIComponentConfig)

#### 实体描述
存储UI组件的配置信息，支持组件个性化和主题定制。

#### 字段定义
```python
class UIComponentConfig(db.Model):
    __tablename__ = 'ui_component_configs'
    
    id = db.Column(db.Integer, primary_key=True, comment='配置ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID，空表示全局配置')
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    component_type = db.Column(db.String(50), nullable=False, comment='组件类型')
    config_data = db.Column(db.JSON, nullable=False, comment='配置数据JSON')
    is_active = db.Column(db.Boolean, default=True, comment='是否启用')
    version = db.Column(db.Integer, default=1, comment='配置版本')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='ui_configs')
    
    # 索引
    __table_args__ = (
        db.Index('idx_ui_config_user_component', 'user_id', 'component_name'),
        db.Index('idx_ui_config_type', 'component_type'),
    )
```

#### 验证规则
- `component_name`: 必填，长度1-100字符，仅允许字母、数字、下划线、连字符
- `component_type`: 必填，限定值范围：['form', 'button', 'card', 'navigation', 'modal', 'notification']
- `config_data`: 必填，有效JSON格式，大小限制10KB
- 用户级配置优先于全局配置

#### 状态迁移
```
创建 -> 激活 -> 更新 -> 停用 -> 删除
       |  ^         |
       |  |---------|
```

### 2. 组件渲染缓存 (ComponentRenderCache)

#### 实体描述
缓存组件渲染结果，提升页面加载性能。

#### 字段定义
```python
class ComponentRenderCache(db.Model):
    __tablename__ = 'component_render_cache'
    
    id = db.Column(db.Integer, primary_key=True, comment='缓存ID')
    cache_key = db.Column(db.String(255), unique=True, nullable=False, comment='缓存键')
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    render_data = db.Column(db.Text, nullable=False, comment='渲染数据')
    content_hash = db.Column(db.String(64), nullable=False, comment='内容哈希值')
    expires_at = db.Column(db.DateTime, nullable=False, comment='过期时间')
    hit_count = db.Column(db.Integer, default=0, comment='命中次数')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow, comment='最后访问时间')
    
    # 索引
    __table_args__ = (
        db.Index('idx_cache_key', 'cache_key'),
        db.Index('idx_cache_component', 'component_name'),
        db.Index('idx_cache_expires', 'expires_at'),
    )
```

#### 验证规则
- `cache_key`: 必填，唯一，长度1-255字符
- `render_data`: 必填，HTML内容，大小限制100KB
- `expires_at`: 必填，不能早于当前时间
- 缓存TTL策略：组件类型决定（表单:5min，卡片:30min，导航:2h）

### 3. 性能监控记录 (PerformanceMetrics)

#### 实体描述
记录系统性能指标，用于监控和优化分析。

#### 字段定义
```python
class PerformanceMetrics(db.Model):
    __tablename__ = 'performance_metrics'
    
    id = db.Column(db.Integer, primary_key=True, comment='记录ID')
    metric_type = db.Column(db.String(50), nullable=False, comment='指标类型')
    endpoint = db.Column(db.String(200), nullable=True, comment='API端点')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    response_time = db.Column(db.Float, nullable=False, comment='响应时间(ms)')
    memory_usage = db.Column(db.Float, nullable=True, comment='内存使用(MB)')
    db_queries = db.Column(db.Integer, nullable=True, comment='数据库查询次数')
    cache_hits = db.Column(db.Integer, default=0, comment='缓存命中次数')
    cache_misses = db.Column(db.Integer, default=0, comment='缓存未命中次数')
    error_count = db.Column(db.Integer, default=0, comment='错误次数')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment='记录时间')
    
    # 关联关系
    user = db.relationship('User', backref='performance_records')
    
    # 索引
    __table_args__ = (
        db.Index('idx_perf_type_time', 'metric_type', 'timestamp'),
        db.Index('idx_perf_endpoint', 'endpoint'),
        db.Index('idx_perf_user_time', 'user_id', 'timestamp'),
    )
```

#### 验证规则
- `metric_type`: 必填，限定值：['page_load', 'api_response', 'component_render', 'user_action']
- `response_time`: 必填，大于0的浮点数
- `endpoint`: 可选，但当metric_type为'api_response'时必填
- 数据保留期：30天，超期自动清理

### 4. 用户界面偏好 (UserUIPreferences)

#### 实体描述
扩展现有User模型，存储用户UI个性化偏好设置。

#### 字段定义
```python
class UserUIPreferences(db.Model):
    __tablename__ = 'user_ui_preferences'
    
    id = db.Column(db.Integer, primary_key=True, comment='偏好ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    theme = db.Column(db.String(20), default='default', comment='主题')
    language = db.Column(db.String(10), default='zh-cn', comment='语言')
    timezone = db.Column(db.String(50), default='Asia/Shanghai', comment='时区')
    layout_density = db.Column(db.String(20), default='comfortable', comment='布局密度')
    sidebar_collapsed = db.Column(db.Boolean, default=False, comment='侧边栏是否折叠')
    notification_settings = db.Column(db.JSON, comment='通知设置')
    dashboard_layout = db.Column(db.JSON, comment='仪表板布局配置')
    accessibility_settings = db.Column(db.JSON, comment='无障碍设置')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref=db.backref('ui_preferences', uselist=False))
    
    # 索引
    __table_args__ = (
        db.Index('idx_ui_pref_user', 'user_id'),
    )
```

#### 验证规则
- `theme`: 限定值：['default', 'dark', 'light', 'auto']
- `language`: 限定值：['zh-cn', 'en-us']
- `layout_density`: 限定值：['compact', 'comfortable', 'spacious']
- `notification_settings`: JSON格式，包含email, push, in_app开关
- `dashboard_layout`: JSON格式，存储组件位置和大小配置

### 5. 组件使用统计 (ComponentUsageStats)

#### 实体描述
统计组件使用情况，用于优化决策和用户体验分析。

#### 字段定义
```python
class ComponentUsageStats(db.Model):
    __tablename__ = 'component_usage_stats'
    
    id = db.Column(db.Integer, primary_key=True, comment='统计ID')
    component_name = db.Column(db.String(100), nullable=False, comment='组件名称')
    action_type = db.Column(db.String(50), nullable=False, comment='操作类型')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, comment='用户ID')
    session_id = db.Column(db.String(100), nullable=True, comment='会话ID')
    page_url = db.Column(db.String(500), nullable=True, comment='页面URL')
    device_type = db.Column(db.String(20), nullable=True, comment='设备类型')
    browser = db.Column(db.String(50), nullable=True, comment='浏览器')
    interaction_data = db.Column(db.JSON, comment='交互数据')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, comment='记录时间')
    
    # 关联关系
    user = db.relationship('User', backref='usage_stats')
    
    # 索引
    __table_args__ = (
        db.Index('idx_usage_component_time', 'component_name', 'timestamp'),
        db.Index('idx_usage_user_time', 'user_id', 'timestamp'),
        db.Index('idx_usage_session', 'session_id'),
    )
```

#### 验证规则
- `action_type`: 限定值：['render', 'click', 'submit', 'error', 'close']
- `device_type`: 限定值：['desktop', 'tablet', 'mobile']
- `interaction_data`: JSON格式，记录具体交互细节
- 数据聚合：按小时、按天进行统计聚合

## 实体关系图

```
User (现有)
├── ui_configs (1:N)           -> UIComponentConfig
├── ui_preferences (1:1)       -> UserUIPreferences  
├── performance_records (1:N)  -> PerformanceMetrics
└── usage_stats (1:N)          -> ComponentUsageStats

UIComponentConfig
├── 依赖组件定义文件
└── 支持版本管理

ComponentRenderCache
├── 基于内容哈希缓存
└── 支持TTL过期策略

PerformanceMetrics
└── 支持多维度性能分析

UserUIPreferences
└── 支持实时同步更新
```

## 数据迁移策略

### 阶段1: 基础结构创建
1. 创建新表结构
2. 添加必要索引
3. 建立外键关系

### 阶段2: 数据初始化
1. 为现有用户创建默认UI偏好
2. 初始化全局组件配置
3. 设置性能监控基准

### 阶段3: 数据迁移
1. 现有用户设置迁移到新表
2. 历史性能数据导入
3. 数据一致性验证

## 性能优化

### 索引策略
- 组合索引：用户+组件名，用户+时间戳
- 单列索引：缓存键，过期时间，组件类型
- 分区策略：性能数据按月分区

### 缓存策略
- L1缓存：组件配置（内存，5分钟）
- L2缓存：渲染结果（Redis，30分钟）
- L3缓存：用户偏好（内存，用户会话期间）

### 数据清理
- 性能记录：保留30天
- 使用统计：聚合后保留90天原始数据
- 渲染缓存：基于TTL自动清理

## 备注

1. 所有JSON字段都需要定义Schema验证
2. 时间字段统一使用UTC时区
3. 敏感配置数据需要加密存储
4. 支持配置的版本控制和回滚
5. 性能数据需要定期分析和报表生成

---

*本数据模型设计遵循现有系统架构，确保向后兼容性和数据一致性。*