# Kronos Stock API 文档

## 概述

Kronos Stock 系统提供了完整的 REST API 和 HTMX 视图端点，用于股票预测、用户管理、UI组件配置和性能监控。

## 基础信息

- **基础URL**: `http://localhost:5001`
- **API版本**: `v1`
- **认证方式**: Session-based (Flask-Session)
- **数据格式**: JSON
- **字符编码**: UTF-8

## API 端点概览

### 1. 认证相关 API (`/api/auth`)

#### 用户注册
```http
POST /api/auth/register
Content-Type: application/json

{
    "username": "string",
    "email": "string", 
    "password": "string",
    "nickname": "string (可选)"
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "用户注册成功",
    "user": {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "nickname": "测试用户",
        "created_at": "2025-01-01T12:00:00Z"
    }
}
```

#### 用户登录
```http
POST /api/auth/login
Content-Type: application/json

{
    "username": "string",
    "password": "string",
    "remember_me": "boolean (可选)"
}
```

#### 用户登出
```http
POST /api/auth/logout
```

### 2. 股票预测 API (`/api/prediction`)

#### 预测股票价格
```http
POST /api/prediction/predict
Content-Type: application/json

{
    "stock_code": "000001",
    "prediction_days": 5,
    "model_name": "kronos-mini"
}
```

**响应示例**:
```json
{
    "success": true,
    "prediction": {
        "stock_code": "000001",
        "stock_name": "平安银行",
        "prediction_id": "pred_123456",
        "predictions": [
            {
                "date": "2025-01-02",
                "predicted_price": 12.34,
                "confidence": 0.85
            }
        ],
        "model_info": {
            "name": "kronos-mini",
            "version": "1.0.0"
        }
    }
}
```

#### 获取预测历史
```http
GET /api/prediction/history?page=1&per_page=10&stock_code=000001
```

### 3. 股票数据 API (`/api/stock`)

#### 获取股票信息
```http
GET /api/stock/<stock_code>
```

#### 搜索股票
```http
GET /api/stock/search?q=平安银行&limit=10
```

#### 获取市场数据
```http
GET /api/market/overview
GET /api/market/sse  # 上证指数
GET /api/market/szse # 深证成指
```

### 4. UI组件配置 API (`/api/ui-components`)

#### 获取组件配置
```http
GET /api/ui-components/
GET /api/ui-components/<config_id>
```

#### 更新组件配置
```http
PUT /api/ui-components/<config_id>
Content-Type: application/json

{
    "component_name": "sidebar",
    "config_data": {
        "theme": "dark",
        "position": "left",
        "collapsed": false
    },
    "enabled": true
}
```

**响应示例**:
```json
{
    "success": true,
    "message": "组件配置更新成功",
    "config": {
        "id": 1,
        "component_name": "sidebar",
        "config_data": {
            "theme": "dark",
            "position": "left", 
            "collapsed": false
        },
        "enabled": true,
        "updated_at": "2025-01-01T12:00:00Z"
    }
}
```

#### 创建组件配置
```http
POST /api/ui-components/
Content-Type: application/json

{
    "component_name": "chart_display",
    "config_data": {
        "chart_type": "candlestick",
        "show_volume": true,
        "indicators": ["MA5", "MA10"]
    }
}
```

### 5. 用户偏好 API (`/api/user-preferences`)

#### 获取用户偏好
```http
GET /api/user-preferences/<user_id>
GET /api/user-preferences/<user_id>/<preference_id>
```

#### 更新用户偏好
```http
PUT /api/user-preferences/<user_id>/<preference_id>
Content-Type: application/json

{
    "preference_key": "theme",
    "preference_value": {
        "mode": "dark",
        "primary_color": "#3b82f6"
    }
}
```

#### 批量更新偏好
```http
PUT /api/user-preferences/<user_id>/batch
Content-Type: application/json

{
    "preferences": {
        "theme": {"mode": "dark"},
        "language": {"locale": "zh-CN"},
        "dashboard": {"layout": "grid"}
    }
}
```

### 6. 性能监控 API (`/api/performance`)

