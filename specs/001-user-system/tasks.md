# Tasks: 用户系统

**Input**: Design documents from `/specs/001-user-system/`
**Prerequisites**: plan.md (required), spec.md (required)

## 执行流程概述

基于功能规范和实现计划，用户登录功能将分解为以下子任务类别：
- **环境配置**: 数据库配置、依赖安装、项目结构
- **测试优先**: 合约测试、集成测试（TDD开发）
- **核心实现**: 数据模型、服务层、API端点
- **用户界面**: 登录页面、仪表板、导航集成
- **集成优化**: 中间件、安全配置、性能优化

## 路径约定
- **Backend**: `app/` 目录（Flask应用）
- **Frontend**: `app/templates/` 和 `assets/css/`
- **Tests**: `tests/` 目录
- **Migrations**: `migrations/versions/`

## Phase 3.1: 环境配置和项目结构
- [ ] T001 安装用户系统相关依赖（bcrypt, PyJWT, Flask-Login）
- [ ] T002 [P] 配置数据库连接（SQLite本地，MySQL生产环境）
- [ ] T003 [P] 创建用户系统目录结构（services, models, templates）
- [ ] T004 [P] 配置环境变量和密钥管理

## Phase 3.2: 数据库设计和迁移 ⚠️ 必须在实现前完成
**关键：数据模型必须先创建并测试通过**
- [ ] T005 [P] 创建User模型 in app/models/user.py
- [ ] T006 [P] 创建UserProfile模型 in app/models/user_profile.py
- [ ] T007 [P] 创建UserSession模型 in app/models/user_session.py
- [ ] T008 [P] 创建UserPrediction关联模型 in app/models/user_prediction.py
- [ ] T009 [P] 创建Watchlist模型 in app/models/watchlist.py
- [ ] T010 生成并测试数据库迁移脚本 in migrations/versions/

## Phase 3.3: 测试优先开发 (TDD) ⚠️ 必须在实现前完成
**关键：这些测试必须编写完成并失败，然后才能开始实现**
- [ ] T011 [P] 用户注册API合约测试 in tests/api/test_auth_register.py
- [ ] T012 [P] 用户登录API合约测试 in tests/api/test_auth_login.py
- [ ] T013 [P] 用户登出API合约测试 in tests/api/test_auth_logout.py
- [ ] T014 [P] 用户档案API合约测试 in tests/api/test_user_profile.py
- [ ] T015 [P] 密码重置流程集成测试 in tests/integration/test_password_reset.py
- [ ] T016 [P] 用户认证流程集成测试 in tests/integration/test_auth_flow.py
- [ ] T017 [P] 用户会话管理集成测试 in tests/integration/test_session_management.py

## Phase 3.4: 服务层实现（仅在测试失败后进行）
- [ ] T018 [P] 用户认证服务 in app/services/auth_service.py
- [ ] T019 [P] 用户管理服务 in app/services/user_service.py
- [ ] T020 [P] 会话管理服务 in app/services/session_service.py
- [ ] T021 [P] 密码加密和验证服务 in app/services/password_service.py
- [ ] T022 用户输入验证和清理 in app/utils/validators.py

## Phase 3.5: API端点实现 ✅ 已完成
- [x] T023 POST /api/auth/register 用户注册端点 in app/api/auth.py
- [x] T024 POST /api/auth/login 用户登录端点 in app/api/auth.py
- [x] T025 POST /api/auth/logout 用户登出端点 in app/api/auth.py
- [x] T026 POST /api/auth/reset-password 密码重置端点 in app/api/auth.py
- [x] T027 GET /api/user/profile 获取用户档案端点 in app/api/user.py
- [x] T028 PUT /api/user/profile 更新用户档案端点 in app/api/user.py
- [x] T029 GET /api/user/watchlist 获取关注列表端点 in app/api/user.py
- [x] T030 POST /api/user/watchlist 添加股票到关注列表 in app/api/user.py

## Phase 3.6: 用户界面模板 ✅
- [x] T031 用户登录页面 in app/templates/auth/login.html
- [x] T032 用户注册页面 in app/templates/auth/register.html
- [x] T033 密码重置页面 in app/templates/auth/reset_password.html
- [x] T034 用户仪表板页面 in app/templates/user/dashboard.html
- [x] T035 用户资料页面 in app/templates/user/profile.html
- [x] T036 关注列表页面 in app/templates/user/watchlist.html
- [x] T037 用户认证视图控制器 in app/views/auth.py
- [x] T038 用户管理视图控制器 in app/views/user.py

## Phase 3.7: 中间件和安全集成 ✅
- [x] T039 认证中间件实现 in app/middleware/auth_middleware.py
- [x] T040 会话管理中间件 in app/middleware/session_middleware.py
- [x] T041 速率限制配置（5次尝试/分钟）
- [x] T042 CSRF保护配置
- [x] T043 安全响应头配置
- [x] T044 用户权限装饰器 in app/decorators/auth_decorators.py

