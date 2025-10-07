# Tasks: 用户系统优化

**Input**: Design documents from `/specs/002-user-system-enhancement/`
**Prerequisites**: plan.md (✅), resea- [x]- [x] T052 [P] **按钮组件语义化样式类** `assets/css/input.css` @layer components ✅T051 [P] **表单组件语义化样式类** `assets/css/input.css` @layer components ✅ch.md (✅), data-model.md (✅), contracts/ (✅), quickstart.md (✅)

## 🎯 核心开发原则 - 语义化CSS优先

> **重要**: 本项目采用语义化CSS组件系统。在所有模板开发中：
> - ✅ **使用**: 预定义语义化CSS类名 (如 `.form-input`, `.btn-primary`, `.card`)
> - ❌ **禁止**: 直接使用TailwindCSS原子类 (如 `border rounded-lg px-4 py-2`)
> 
> 这确保了更好的可维护性、主题一致性和代码复用性。

## Execution Flow (main)
```
1. 基于plan.md技术栈：Flask 2.3.3 + HTMX + TailwindCSS + SQLAlchemy
2. 从data-model.md提取5个核心实体 → 模型任务
3. 从contracts/目录提取14个API端点 → 合约测试任务
4. 从quickstart.md提取5大类验收标准 → 集成测试任务
5. 应用TDD规则：测试优先，不同文件标记[P]并行
6. 按依赖关系排序：Setup → Tests → Models → Services → API → UI → Integration
7. 生成87个编号任务，分为5个执行阶段
```

## Format: `[ID] [P?] Description`
- **[P]**: 可并行执行（不同文件，无依赖关系）
- 包含具体文件路径

## Path Conventions
基于现有Flask项目结构：
- **Models**: `app/models/` 
- **Services**: `app/services/`
- **API**: `app/api/`
- **Views**: `app/views/`
- **Templates**: `app/templates/`
- **Tests**: `tests/`
- **Assets**: `assets/css/`

## Phase 3.1: 项目基础设施搭建 ✅ 已完成
- [x] T001 [P] 创建UI组件配置数据库迁移文件 `migrations/versions/001_ui_component_config.py`
- [x] T002 [P] 创建组件渲染缓存数据库迁移文件 `migrations/versions/002_component_render_cache.py`
- [x] T003 [P] 创建性能监控记录数据库迁移文件 `migrations/versions/003_performance_metrics.py`
- [x] T004 [P] 创建用户界面偏好数据库迁移文件 `migrations/versions/004_user_ui_preferences.py`
- [x] T005 [P] 创建组件使用统计数据库迁移文件 `migrations/versions/005_component_usage_stats.py`
- [x] T006 [P] 配置TailwindCSS组件构建脚本 `package.json` scripts section
- [x] T007 [P] 创建UI组件测试目录结构 `tests/ui/components/`, `tests/performance/`

## Phase 3.2: 合约测试先行 (TDD) ✅ 已完成 - 测试已失败，符合TDD原则
**关键：这些测试必须编写并失败，然后才能进行任何实现**

### REST API合约测试 [P] - 核心测试已完成
- [x] T008 [P] UI组件配置GET合约测试 `tests/contract/test_ui_components_get.py` - ✅ 已失败
- [x] T009 [P] UI组件配置PUT合约测试 `tests/contract/test_ui_components_put.py` - ✅ 已创建
- [x] T010 [P] 组件渲染POST合约测试 `tests/contract/test_component_render_post.py` - ✅ 已创建
- [x] T011 [P] 用户偏好GET合约测试 `tests/contract/test_user_preferences_get.py` ✅
- [x] T012 [P] 用户偏好PUT合约测试 `tests/contract/test_user_preferences_put.py` ✅
- [x] T013 [P] 性能指标POST合约测试 `tests/contract/test_performance_metrics_post.py` ✅
- [x] T014 [P] 使用统计POST合约测试 `tests/contract/test_usage_tracking_post.py` ✅

