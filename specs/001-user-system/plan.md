# 实施计划：用户系统

**分支**: `001-user-system` | **日期**: 2025-10-01 | **规范**: [spec.md](./spec.md)
**输入**: 来自 `/specs/001-user-system/spec.md` 的功能规范

## 概述
实现包含认证、授权、档案管理和与现有股票预测功能集成的综合用户管理系统。该系统将遵循Flask蓝图架构，采用服务层业务逻辑和TDD开发实践。

## 技术背景
**语言/版本**: Python 3.11+  
**主要依赖**: Flask 2.3.3, SQLAlchemy, Flask-Migrate, bcrypt, PyJWT  
**存储**: SQLite（开发环境）, MySQL（生产环境）配合现有数据库  
**测试**: pytest 配合标记（单元测试、集成测试、API测试、慢测试）  
**目标平台**: Linux服务器配合Docker部署  
**项目类型**: Web应用（Flask后端 + HTMX前端）  
**性能目标**: <2秒登录，<3秒仪表板加载，1000+并发用户  
**约束**: 必须与现有架构集成，维持纯CPU推理  
**规模/范围**: 5个数据库表，15+个API端点，8个UI模板

## 宪法合规检查
*门禁: 必须在阶段0研究前通过。在阶段1设计后重新检查。*

### I. 服务层架构 ✅
- **合规性**: 用户业务逻辑将在 `app/services/user_service.py` 中实现
- **实现**: 蓝图中的路由处理器将委托给服务方法
- **测试**: 服务方法将在无Flask上下文的情况下进行单元测试

### II. 蓝图模块化 ✅
- **API结构**: 认证端点在 `app/api/auth.py` 中
- **Web视图**: 用户相关页面在 `app/views/user.py` 中
- **管理界面**: 管理功能在独立的 `app/views/admin.py` 蓝图中
- **清晰边界**: 用户系统将与股票预测逻辑保持最小依赖

### III. 测试驱动开发 ✅
- **TDD循环**: 为所有认证和用户管理功能首先编写测试
- **测试类别**: 服务的单元测试，认证流程的集成测试，端点的API测试
- **Pytest标记**: 将使用现有的标记系统进行测试组织

### IV. 模型管理与纯CPU推理 ✅
- **无冲突**: 用户系统不涉及AI模型操作
- **兼容性**: 不会干扰现有的模型推理管道
- **集成**: 用户预测将通过外键链接到现有模型输出

### V. 数据验证与金融领域规则 ✅
- **用户数据**: 邮箱验证，密码强度要求
- **集成**: 用户关注列表将使用验证的6位股票代码
- **合规**: 用户活动日志将维护审计跟踪

### VI. 组件优先UI开发 ✅
- **UI组件**: 将使用现有的 `.form-input`, `.btn-primary`, `.card` 类
- **认证表单**: 登录/注册将遵循已建立的表单模式
- **用户仪表板**: 将利用 `.info-card-*`, `.data-table-*` 组件
- **移动响应**: 将使用 `.responsive-grid`, `.mobile-nav-*` 类

### VII. 中文优先开发 ✅
- **代码注释**: 所有注释将使用中文
- **用户界面**: 所有UI文本使用中文
- **变量命名**: 在语义清晰的情况下使用中文拼音
- **文档**: 技术文档和API说明使用中文

## 项目结构

### 文档结构（此功能）
```
specs/001-user-system/
├── plan.md              # 本文件（/plan 命令输出）
├── research.md          # 阶段0输出（/plan 命令）
├── data-model.md        # 阶段1输出（/plan 命令）
├── quickstart.md        # 阶段1输出（/plan 命令）
└── contracts/           # 阶段1 API合约
    ├── auth-endpoints.md
    ├── user-endpoints.md
    └── admin-endpoints.md
```

### 实现结构
```
app/
├── services/
│   ├── user_service.py          # 用户CRUD和业务逻辑
│   ├── auth_service.py          # 认证和会话管理
│   └── admin_service.py         # 管理员操作和用户管理
├── api/
│   ├── auth.py                  # 认证端点
│   ├── user.py                  # 用户档案端点
│   └── admin.py                 # 管理员管理端点
├── views/
│   ├── auth.py                  # 登录/注册/登出页面
│   ├── user.py                  # 用户仪表板和档案页面
│   └── admin.py                 # 管理界面页面
├── models/
│   ├── user.py                  # 用户和用户档案模型
│   ├── session.py               # 用户会话模型
│   └── user_prediction.py       # 用户与预测之间的链接
└── templates/
    ├── auth/                    # 认证模板
    │   ├── login.html          # 登录页面
    │   ├── register.html       # 注册页面
    │   └── reset_password.html # 密码重置页面
    ├── user/                    # 用户界面模板
    │   ├── dashboard.html      # 用户仪表板
    │   ├── profile.html        # 用户档案
    │   └── watchlist.html      # 关注列表
    └── admin/                   # 管理界面模板
        ├── users.html          # 用户管理
        └── analytics.html      # 分析统计
```

### 数据库模式扩展
```
migrations/
└── versions/
    ├── 001_create_user_tables.py     # 创建用户表
    ├── 002_create_user_sessions.py   # 创建用户会话表
    ├── 003_create_user_predictions.py # 创建用户预测表
    └── 004_create_watchlists.py      # 创建关注列表表
```

## Phase 0: Research & Discovery
*Execute immediately after Constitution Check passes*

### Database Design Research
- [ ] **Current Schema Analysis**: Review existing database structure and relationships
- [ ] **Migration Strategy**: Plan for adding user tables without breaking existing data
- [ ] **Index Optimization**: Design database indexes for user lookup performance
- [ ] **Foreign Key Strategy**: Define relationships between users and existing prediction data

