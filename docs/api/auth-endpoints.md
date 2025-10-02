# 用户认证 API 端点文档

## 概览

本文档描述了 Kronos Stock 系统中用户认证相关的 API 端点。所有 API 端点都遵循 RESTful 设计原则，使用 JSON 格式进行数据交换。

## 基础信息

- **基础URL**: `http://localhost:5001/api`
- **数据格式**: JSON
- **字符编码**: UTF-8
- **认证方式**: Bearer Token (JWT)

## 认证端点

### 1. 用户注册

注册新用户账户。

**端点**: `POST /auth/register`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "test_user",
  "email": "test@example.com",
  "password": "Password123!",
  "confirm_password": "Password123!",
  "nickname": "测试用户",
  "phone": "13812345678"
}
```

**字段说明**:
- `username` (必填): 用户名，3-50个字符，只能包含字母、数字、下划线、连字符和点号
- `email` (必填): 邮箱地址，必须是有效格式
- `password` (必填): 密码，至少8位，必须包含大小写字母、数字和特殊字符
- `confirm_password` (必填): 确认密码，必须与password一致
- `nickname` (可选): 昵称，显示名称
- `phone` (可选): 手机号码，中国大陆格式

**成功响应** (201 Created):
```json
{
  "success": true,
  "message": "用户注册成功",
  "data": {
    "user_id": 1,
    "username": "test_user",
    "email": "test@example.com",
    "nickname": "测试用户",
    "is_active": true,
    "created_at": "2023-12-01T10:30:00Z"
  }
}
```

**错误响应** (400 Bad Request):
```json
{
  "success": false,
  "message": "注册信息验证失败",
  "errors": {
    "username": ["用户名已存在"],
    "email": ["邮箱已被注册"],
    "password": ["密码强度不足"]
  }
}
```

### 2. 用户登录

用户账户登录认证。

**端点**: `POST /auth/login`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "username": "test_user",
  "password": "Password123!"
}
```

**字段说明**:
- `username` (必填): 用户名或邮箱地址
- `password` (必填): 用户密码

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": 1,
      "username": "test_user",
      "email": "test@example.com",
      "nickname": "测试用户",
      "is_active": true,
      "is_admin": false,
      "last_login_at": "2023-12-01T10:30:00Z"
    }
  }
}
```

**错误响应** (401 Unauthorized):
```json
{
  "success": false,
  "message": "用户名或密码错误",
  "errors": {
    "authentication": ["认证失败"]
  }
}
```

### 3. 用户登出

注销当前用户会话。

**端点**: `POST /auth/logout`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**请求体**: 无

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "登出成功"
}
```

**错误响应** (401 Unauthorized):
```json
{
  "success": false,
  "message": "无效的认证令牌",
  "errors": {
    "token": ["令牌无效或已过期"]
  }
}
```

### 4. 密码重置申请

申请重置密码，发送重置链接到邮箱。

**端点**: `POST /auth/reset-password`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "email": "test@example.com"
}
```

**字段说明**:
- `email` (必填): 注册邮箱地址

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "密码重置链接已发送到您的邮箱"
}
```

**错误响应** (404 Not Found):
```json
{
  "success": false,
  "message": "邮箱地址不存在",
  "errors": {
    "email": ["未找到对应的用户账户"]
  }
}
```

### 5. 确认密码重置

使用重置令牌设置新密码。

**端点**: `POST /auth/reset-password/confirm`

**请求头**:
```
Content-Type: application/json
```

**请求体**:
```json
{
  "reset_token": "reset_token_here",
  "new_password": "NewPassword123!",
  "confirm_password": "NewPassword123!"
}
```

**字段说明**:
- `reset_token` (必填): 从邮件中获取的重置令牌
- `new_password` (必填): 新密码
- `confirm_password` (必填): 确认新密码

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "密码重置成功"
}
```

## 用户管理端点

### 6. 获取用户档案

获取当前用户的详细档案信息。

**端点**: `GET /user/profile`

**请求头**:
```
Authorization: Bearer {access_token}
```

**成功响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "test_user",
      "email": "test@example.com",
      "nickname": "测试用户",
      "is_active": true,
      "is_admin": false,
      "created_at": "2023-11-01T10:30:00Z",
      "last_login_at": "2023-12-01T10:30:00Z"
    },
    "profile": {
      "real_name": "张三",
      "phone": "13812345678",
      "gender": "male",
      "birth_date": "1990-01-01",
      "location": "北京市",
      "bio": "股票投资爱好者",
      "investment_experience": "中级",
      "risk_tolerance": "中等",
      "investment_goal": "长期增值"
    }
  }
}
```

### 7. 更新用户档案

更新用户档案信息。

**端点**: `PUT /user/profile`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "nickname": "新昵称",
  "phone": "13987654321",
  "real_name": "李四",
  "gender": "female",
  "birth_date": "1992-05-15",
  "location": "上海市",
  "bio": "专业投资者",
  "investment_experience": "高级",
  "risk_tolerance": "激进",
  "investment_goal": "短期收益"
}
```

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "档案更新成功",
  "data": {
    "profile": {
      "real_name": "李四",
      "phone": "13987654321",
      "nickname": "新昵称",
      "gender": "female",
      "birth_date": "1992-05-15",
      "location": "上海市",
      "bio": "专业投资者",
      "investment_experience": "高级",
      "risk_tolerance": "激进",
      "investment_goal": "短期收益",
      "updated_at": "2023-12-01T11:00:00Z"
    }
  }
}
```

### 8. 获取用户关注列表

获取用户关注的股票列表。