#### 提交性能指标
```http
POST /api/performance/metrics
Content-Type: application/json

{
    "metric_type": "page_load",
    "metric_name": "dashboard_load_time",
    "metric_value": 1.25,
    "session_id": "sess_123456",
    "user_agent": "Mozilla/5.0...",
    "additional_data": {
        "page": "/dashboard",
        "component_count": 15
    }
}
```

#### 获取性能报告
```http
GET /api/performance/report?start_date=2025-01-01&end_date=2025-01-31&metric_type=page_load
```

### 7. 使用统计 API (`/api/usage-tracking`)

#### 记录使用行为
```http
POST /api/usage-tracking/
Content-Type: application/json

{
    "component_name": "prediction_form",
    "action": "submit", 
    "session_id": "sess_123456",
    "additional_data": {
        "stock_code": "000001",
        "model_used": "kronos-mini"
    }
}
```

#### 获取使用统计
```http
GET /api/usage-tracking/stats?component=prediction_form&period=7d
```

## HTMX 视图端点

### 1. 组件渲染 (`/htmx/components`)

#### 获取组件HTML
```http
GET /htmx/components/<component_name>?config_id=1&user_id=123
```

#### 渲染表单组件  
```http
GET /htmx/forms/<form_type>?context=prediction&stock_code=000001
```

#### 渲染模态框
```http
GET /htmx/modals/<modal_type>?title=确认删除&message=是否确定删除此预测记录？
```

#### 获取通知列表
```http
GET /htmx/notifications/?user_id=123&limit=10
```

### 2. 用户状态 (`/htmx/user`)

#### 获取用户状态
```http
GET /htmx/user/status
```

## 错误响应格式

所有API错误都遵循统一的响应格式：

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "输入数据验证失败",
        "details": {
            "field": "stock_code",
            "reason": "股票代码格式不正确"
        }
    }
}
```

### 常见错误代码

- `VALIDATION_ERROR` - 输入验证失败
- `NOT_FOUND` - 资源不存在
- `UNAUTHORIZED` - 未认证
- `FORBIDDEN` - 权限不足  
- `RATE_LIMIT_EXCEEDED` - 请求频率超限
- `INTERNAL_ERROR` - 服务器内部错误
- `MODEL_ERROR` - AI模型处理错误
- `STOCK_DATA_ERROR` - 股票数据获取失败

## 请求限制

- **认证API**: 每IP每分钟最多10次请求
- **预测API**: 每用户每分钟最多5次预测请求
- **其他API**: 每IP每分钟最多100次请求
- **文件上传**: 最大文件大小 10MB

## 认证和权限

### Session认证
使用Flask-Session进行会话管理：
- 登录后获得24小时有效期的会话
- 会话信息存储在服务器端
- 客户端通过Cookie保持会话状态

### 权限控制
- **公开端点**: 无需认证（如注册、股票基础信息查询）
- **用户端点**: 需要登录认证（如预测、偏好设置）
- **管理端点**: 需要管理员权限（如系统配置）

## 开发和测试

### 本地开发
```bash
# 启动开发服务器
python run.py

# API基础URL
http://localhost:5001
```

### API测试工具
推荐使用以下工具测试API：
- **Postman** - 完整的API测试套件
- **curl** - 命令行快速测试
- **HTTPie** - 用户友好的HTTP客户端

### 示例测试请求 (curl)
```bash
# 用户注册
curl -X POST http://localhost:5001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# 股票预测
curl -X POST http://localhost:5001/api/prediction/predict \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"stock_code":"000001","prediction_days":5,"model_name":"kronos-mini"}'
```

## 更新日志

### v2.0.0 (2025-01-01)
- ✅ 新增UI组件配置API (`/api/ui-components`)
- ✅ 新增用户偏好管理API (`/api/user-preferences`)  
- ✅ 新增性能监控API (`/api/performance`)
- ✅ 新增使用统计API (`/api/usage-tracking`)
- ✅ 新增HTMX视图端点套件
- ✅ 改进错误处理和响应格式
- ✅ 增加请求速率限制
- ✅ 优化API文档和示例

### v1.0.0 (2024-12-01)  
- 基础认证API
- 股票预测API
- 市场数据API
- 用户管理功能

---

*本文档最后更新时间: 2025-01-07*