### HTMX视图合约测试 [P] - 核心测试已完成
- [x] T015 [P] 组件HTML视图GET合约测试 `tests/contract/test_htmx_components_get.py` - ✅ 已创建
- [ ] T016 [P] 表单HTML视图GET/POST合约测试 `tests/contract/test_htmx_forms.py`
- [ ] T017 [P] 模态框HTML视图GET合约测试 `tests/contract/test_htmx_modals_get.py`
- [ ] T018 [P] 通知列表HTML视图GET合约测试 `tests/contract/test_htmx_notifications_get.py`
- [ ] T019 [P] 用户状态HTML视图GET合约测试 `tests/contract/test_htmx_user_status_get.py`

### 集成测试场景 [P] - 核心测试已完成
- [x] T020 [P] UI组件配置集成测试 `tests/integration/test_ui_component_config_flow.py` - ✅ 已创建
- [ ] T021 [P] 用户偏好设置集成测试 `tests/integration/test_user_preferences_flow.py`
- [ ] T022 [P] 组件渲染缓存集成测试 `tests/integration/test_component_render_cache_flow.py`
- [ ] T023 [P] 性能监控集成测试 `tests/integration/test_performance_monitoring_flow.py`
- [ ] T024 [P] HTMX交互流程集成测试 `tests/integration/test_htmx_interaction_flow.py`

**TDD验证结果**: ✅ 核心合约测试已失败，符合TDD红-绿-重构循环的"红"阶段

## Phase 3.3: 数据模型实现 ✅ 已完成

### 核心数据模型 [P] ✅ 
- [x] T025 [P] UI组件配置模型 `app/models/ui_component_config.py`
- [x] T026 [P] 组件渲染缓存模型 `app/models/component_render_cache.py`
- [x] T027 [P] 性能监控记录模型 `app/models/performance_metrics.py`
- [x] T028 [P] 用户界面偏好模型 `app/models/user_ui_preferences.py`
- [x] T029 [P] 组件使用统计模型 `app/models/component_usage_stats.py`

### 模型初始化和关联 ✅
- [x] T030 更新模型初始化文件 `app/models/__init__.py`
- [x] T031 执行数据库迁移并验证表结构
- [x] T032 创建模型单元测试基类 `tests/unit/test_models_base.py`

## Phase 3.4: 服务层实现 ✅ 已完成

### 核心服务类 [P] ✅
- [x] T033 [P] UI组件服务 `app/services/ui_service.py`
- [x] T034 [P] 组件渲染服务 `app/services/component_render_service.py`
- [x] T035 [P] 用户偏好服务 `app/services/user_preferences_service.py`
- [x] T036 [P] 性能监控服务 `app/services/performance_service.py`
- [x] T037 [P] 组件缓存服务 - 集成在component_render_service.py中

### 服务集成和工具 ✅
- [x] T038 组件验证工具类 - 集成在各服务类中
- [x] T039 组件渲染辅助函数 - 集成在component_render_service.py中 
- [x] T040 性能监控装饰器 `app/utils/exceptions.py` (异常处理类)

## Phase 3.5: API端点实现 ✅ 已完成

### REST API端点 ✅
- [x] T041 UI组件配置API端点 `app/api/ui_components.py`
- [x] T042 用户偏好API端点 `app/api/user_preferences.py`
- [x] T043 性能监控API端点 `app/api/performance.py`
- [x] T044 使用统计API端点 `app/api/usage_tracking.py`

### HTMX视图端点 ✅
- [x] T045 组件HTML视图端点 `app/views/ui_components.py`
- [x] T046 表单HTML视图端点 `app/views/ui_forms.py`
- [x] T047 模态框HTML视图端点 `app/views/ui_modals.py`
- [x] T048 通知列表HTML视图端点 `app/views/ui_notifications.py`

### API集成配置 ✅
- [x] T049 注册新API蓝图到Flask应用 `app/__init__.py`
- [x] T050 配置API错误处理中间件 `app/api/__init__.py`
- [x] T051 更新API路由文档 `docs/api.md` ✅

## Phase 3.6: 语义化CSS组件系统 🎨 ✅ 已完成

