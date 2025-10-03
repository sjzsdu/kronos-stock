
# Implementation Plan: 用户系统完善与优化

**Branch**: `002-user-system-enhancement` | **Date**: 2025-10-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-user-system-enhancement/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
基于已完成的用户系统(001-user-system)进行全面优化，重点提升UI/UX体验、代码复用率和系统架构。采用组件化重构和性能优化的技术方案，将现有功能完整的用户系统提升到生产级别的高质量应用。主要包括：统一设计语言系统、组件库建设、服务层解耦、性能优化和测试完善。

## Technical Context
**Language/Version**: Python 3.12+ with Flask 2.3.3 web framework
**Primary Dependencies**: Flask, SQLAlchemy, HTMX 1.x, TailwindCSS 3.x, PyTorch (CPU), bcrypt, PyJWT
**Storage**: SQLite (开发环境) / MySQL (生产环境), 现有数据库结构保持不变
**Testing**: pytest with markers (unit, integration, api, slow), 现有测试框架扩展
**Target Platform**: Linux服务器 + Docker部署, 支持现代浏览器 (Chrome, Firefox, Safari, Edge)
**Project Type**: Web应用 (Flask后端 + HTMX前端)
**Performance Goals**: 页面加载 <1.5秒, API响应 <500ms, 支持1500+并发用户
**Constraints**: 向后兼容现有API, 不破坏现有功能, 保持现有安全级别, 中文优先开发
**Scale/Scope**: 优化现有5个核心页面, 重构15+个组件, 优化10+个API端点

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### I. Service-Layer Architecture ✅
- 优化现有服务层架构，减少耦合度
- 业务逻辑保持在 `app/services/` 中
- 路由处理器只负责HTTP相关逻辑
- 服务方法独立可测试

### II. Blueprint Modularity ✅
- 基于现有蓝图架构进行优化
- API端点在 `app/api/` 遵循 `/api/*` 模式
- Web视图在 `app/views/` 兼容HTMX
- 组件化重构提升模块独立性

### III. Test-Driven Development ✅
- 遵循TDD循环：编写失败测试 → 最小实现 → 重构
- 使用pytest标记分类测试
- 优化和扩展现有测试覆盖率
- 新功能必须先写测试

### IV. Model Management & CPU-Only Inference ✅
- 保持现有AI模型操作为CPU-only
- 不修改现有模型管理系统
- 优化模型服务性能但不改变核心逻辑

### V. Data Validation & Financial Domain Rules ✅
- 保持现有数据验证规则
- 不修改股票代码验证逻辑
- 保持交易日处理和预测存储格式

### VI. Component-First UI Development ✅
- **重点优化项**：建立统一的组件系统
- 从 `assets/css/input.css` 优先使用组件类
- 建立 `.form-input`, `.btn-primary`, `.card` 等组件
- 使用 @layer components 结构
- 统一设计规范和命名约定

### VII. Chinese-First Development ✅
- 所有新代码和文档使用中文
- 代码注释、变量名、错误信息中文优先
- UI界面完全中文化
- 文档和测试用例使用中文

**评估结果**: 通过 - 所有宪法原则得到遵守，特别重点在组件化UI开发

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
# Web应用架构 - 基于现有Flask + HTMX结构优化
app/
├── models/              # 数据模型 (保持现有结构)
│   ├── user.py
│   └── prediction.py
├── services/            # 服务层 (重构优化)
│   ├── auth_service.py
│   ├── user_service.py
│   ├── password_service.py
│   └── ui_service.py    # 新增：UI组件服务
├── api/                 # API端点 (性能优化)
│   ├── auth.py
│   └── user.py
├── views/               # 视图控制器 (重构)
│   ├── auth.py
│   └── user.py
├── templates/           # 模板系统 (组件化重构)
│   ├── layouts/
│   ├── components/      # 重点：可复用组件
│   │   ├── forms/
│   │   ├── cards/
│   │   ├── buttons/
│   │   └── navigation/
│   ├── auth/
│   └── user/
├── static/              # 静态资源优化
│   ├── css/
│   │   ├── input.css    # 组件定义
│   │   └── tw.css       # 编译输出
│   └── js/
└── utils/               # 工具函数优化
    └── validators.py