**端点**: `GET /user/watchlist`

**请求头**:
```
Authorization: Bearer {access_token}
```

**查询参数**:
- `page` (可选): 页码，默认为1
- `per_page` (可选): 每页数量，默认为20，最大100

**成功响应** (200 OK):
```json
{
  "success": true,
  "data": {
    "watchlist": [
      {
        "id": 1,
        "stock_code": "000001",
        "stock_name": "平安银行",
        "added_at": "2023-11-15T09:30:00Z"
      },
      {
        "id": 2,
        "stock_code": "600036",
        "stock_name": "招商银行",
        "added_at": "2023-11-20T14:20:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 15,
      "total_pages": 1
    }
  }
}
```

### 9. 添加股票到关注列表

将股票添加到用户的关注列表。

**端点**: `POST /user/watchlist`

**请求头**:
```
Content-Type: application/json
Authorization: Bearer {access_token}
```

**请求体**:
```json
{
  "stock_code": "000002",
  "stock_name": "万科A"
}
```

**字段说明**:
- `stock_code` (必填): 股票代码，6位数字格式
- `stock_name` (可选): 股票名称，如果不提供将自动获取

**成功响应** (201 Created):
```json
{
  "success": true,
  "message": "股票已添加到关注列表",
  "data": {
    "watchlist_item": {
      "id": 3,
      "stock_code": "000002",
      "stock_name": "万科A",
      "added_at": "2023-12-01T12:00:00Z"
    }
  }
}
```

**错误响应** (400 Bad Request):
```json
{
  "success": false,
  "message": "股票已在关注列表中",
  "errors": {
    "stock_code": ["该股票已存在于关注列表"]
  }
}
```

### 10. 从关注列表移除股票

从用户关注列表中移除指定股票。

**端点**: `DELETE /user/watchlist/{stock_code}`

**请求头**:
```
Authorization: Bearer {access_token}
```

**路径参数**:
- `stock_code`: 要移除的股票代码

**成功响应** (200 OK):
```json
{
  "success": true,
  "message": "股票已从关注列表移除"
}
```

## 错误处理

### HTTP 状态码

- `200 OK`: 请求成功
- `201 Created`: 资源创建成功
- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未认证或认证失败
- `403 Forbidden`: 权限不足
- `404 Not Found`: 资源不存在
- `409 Conflict`: 资源冲突（如用户名重复）
- `429 Too Many Requests`: 请求频率超限
- `500 Internal Server Error`: 服务器内部错误

### 错误响应格式

所有错误响应都遵循统一格式：

```json
{
  "success": false,
  "message": "错误描述信息",
  "errors": {
    "field_name": ["具体错误信息1", "具体错误信息2"],
    "another_field": ["另一个字段的错误信息"]
  },
  "error_code": "ERROR_CODE_IF_APPLICABLE"
}
```

### 常见错误代码

- `AUTH_REQUIRED`: 需要认证
- `TOKEN_INVALID`: 令牌无效
- `TOKEN_EXPIRED`: 令牌过期
- `USER_NOT_FOUND`: 用户不存在
- `USER_INACTIVE`: 用户账户已禁用
- `VALIDATION_ERROR`: 数据验证失败
- `RATE_LIMIT_EXCEEDED`: 请求频率超限

## 认证说明

### Bearer Token 认证

大部分端点需要在请求头中包含有效的访问令牌：

```
Authorization: Bearer {access_token}
```

### 令牌生命周期

- 访问令牌有效期：24小时
- 令牌过期后需要重新登录获取新令牌
- 登出操作会立即使令牌失效

### 安全建议

1. **保护令牌安全**: 不要在客户端明文存储令牌
2. **使用HTTPS**: 生产环境必须使用HTTPS传输
3. **及时登出**: 使用完毕后及时调用登出接口
4. **定期更换密码**: 建议用户定期更换密码
5. **监控异常登录**: 注意检测异常的登录活动

## 速率限制

为了防止滥用，API 实施了速率限制：

- 登录端点：每分钟最多5次尝试
- 注册端点：每小时最多3次注册
- 密码重置：每小时最多3次申请
- 其他端点：每分钟最多60次请求

当触发速率限制时，将返回 429 状态码：

```json
{
  "success": false,
  "message": "请求过于频繁，请稍后再试",
  "retry_after": 60
}
```

## 示例代码

### JavaScript/Fetch 示例

```javascript
// 用户登录
async function loginUser(username, password) {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      username: username,
      password: password
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // 存储令牌
    localStorage.setItem('access_token', data.data.access_token);
    return data.data.user;
  } else {
    throw new Error(data.message);
  }
}

// 获取用户档案
async function getUserProfile() {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('/api/user/profile', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  return data.data;
}
```

### Python/Requests 示例

```python
import requests

# 用户登录
def login_user(username, password):
    url = 'http://localhost:5001/api/auth/login'
    data = {
        'username': username,
        'password': password
    }
    
    response = requests.post(url, json=data)
    result = response.json()
    
    if result['success']:
        return result['data']
    else:
        raise Exception(result['message'])

# 获取用户档案
def get_user_profile(access_token):
    url = 'http://localhost:5001/api/user/profile'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.get(url, headers=headers)
    result = response.json()
    
    return result['data']
```

## 更新日志

### v1.0.0 (2023-12-01)
- 初始版本发布
- 实现基础用户认证功能
- 添加用户档案管理
- 实现股票关注列表功能

---

**注意**: 本文档描述的是开发版本API，生产环境的具体实现可能会有所不同。请根据实际部署环境调整基础URL和相关配置。