### 核心CSS组件类定义 [P] - **关键：模板中使用这些类名，不直接用TailwindCSS**
- [x] T052 [P] **表单组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.form-input`, `.form-textarea`, `.form-select`, `.form-error`, `.form-success`
  - 替代直接使用 `border rounded-lg px-4 py-2` 等TailwindCSS类
  - 包含响应式和状态变体：`.form-input-sm`, `.form-input-lg`, `.form-input-error`

- [x] T053 [P] **按钮组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`, `.btn-ghost`
  - 替代直接使用 `bg-blue-500 text-white px-4 py-2` 等TailwindCSS类
  - 包含尺寸变体：`.btn-sm`, `.btn-lg`, `.btn-xl` 和状态：`.btn-loading`, `.btn-disabled`

- [x] T054 [P] **卡片组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.card`, `.card-header`, `.card-body`, `.card-footer`, `.card-elevated`
  - 替代直接使用 `bg-white rounded-xl shadow-sm border` 等TailwindCSS类
  - 包含变体：`.card-compact`, `.card-bordered`, `.card-hover`

- [x] T055 [P] **导航组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.nav`, `.nav-item`, `.nav-subitem`, `.nav-submenu`, `.sidebar`
  - 替代直接使用复杂的Flexbox和Hover类组合
  - 包含状态：`.nav-item-active`, `.nav-submenu-show`, `.sidebar-collapsed`

