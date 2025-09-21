# Kronos Stock 数据库设计

## 数据库关系图

```mermaid
erDiagram
    %% 用户相关表
    users {
        string id PK "用户ID (UUID)"
        string email UK "邮箱地址"
        string phone UK "手机号"
        string password_hash "密码哈希"
        string subscription_tier "订阅等级"
        timestamp subscription_expires "订阅过期时间"
        boolean is_active "是否激活"
        boolean is_verified "是否验证"
        timestamp created_at "创建时间"
        timestamp updated_at "更新时间"
        timestamp last_login "最后登录时间"
    }

    user_profiles {
        string user_id PK,FK "用户ID"
        string display_name "显示名称"
        string avatar_url "头像URL"
        string risk_tolerance "风险承受能力"
        string investment_experience "投资经验"
        json preferred_sectors "偏好行业"
        json notification_preferences "通知偏好"
        integer total_predictions "总预测次数"
        integer successful_predictions "成功预测次数"
        timestamp created_at "创建时间"
        timestamp updated_at "更新时间"
    }

    %% 预测相关表
    predictions {
        string id PK "预测ID (UUID)"
        string user_id FK "用户ID"
        string stock_symbol "股票代码"
        string stock_name "股票名称"
        string model_type "模型类型"
        integer prediction_days "预测天数"
        decimal current_price "当前价格"
        decimal predicted_price "预测价格"
        decimal confidence "置信度"
        json prediction_data "预测数据"
        string status "状态"
        timestamp created_at "创建时间"
        timestamp expires_at "过期时间"
    }

    prediction_results {
        string prediction_id PK,FK "预测ID"
        decimal actual_price "实际价格"
        decimal accuracy_score "准确性得分"
        timestamp verified_at "验证时间"
    }

    %% 订阅相关表
    subscriptions {
        string id PK "订阅ID (UUID)"
        string user_id FK "用户ID"
        string plan "订阅计划"
        string status "状态"
        timestamp start_date "开始时间"
        timestamp end_date "结束时间"
        decimal amount "金额"
        string currency "货币"
        string payment_method "支付方式"
        string payment_id "支付ID"
        timestamp created_at "创建时间"
    }

    usage_records {
        string id PK "记录ID (UUID)"
        string user_id FK "用户ID"
        string action_type "操作类型"
        string resource_id "资源ID"
        integer cost "消耗积分"
        timestamp created_at "创建时间"
    }

    %% 股票数据表
    stock_data {
        string symbol PK "股票代码"
        date date PK "日期"
        decimal open_price "开盘价"
        decimal close_price "收盘价"
        decimal high_price "最高价"
        decimal low_price "最低价"
        bigint volume "成交量"
        timestamp created_at "创建时间"
    }

    %% 社区相关表
    posts {
        string id PK "帖子ID (UUID)"
        string user_id FK "用户ID"
        string title "标题"
        text content "内容"
        string prediction_id FK "预测ID"
        integer likes_count "点赞数"
        integer comments_count "评论数"
        boolean is_featured "是否精选"
        timestamp created_at "创建时间"
        timestamp updated_at "更新时间"
    }

    comments {
        string id PK "评论ID (UUID)"
        string post_id FK "帖子ID"
        string user_id FK "用户ID"
        text content "评论内容"
        string parent_comment_id FK "父评论ID"
        timestamp created_at "创建时间"
    }

    likes {
        string user_id PK,FK "用户ID"
        string post_id PK,FK "帖子ID"
        timestamp created_at "创建时间"
    }

    %% 关注和预警表
    watchlists {
        string id PK "关注列表ID (UUID)"
        string user_id FK "用户ID"
        string stock_symbol "股票代码"
        string stock_name "股票名称"
        decimal alert_price_high "高价预警"
        decimal alert_price_low "低价预警"
        boolean is_active "是否激活"
        timestamp created_at "创建时间"
    }

    price_alerts {
        string id PK "预警ID (UUID)"
        string user_id FK "用户ID"
        string stock_symbol "股票代码"
        string alert_type "预警类型"
        decimal target_price "目标价格"
        decimal change_percent "变化百分比"
        boolean is_active "是否激活"
        timestamp triggered_at "触发时间"
        timestamp created_at "创建时间"
    }

    %% 通知表
    notifications {
        string id PK "通知ID (UUID)"
        string user_id FK "用户ID"
        string type "通知类型"
        string title "标题"
        text message "消息内容"
        json data "附加数据"
        boolean is_read "是否已读"
        timestamp created_at "创建时间"
    }

    %% 系统配置表
    system_configs {
        string key PK "配置键"
        text value "配置值"
        text description "描述"
        timestamp updated_at "更新时间"
    }

    %% 关系定义
    users ||--|| user_profiles : "一对一"
    users ||--o{ predictions : "一对多"
    users ||--o{ subscriptions : "一对多"
    users ||--o{ usage_records : "一对多"
    users ||--o{ posts : "一对多"
    users ||--o{ comments : "一对多"
    users ||--o{ likes : "一对多"
    users ||--o{ watchlists : "一对多"
    users ||--o{ price_alerts : "一对多"
    users ||--o{ notifications : "一对多"

    predictions ||--|| prediction_results : "一对一"
    predictions ||--o{ posts : "一对多"

    posts ||--o{ comments : "一对多"
    posts ||--o{ likes : "一对多"
    
    comments ||--o{ comments : "自关联(父子评论)"
```

## 数据库表说明

### 核心业务表

#### 1. 用户管理
- **users**: 用户基础信息表，存储登录凭证和订阅信息
- **user_profiles**: 用户详细配置表，存储个人偏好和统计数据

#### 2. 预测业务
- **predictions**: 股票预测记录表，核心业务表
- **prediction_results**: 预测结果验证表，用于评估预测准确性
- **stock_data**: 股票历史数据表，支持预测算法

#### 3. 订阅计费
- **subscriptions**: 用户订阅记录表
- **usage_records**: 用户使用记录表，用于计费和限额控制

#### 4. 社区功能
- **posts**: 社区帖子表，用户可分享预测见解
- **comments**: 评论表，支持嵌套评论
- **likes**: 点赞表，用户互动功能

#### 5. 个性化服务
- **watchlists**: 用户关注股票列表
- **price_alerts**: 价格预警设置
- **notifications**: 系统通知表

#### 6. 系统管理
- **system_configs**: 系统配置表，存储应用级配置参数

## 主要特性

### 数据完整性保证
- 使用 UUID 作为主键，避免 ID 冲突
- 外键约束确保数据一致性
- 级联删除保证数据清理完整性

### 性能优化
- 针对常用查询创建复合索引
- 分离冷热数据（历史数据 vs 活跃数据）
- JSON 字段存储灵活配置数据

### 扩展性设计
- 预测数据使用 JSON 存储，支持不同模型格式
- 通知系统支持多种类型扩展
- 配置表支持动态系统参数调整

### 业务逻辑支持
- 订阅等级控制使用限额
- 预测结果自动过期机制
- 社区内容与预测记录关联
- 灵活的价格预警机制

## 索引策略

关键查询路径的索引优化：
- 用户邮箱唯一索引（登录查询）
- 预测记录按用户和时间的复合索引
- 股票数据按代码和日期的复合索引
- 通知按用户和读取状态的复合索引

## 数据保留策略

- 股票历史数据保留 365 天
- 系统通知保留 30 天
- 预测记录永久保留（用于模型训练）
- 用户行为记录用于分析和计费