## Phase 3.8: 导航和UI集成 ✅
- [x] T045 更新主导航显示用户状态 in app/templates/layouts/base.html
- [x] T046 [P] 移动端用户菜单组件 in app/templates/components/user_menu.html
- [x] T047 [P] 用户头像和状态组件 in app/templates/components/user_avatar.html
- [x] T048 登录状态检查的HTMX组件更新

## Phase 3.9: 数据库优化和索引 ✅
- [x] T049 [P] 用户邮箱唯一索引优化
- [x] T050 [P] 会话令牌查询索引优化
- [x] T051 [P] 用户预测关联查询优化
- [x] T052 过期会话自动清理任务

## Phase 3.10: 性能优化和缓存 ✅
- [x] T053 [P] 用户会话数据缓存策略
- [x] T054 [P] 用户档案数据缓存
- [x] T055 登录性能测试（目标<2秒）
- [x] T056 仪表板加载性能测试（目标<3秒）

## Phase 3.11: 单元测试和文档
- [ ] T057 [P] 用户服务单元测试 in tests/unit/test_user_service.py
- [ ] T058 [P] 认证服务单元测试 in tests/unit/test_auth_service.py
- [ ] T059 [P] 密码验证单元测试 in tests/unit/test_password_service.py
- [ ] T060 [P] 验证器单元测试 in tests/unit/test_validators.py
- [ ] T061 [P] API文档更新 in docs/api/auth-endpoints.md
- [ ] T062 [P] 用户系统使用文档 in docs/user-system.md

## 依赖关系

### 阻塞依赖关系
- T001-T004 (环境配置) 必须在所有其他任务之前
- T005-T010 (数据模型) 必须在T018-T030 (服务和API) 之前
- T011-T017 (测试) 必须在T018-T048 (实现) 之前
- T018-T022 (服务层) 必须在T023-T030 (API端点) 之前
- T023-T030 (API端点) 必须在T037-T038 (视图控制器) 之前
- T031-T036 (模板) 可以与T037-T038 (视图) 并行开发

### 并行执行组
```
# 数据模型组（可并行）
Task: "创建User模型 in app/models/user.py"
Task: "创建UserProfile模型 in app/models/user_profile.py"  
Task: "创建UserSession模型 in app/models/user_session.py"
Task: "创建UserPrediction关联模型 in app/models/user_prediction.py"
Task: "创建Watchlist模型 in app/models/watchlist.py"

# 测试组（可并行）
Task: "用户注册API合约测试 in tests/api/test_auth_register.py"
Task: "用户登录API合约测试 in tests/api/test_auth_login.py"
Task: "用户登出API合约测试 in tests/api/test_auth_logout.py"
Task: "密码重置流程集成测试 in tests/integration/test_password_reset.py"

# 服务层组（可并行）
Task: "用户认证服务 in app/services/auth_service.py"
Task: "用户管理服务 in app/services/user_service.py"
Task: "会话管理服务 in app/services/session_service.py"

# 模板组（可并行）
Task: "用户登录页面模板 in app/templates/auth/login.html"
Task: "用户注册页面模板 in app/templates/auth/register.html"
Task: "用户仪表板模板 in app/templates/user/dashboard.html"
```

## 中文优先开发要求

**重要**: 根据项目宪法第VII条，所有开发必须遵循中文优先原则：

### 代码层面
- 所有注释使用中文
- 变量和函数名采用中文拼音或中英文混合（语义清晰的情况下）
- 错误消息和日志使用中文
- 数据库字段注释使用中文

### 用户界面
- 所有UI文本使用中文
- 错误提示信息使用中文
- 表单标签和按钮文字使用中文
- 邮件模板使用中文

### 文档和测试
- 测试用例描述使用中文
- API文档使用中文
- 代码注释和文档字符串使用中文

## 验证标准

### 功能验证
- [ ] 用户可以成功注册和登录
- [ ] 密码安全性符合要求（bcrypt, 12轮）
- [ ] 会话管理正常工作（24小时过期）
- [ ] 速率限制有效防止暴力破解
- [ ] 用户界面响应式设计正常工作

### 性能验证  
- [ ] 登录响应时间 < 2秒
- [ ] 仪表板加载时间 < 3秒
- [ ] 支持1000+并发用户
- [ ] 数据库查询经过优化

### 安全验证
- [ ] 密码哈希安全存储
- [ ] 会话令牌安全生成
- [ ] CSRF保护正常工作
- [ ] SQL注入防护有效
- [ ] XSS攻击防护有效

---

**总任务数**: 62个任务
**预估开发时间**: 2-3周（单人全职开发）
**关键里程碑**: 
1. 数据模型完成（T005-T010）
2. 核心认证功能完成（T018-T030）
3. 用户界面完成（T031-T048）
4. 系统集成完成（T039-T056）

**下一步**: 开始执行Phase 3.1的环境配置任务