### Authentication Architecture Research
- [ ] **Session Management**: Compare database vs Redis for session storage
- [ ] **Password Security**: Research bcrypt configuration for optimal security/performance
- [ ] **JWT vs Sessions**: Evaluate token-based vs session-based authentication
- [ ] **Rate Limiting**: Research Flask-Limiter integration for authentication endpoints

### Integration Research
- [ ] **HTMX Authentication**: Research patterns for authenticated HTMX requests
- [ ] **Middleware Design**: Plan authentication middleware for protecting endpoints
- [ ] **Template Integration**: Research user context integration with existing templates
- [ ] **Navigation Updates**: Plan main navigation changes for authenticated users

### UI/UX Research
- [ ] **Component Inventory**: Catalog existing input.css components suitable for auth forms
- [ ] **Mobile Authentication**: Research mobile-friendly authentication patterns
- [ ] **Dashboard Layout**: Design personalized dashboard using existing layout system
- [ ] **Admin Interface**: Plan admin interface using existing table and form components

## Phase 1: Design & Contracts

### Database Models Design
- [ ] **User Model**: Define User entity with authentication fields
- [ ] **Profile Model**: Design UserProfile for extended user information
- [ ] **Session Model**: Create UserSession for secure session management
- [ ] **Relationship Models**: Define UserPrediction and Watchlist linking models
- [ ] **Migration Scripts**: Create reversible database migration files

### API Contract Design
- [ ] **Authentication Endpoints**: Design POST /api/auth/login, /logout, /register
- [ ] **User Profile Endpoints**: Design GET/PUT /api/user/profile, /preferences
- [ ] **Admin Endpoints**: Design /api/admin/users, /analytics for admin operations
- [ ] **Integration Endpoints**: Extend existing prediction endpoints with user context
- [ ] **Error Handling**: Standardize error responses for authentication failures

### Service Layer Design
- [ ] **UserService**: Design CRUD operations and user management logic
- [ ] **AuthService**: Design authentication, session management, password operations
- [ ] **AdminService**: Design user administration and analytics operations
- [ ] **Integration Services**: Plan integration with existing PredictionService
- [ ] **Validation Logic**: Design input validation and business rule enforcement

### UI Template Design
- [ ] **Authentication Templates**: Design login, register, password reset pages
- [ ] **User Dashboard**: Design personalized dashboard with prediction history
- [ ] **Profile Management**: Design user profile and settings pages
- [ ] **Admin Interface**: Design user management and analytics pages
- [ ] **Navigation Integration**: Design authenticated user navigation and menu updates

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No complexity violations identified** - User system implementation aligns with all constitutional principles:
- Follows established service-layer architecture
- Uses blueprint modularity pattern
- Implements comprehensive TDD approach
- Maintains existing model inference isolation
- Uses component-first UI development
- Follows established CSS and data validation patterns

## Dependencies & Integration Points

### Internal Dependencies
- **Existing Models**: Must integrate with current prediction result storage
- **Stock Service**: Will use existing stock code validation for watchlists
- **Template System**: Will extend existing base templates and navigation
- **Database**: Must coordinate with existing SQLAlchemy setup and migrations

### External Dependencies
- **Email Service**: SMTP configuration for password reset and notifications
- **Cryptography**: bcrypt for password hashing, secure token generation
- **Session Storage**: Database-backed sessions (with optional Redis upgrade path)
- **Rate Limiting**: Flask-Limiter for authentication endpoint protection

### Performance Considerations
- **Database Indexing**: User email, session tokens, foreign key relationships
- **Caching Strategy**: User profile data, session validation
- **Query Optimization**: User dashboard queries, admin analytics
- **Session Cleanup**: Automated expired session removal

## Risk Mitigation

### Security Risks
- **Password Security**: Implement bcrypt with appropriate work factor
- **Session Security**: Secure token generation and proper expiration
- **Rate Limiting**: Prevent brute force attacks on authentication
- **Input Validation**: Comprehensive validation to prevent injection attacks

### Integration Risks
- **Database Migration**: Comprehensive backup and rollback procedures
- **Existing Data**: Careful handling of existing prediction data relationships
- **Template Conflicts**: Thorough testing of navigation and layout changes
- **Performance Impact**: Monitoring of authentication overhead on existing endpoints

### Development Risks
- **TDD Discipline**: Strict adherence to test-first development
- **Constitution Compliance**: Regular review against architectural principles
- **Blueprint Isolation**: Careful management of cross-blueprint dependencies
- **Component Usage**: Consistent application of existing CSS component system

## Progress Tracking

### Phase 0: Research & Discovery
- [ ] Initial Constitution Check: PASS
- [ ] Database design research completed
- [ ] Authentication architecture research completed  
- [ ] Integration patterns research completed
- [ ] UI/UX component research completed

### Phase 1: Design & Architecture
- [ ] Database models designed and validated
- [ ] API contracts defined and documented
- [ ] Service layer architecture finalized
- [ ] UI templates designed using component system
- [ ] Post-Design Constitution Check: PASS

### Ready for Task Generation
- [ ] All research questions resolved
- [ ] No [NEEDS CLARIFICATION] items remaining
- [ ] Complete technical architecture documented
- [ ] Integration strategy finalized
- [ ] Ready for /tasks command execution

---

**Implementation Approach**: Service-layer first development with comprehensive testing, followed by API endpoints, then UI integration using established component patterns.

**Success Criteria**: Secure, scalable user system that integrates seamlessly with existing architecture while maintaining all constitutional principles and design standards.