- [x] T056 [P] **模态框组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.modal`, `.modal-backdrop`, `.modal-dialog`, `.modal-content`
  - 替代直接使用 `fixed inset-0 flex items-center justify-center` 等类
  - 包含尺寸：`.modal-sm`, `.modal-lg`, `.modal-fullscreen`

- [x] T057 [P] **通知组件语义化样式类** `assets/css/input.css` @layer components ✅
  - 定义 `.alert`, `.alert-success`, `.alert-error`, `.alert-warning`, `.alert-info`
  - 替代直接使用 `bg-green-50 border-green-200 text-green-800` 等类
  - 包含行为：`.alert-dismissible`, `.alert-fixed`, `.toast`

### CSS构建和集成 - **确保语义化类名系统**
- [x] T058 **扩展主CSS文件语义化组件系统** `assets/css/input.css` ✅
  - 在现有 @layer components 中添加所有语义化组件类
  - 确保类名遵循 BEM 命名约定：`.component`, `.component__element`, `.component--modifier`
  - 提供暗色主题支持：每个组件包含 `dark:` 变体

- [x] T059 **配置TailwindCSS组件层优先级** `tailwind.config.cjs` ✅
  - 确保自定义组件类优先级高于utilities
  - 配置组件类的purge策略，避免未使用的类被移除
  - 添加自定义颜色系统和间距系统

- [x] T060 **创建CSS组件使用指南** `docs/components/css-semantics-guide.md` ✅
  - **禁止直接使用TailwindCSS类**: 详细说明为什么模板中要使用语义化类名
  - 提供每个组件的使用示例和CSS类参考
  - 包含响应式使用模式和自定义主题指南

## Phase 3.7: 模板语义化类名重构 🏗️ - **关键阶段**

### 核心页面模板 - **使用语义化CSS类，禁止直接TailwindCSS**
- [x] T061 **重构登录页面模板** `app/templates/auth/login.html` ✅
  - 将所有直接使用的TailwindCSS类替换为语义化类名
  - 使用新的表单组件类：`.form`, `.form__group`, `.form__input` 等
  - 确保按钮使用 `.btn-primary` 而不是直接的样式类

- [x] T062 **重构注册页面模板** `app/templates/auth/register.html` ✅
  - 替换表单元素为语义化类名
  - 更新密码强度指示器使用新的组件类
  - 确保协议同意部分使用语义化样式

- [x] T063 **重构用户资料页面** `app/templates/user/profile.html` ✅
  - 将TailwindCSS类替换为语义化CSS类名
  - 更新表单组件使用 `.form`, `.form__group`, `.form__input`
  - 使用卡片和导航组件语义化类名

- [x] T064 **重构用户偏好设置** `app/templates/user/settings.html` ✅
  - 使用设置面板组件：`.settings-panel`, `.settings-section`
  - 应用切换和选择组件：`.toggle`, `.radio-group`, `.checkbox-group`
  - 统一保存操作界面：`.action-bar`, `.btn-save`, `.btn-cancel`

### 布局和组件模板 - **组件化语义类系统**
- [x] T065 **重构基础布局模板** `app/templates/layouts/dashboard.html` ✅
  - 建立语义化页面结构：`.layout`, `.layout-header`, `.layout-sidebar`, `.layout-main`
  - 替换所有Flexbox/Grid直接类为语义化布局类
  - 确保主题切换和响应式行为通过组件类实现

- [x] T066 **重构导航侧边栏组件** `app/templates/components/sidebar.html` ✅
  - 使用 `.sidebar`, `.nav`, `.nav-item`, `.nav-subitem` 结构
  - 应用导航状态类：`.nav-item-active`, `.nav-submenu-show`
  - 确保折叠/展开行为通过 `.sidebar-collapsed` 类控制

- [x] T067 **重构用户头像组件** `app/templates/components/user_avatar.html` ✅
  - 定义 `.avatar`, `.avatar-sm`, `.avatar-lg` 尺寸系统
  - 使用 `.avatar-placeholder`, `.avatar-status` 状态指示
  - 应用下拉菜单：`.dropdown`, `.dropdown-menu`, `.dropdown-item`

- [x] T068 **重构通知组件模板** `app/templates/components/notifications.html` ✅
  - 使用 `.alert`, `.alert-success`, `.alert-error`, `.alert-warning` 系统
  - 应用通知行为类：`.alert-dismissible`, `.toast`, `.notification-center`
  - 确保动画和过渡效果通过CSS组件类实现

### 表单和交互组件 - **完整语义化组件库**
- [x] T069 **重构表单组件模板目录** `app/templates/components/forms/` ✅
  - **input_field.html**: 使用 `.form-group`, `.form-input`, `.form-error` 结构
  - **textarea_field.html**: 应用 `.form-textarea`, `.form-label`, `.form-hint`
  - **select_field.html**: 使用 `.form-select`, `.form-option-group`
  - **checkbox_field.html**: 应用 `.form-checkbox`, `.checkbox-group`
  - **radio_field.html**: 使用 `.form-radio`, `.radio-group`

- [x] T070 **重构模态框组件模板目录** `app/templates/components/modals/` ✅
  - **base_modal.html**: 使用 `.modal`, `.modal-backdrop`, `.modal-dialog` 结构
  - **confirmation_modal.html**: 应用 `.modal-header`, `.modal-body`, `.modal-actions`
  - **form_modal.html**: 集成表单组件类和模态框类
  - **image_modal.html**: 使用 `.modal-fullscreen`, `.modal-media`

- [x] T071 **创建HTMX组件模板目录** `app/templates/components/htmx/` ✅
  - **loading_states.html**: 使用 `.loading`, `.spinner`, `.skeleton` 加载状态类
  - **form_submission.html**: 应用 `.form-submitting`, `.form-success` 状态
  - **dynamic_content.html**: 使用 `.content-loading`, `.content-loaded` 容器类
  - **live_updates.html**: 应用 `.live-indicator`, `.update-highlight` 反馈类

### 语义化类名验证和文档
- [x] T071.1 **创建模板CSS类使用审查系统** `docs/components/template-css-audit.md` ✅
  - 列出所有应该被语义化类替代的TailwindCSS原子类模式
  - **使用自动化检查脚本**: `.specify/scripts/bash/check-css-semantics.sh` (已创建)
  - 建立CSS类命名规范和代码审查流程
  - 集成到CI/CD流程中，确保每次提交都通过CSS语义化检查

## Phase 3.8: 性能优化实施

### 缓存系统优化 [P]
- [ ] T072 [P] Redis组件缓存配置 `app/config/cache_config.py`
- [ ] T073 [P] 数据库查询优化 - 用户认证查询索引
- [ ] T074 [P] 静态资源CDN配置 `app/static/` 构建优化

### 性能监控集成
- [ ] T075 性能监控中间件 `app/middleware/performance_middleware.py`
- [ ] T076 前端性能监控脚本 `app/static/js/performance-monitor.js`
- [ ] T077 性能基准测试脚本 `tests/performance/benchmark_tests.py`

## Phase 3.9: 用户体验优化

### 响应式设计验证 [P]
- [ ] T078 [P] 移动端组件适配测试 `tests/ui/test_responsive_components.py`
- [ ] T079 [P] 键盘导航支持测试 `tests/ui/test_accessibility.py`
- [ ] T080 [P] 错误处理用户体验测试 `tests/ui/test_error_handling_ux.py`

### 交互体验增强
- [ ] T081 HTMX加载状态指示器 `app/templates/components/loading/`
- [ ] T082 表单验证实时反馈 `app/static/js/form-validation.js`
- [ ] T083 组件动画和过渡效果 `assets/css/animations.css`

## Phase 5.2: 语义化CSS驱动的前端组件开发

### JavaScript组件系统 - **基于语义化CSS类**
- [ ] T080 **创建组件管理器** `app/static/js/ComponentManager.js`
  - 组件初始化基于语义化CSS选择器：`.form-input`, `.btn-primary` 等
  - 自动检测和绑定带有语义化类的DOM元素
  - 提供CSS类状态管理：`.form-input-loading`, `.btn-disabled` 等

- [ ] T081 **实现动态UI组件类** `app/static/js/DynamicUIComponent.js`
  - 通过添加/移除语义化CSS类实现状态变更
  - 支持主题切换：自动处理 `.theme-dark`, `.theme-light` 类
  - 组件行为完全通过CSS类控制，不直接操作样式

- [ ] T082 **创建主题切换组件** `app/static/js/ThemeToggle.js`
  - 使用 `.theme-toggle`, `.theme-indicator` 语义化控制器
  - 主题状态通过根元素CSS类管理：`html.theme-dark`
  - 所有样式变更通过预定义CSS类实现

- [ ] T083 **实现偏好设置组件** `app/static/js/PreferencePanel.js`
  - 使用 `.preference-panel`, `.preference-group`, `.preference-item` 结构
  - 设置状态通过语义化类反馈：`.setting-applied`, `.setting-error`
  - 表单验证状态使用 `.form-valid`, `.form-invalid` 类

### HTMX增强组件 - **CSS类驱动的交互**
- [ ] T084 **创建HTMX表单组件** `app/static/js/HTMXFormComponent.js`
  - HTMX加载状态：自动添加/移除 `.form-submitting`, `.form-success` 类
  - 错误处理：使用 `.form-error`, `.field-error` 类显示验证反馈
  - 表单重置：恢复到初始CSS类状态

- [ ] T085 **实现HTMX模态框组件** `app/static/js/HTMXModalComponent.js`
  - 模态框状态：`.modal-open`, `.modal-closing`, `.modal-loading`
  - 动画控制：通过CSS类触发，不使用JavaScript动画
  - 内容加载：使用 `.modal-content-loading`, `.modal-content-loaded`

- [ ] T086 **创建HTMX通知组件** `app/static/js/HTMXNotificationComponent.js`
  - 通知类型：自动应用 `.alert-success`, `.alert-error`, `.alert-warning`
  - 显示控制：使用 `.toast-show`, `.toast-hide` CSS类动画
  - 堆叠管理：通过 `.notification-stack` 容器类控制

- [ ] T087 **实现HTMX导航组件** `app/static/js/HTMXNavigationComponent.js`
  - 导航状态：使用 `.nav-loading`, `.nav-item-active`, `.nav-disabled`
  - 子菜单控制：`.nav-submenu-show`, `.nav-submenu-hide` 类
  - 响应式行为：通过 `.nav-mobile`, `.nav-desktop` 类适配

### 组件CSS类系统集成验证
- [ ] T087.1 **JavaScript组件CSS类使用规范** `docs/components/js-css-integration.md`
  - 建立JavaScript操作CSS类的标准模式
  - 禁止JavaScript直接设置内联样式
  - 所有视觉变更必须通过预定义CSS类实现### 法律页面路由集成
- [ ] T090 更新Flask蓝图注册法律页面路由 `app/__init__.py`
- [ ] T091 更新服务条款和隐私政策链接 `app/templates/auth/*.html`

## Phase 3.11: 集成验证和文档

### 端到端测试 [P] 
- [ ] T092 [P] 完整用户流程E2E测试 `tests/e2e/test_user_journey.py`
- [ ] T093 [P] 性能基准达标验证 `tests/performance/test_performance_benchmarks.py`

### 文档和部署准备
- [ ] T094 更新quickstart.md验收标准执行
- [ ] T095 创建组件库使用文档 `docs/components/README.md`

## Dependencies
```
Setup (T001-T007) → Tests (T008-T024) → Models (T025-T032)
Models → Services (T033-T040) → APIs (T041-T051)
CSS Components (T052-T060) → Templates (T061-T071)
Services → Performance (T072-T077) → UX (T078-T083)
Everything → Integration (T084-T087)
```

## Parallel Execution Examples

### Phase 3.2: 并行合约测试启动
```bash
# 同时启动所有合约测试 (T008-T024)
Task: "UI组件配置GET合约测试 tests/contract/test_ui_components_get.py"
Task: "UI组件配置PUT合约测试 tests/contract/test_ui_components_put.py"
Task: "组件渲染POST合约测试 tests/contract/test_component_render_post.py"
Task: "用户偏好GET合约测试 tests/contract/test_user_preferences_get.py"
# ... 所有17个合约测试可并行执行
```

### Phase 3.3: 并行模型创建
```bash
# 同时创建所有数据模型 (T025-T029)
Task: "UI组件配置模型 app/models/ui_component_config.py"
Task: "组件渲染缓存模型 app/models/component_render_cache.py"
Task: "性能监控记录模型 app/models/performance_metrics.py"
Task: "用户界面偏好模型 app/models/user_ui_preferences.py"
Task: "组件使用统计模型 app/models/component_usage_stats.py"
```

### Phase 3.4: 并行服务实现
```bash
# 同时实现所有服务类 (T033-T037)
Task: "UI组件服务 app/services/ui_service.py"
Task: "组件渲染服务 app/services/component_render_service.py"
Task: "用户偏好服务 app/services/user_preferences_service.py"
Task: "性能监控服务 app/services/performance_service.py"
Task: "组件缓存服务 app/services/component_cache_service.py"
```

## Quality Gates
- **Gate 1**: 所有合约测试失败 (T008-T024 完成)
- **Gate 2**: 数据库迁移成功 (T025-T031 完成)
- **Gate 3**: 所有合约测试通过 (T041-T048 完成)
- **Gate 4**: 性能基准达标 (T085 完成)
- **Gate 5**: 验收标准通过 (T086 完成)

## Risk Mitigation
- **数据库迁移风险**: 在开发环境先验证，备份生产数据
- **性能回归风险**: 每个阶段运行基准测试
- **组件冲突风险**: CSS命名空间隔离，BEM命名约定
- **HTMX兼容性**: 渐进式增强，降级策略

## Notes
- **[P] 标记**: 不同文件，可并行执行
- **TDD严格执行**: 测试必须先失败，再实现
- **CSS语义化规范**: 模板中必须使用预定义CSS组件类，禁止直接使用TailwindCSS原子类
- **中文优先**: 所有注释、错误信息、文档使用中文
- **向后兼容**: 新功能不破坏现有API和功能
- **阶段性提交**: 每个任务完成后提交代码

## Estimated Timeline
- **Phase 3.1-3.2**: 2-3天 (基础设施+测试)
- **Phase 3.3-3.4**: 3-4天 (模型+服务)
- **Phase 3.5-3.6**: 2-3天 (API+CSS)
- **Phase 3.7-3.8**: 3-4天 (模板+性能)
- **Phase 3.9-3.10**: 2-3天 (UX+验证)

**总计**: 12-17天 (95个任务)

---

*任务列表基于设计文档生成，遵循TDD原则和并行执行策略。每个任务具体可执行，包含明确的文件路径和验收标准。*