assets/                  # 构建资源
├── css/
│   └── input.css        # TailwindCSS组件定义
└── js/

tests/                   # 测试体系扩展
├── unit/                # 单元测试
├── integration/         # 集成测试
├── ui/                  # UI组件测试 (新增)
└── performance/         # 性能测试 (新增)

docs/                    # 文档完善
├── components/          # 组件文档 (新增)
├── api/
└── user-system.md
```

**Structure Decision**: 选择Web应用架构，基于现有Flask+HTMX结构进行组件化优化。重点在templates/components/目录下建立可复用组件系统，同时优化assets/css/input.css的组件定义。保持现有目录结构的同时，增加UI组件相关的测试和文档支持。

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh copilot`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
基于Phase 1设计文档生成具体的实施任务列表：

1. **数据模型任务生成**:
   - 从 `data-model.md` 提取5个核心实体
   - 每个实体生成: 模型创建任务 [P]、迁移脚本任务 [P]、单元测试任务
   - 预计生成: 15个数据相关任务

2. **API合约任务生成**:
   - 从 `contracts/ui-components-api.yaml` 提取8个端点
   - 从 `contracts/htmx-views-api.yaml` 提取6个视图端点  
   - 每个端点生成: 合约测试任务 [P]、路由实现任务、集成测试任务
   - 预计生成: 42个API相关任务

3. **组件系统任务**:
   - 基于F002组件化需求，生成TailwindCSS组件类定义任务
   - UI组件模板重构任务 (按组件类型分组)
   - 组件服务层实现任务
   - 预计生成: 12个组件相关任务

4. **性能优化任务**:
   - 基于F004性能需求，生成缓存策略实施任务
   - 数据库查询优化任务
   - 静态资源优化任务
   - 预计生成: 8个性能相关任务

5. **测试体系任务**:
   - 基于F005测试需求和 `quickstart.md` 验收标准
   - UI组件测试框架搭建任务
   - 性能测试脚本任务
   - 集成测试场景实现任务
   - 预计生成: 10个测试相关任务

**Ordering Strategy**:
采用TDD驱动的分层实施顺序：

1. **Phase A: 基础设施** (并行执行)
   - 数据模型和迁移 [P]
   - 合约测试框架 [P] 
   - TailwindCSS组件类定义 [P]

2. **Phase B: 核心服务** (依赖Phase A)
   - UI服务层实现
   - 用户偏好服务
   - 性能监控服务
   - 组件缓存服务

3. **Phase C: API端点实现** (依赖Phase B，部分并行)
   - REST API端点 [P]
   - HTMX视图端点 [P]
   - 错误处理中间件

4. **Phase D: 前端优化** (依赖Phase C)
   - 组件模板重构
   - 样式系统优化  
   - 交互体验增强

5. **Phase E: 集成验证** (依赖Phase D)
   - 集成测试执行
   - 性能基准测试
   - 用户验收测试

**Task Metadata Standards**:
- 优先级: P0(阻塞), P1(重要), P2(一般)
- 并行标记: [P] 表示可并行执行
- 估时: S(< 2h), M(2-8h), L(> 8h)
- 依赖: 明确前置任务ID

**Quality Gates**:
- 每个Phase完成后运行自动化测试
- 性能基准验证 (页面加载 < 1.5s)
- 代码覆盖率检查 (> 85%)
- 组件复用率验证 (> 80%)

**Estimated Output**: 87个编号任务，分为5个执行阶段

**Risk Mitigation**:
- 关键路径识别和风险评估
- 回滚方案 (每个Phase可独立回滚)
- 并行任务冲突检测

**IMPORTANT**: 此规划将由 /tasks 命令执行，/plan 命令仅描述方法

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅ 2024-12-28
- [x] Phase 1: Design complete (/plan command) ✅ 2024-12-28  
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅ 2024-12-28
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅ 所有设计符合宪法原则
- [x] All NEEDS CLARIFICATION resolved ✅ research.md
- [x] Complexity deviations documented ✅ 无违反项

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*
