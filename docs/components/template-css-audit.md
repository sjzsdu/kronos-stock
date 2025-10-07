# 模板CSS类使用审查系统

## 概述

本文档定义了Kronos股票系统中模板CSS类使用的审查标准和检查流程，确保项目遵循语义化CSS组件系统，禁止直接使用TailwindCSS原子类。

## 审查原则

### ✅ 推荐使用 - 语义化CSS类

**原则**: 模板中应使用预定义的语义化CSS组件类，而非直接的TailwindCSS原子类。

#### 表单组件类
```html
<!-- ✅ 正确 - 使用语义化类 -->
<form class="form">
    <div class="form-group">
        <label class="form-label">股票代码</label>
        <input class="form-input" type="text" />
        <span class="form-error">请输入正确的股票代码</span>
    </div>
    <button class="btn btn--primary">提交预测</button>
</form>

<!-- ❌ 错误 - 直接使用TailwindCSS -->
<form class="bg-white p-6 rounded-lg shadow-md">
    <div class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">股票代码</label>
        <input class="w-full px-3 py-2 border border-gray-300 rounded-md" type="text" />
        <span class="text-red-500 text-sm mt-1">请输入正确的股票代码</span>
    </div>
    <button class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded">提交预测</button>
</form>
```

#### 导航组件类
```html
<!-- ✅ 正确 - 语义化导航类 -->
<nav class="sidebar">
    <div class="nav-item nav-item--active">
        <i class="nav-item__icon fas fa-tachometer-alt"></i>
        <span>仪表板</span>
    </div>
    <div class="nav-submenu nav-submenu--show">
        <a class="nav-subitem nav-subitem--active">市场概览</a>
    </div>
</nav>

<!-- ❌ 错误 - TailwindCSS原子类 -->
<nav class="fixed left-0 top-0 h-full w-64 bg-gray-800 text-white">
    <div class="flex items-center px-4 py-2 bg-blue-600 text-blue-100">
        <i class="mr-3 fas fa-tachometer-alt"></i>
        <span>仪表板</span>
    </div>
    <div class="block">
        <a class="block px-6 py-2 text-blue-300 bg-blue-700">市场概览</a>
    </div>
</nav>
```

#### 模态框组件类
```html
<!-- ✅ 正确 - 语义化模态框类 -->
<div class="modal">
    <div class="modal__backdrop"></div>
    <div class="modal__container modal__container--medium">
        <div class="modal__content">
            <div class="modal__header">
                <h3 class="modal__title">确认操作</h3>
                <button class="modal__close"></button>
            </div>
            <div class="modal__body">
                <p class="modal__message">确定要删除此预测记录吗？</p>
            </div>
            <div class="modal__actions">
                <button class="btn btn--secondary">取消</button>
                <button class="btn btn--danger">删除</button>
            </div>
        </div>
    </div>
</div>

<!-- ❌ 错误 - 直接TailwindCSS -->
<div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-black bg-opacity-50"></div>
    <div class="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div class="flex items-center justify-between p-4 border-b">
            <h3 class="text-lg font-semibold">确认操作</h3>
            <button class="text-gray-400 hover:text-gray-600"></button>
        </div>
        <div class="p-4">
            <p class="text-gray-700">确定要删除此预测记录吗？</p>
        </div>
        <div class="flex justify-end space-x-2 p-4 border-t">
            <button class="px-4 py-2 bg-gray-300 text-gray-700 rounded">取消</button>
            <button class="px-4 py-2 bg-red-500 text-white rounded">删除</button>
        </div>
    </div>
</div>
```

### ❌ 禁止使用的模式

#### 1. 直接TailwindCSS原子类组合
```html
<!-- 禁止 -->
<div class="flex items-center justify-between p-4 bg-white rounded-lg shadow-md border">
<div class="w-full max-w-md mx-auto bg-gray-50 rounded-xl p-6">
<button class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
```

#### 2. 内联样式
```html
<!-- 禁止 -->
<div style="display: flex; padding: 1rem; background-color: white;">
<button style="background: #3b82f6; color: white; padding: 0.5rem 1rem;">
```

#### 3. 混合语义类和原子类
```html
<!-- 禁止混合使用 -->
<form class="form bg-white p-4 rounded-lg">
<button class="btn btn--primary hover:bg-blue-600 px-6">
```

## 语义化CSS类系统

### 组件命名约定

采用BEM (Block Element Modifier) 风格的语义化命名：

- **Block**: `.component` (如 `.form`, `.modal`, `.sidebar`)
- **Element**: `.component__element` (如 `.form__input`, `.modal__header`)  
- **Modifier**: `.component--modifier` (如 `.btn--primary`, `.form--loading`)

### 核心组件类库

#### 1. 表单组件 (`@layer components`)
```css
/* 表单容器 */
.form { /* 表单基础样式 */ }
.form--loading { /* 表单加载状态 */ }

/* 表单分组 */
.form-group { /* 表单字段分组 */ }
.form-group--inline { /* 内联表单组 */ }

/* 表单控件 */
.form-input { /* 输入框基础样式 */ }
.form-input--error { /* 输入框错误状态 */ }
.form-input--success { /* 输入框成功状态 */ }
.form-input--loading { /* 输入框加载状态 */ }

.form-select { /* 下拉选择框 */ }
.form-textarea { /* 文本区域 */ }
.form-checkbox { /* 复选框 */ }
.form-radio { /* 单选框 */ }

/* 表单标签和提示 */
.form-label { /* 表单标签 */ }
.form-hint { /* 表单提示文本 */ }
.form-error { /* 错误消息 */ }
.form-success { /* 成功消息 */ }
```

#### 2. 按钮组件
```css
/* 按钮基础 */
.btn { /* 按钮基础样式 */ }
.btn--primary { /* 主要按钮 */ }
.btn--secondary { /* 次要按钮 */ }
.btn--danger { /* 危险按钮 */ }
.btn--success { /* 成功按钮 */ }
.btn--ghost { /* 幽灵按钮 */ }

/* 按钮尺寸 */
.btn--sm { /* 小号按钮 */ }
.btn--lg { /* 大号按钮 */ }
.btn--xl { /* 超大按钮 */ }

/* 按钮状态 */
.btn--loading { /* 加载状态 */ }
.btn--disabled { /* 禁用状态 */ }
```

#### 3. 导航组件
```css
/* 侧边栏 */
.sidebar { /* 侧边栏容器 */ }
.sidebar--collapsed { /* 折叠状态 */ }

/* 导航项 */
.nav-item { /* 导航项基础样式 */ }
.nav-item--active { /* 活跃导航项 */ }
.nav-item__icon { /* 导航图标 */ }

/* 子菜单 */
.nav-submenu { /* 子菜单容器 */ }
.nav-submenu--show { /* 展开的子菜单 */ }
.nav-subitem { /* 子菜单项 */ }
.nav-subitem--active { /* 活跃子菜单项 */ }
```

#### 4. 模态框组件
```css
/* 模态框容器 */
.modal { /* 模态框基础容器 */ }
.modal--hidden { /* 隐藏状态 */ }
.modal__backdrop { /* 背景遮罩 */ }

/* 模态框内容 */
.modal__container { /* 模态框主容器 */ }
.modal__container--small { /* 小尺寸模态框 */ }
.modal__container--medium { /* 中等尺寸模态框 */ }
.modal__container--large { /* 大尺寸模态框 */ }

.modal__content { /* 内容区域 */ }
.modal__header { /* 头部区域 */ }
.modal__body { /* 主体区域 */ }
.modal__footer { /* 底部区域 */ }

.modal__title { /* 标题 */ }
.modal__close { /* 关闭按钮 */ }
.modal__actions { /* 动作按钮区 */ }
```

#### 5. 通知组件  
```css
/* 通知容器 */
.notification-center { /* 通知中心 */ }
.notification-list { /* 通知列表 */ }

/* 警告框 */
.alert { /* 警告框基础 */ }
.alert--success { /* 成功通知 */ }
.alert--error { /* 错误通知 */ }
.alert--warning { /* 警告通知 */ }
.alert--info { /* 信息通知 */ }

.alert__content { /* 通知内容 */ }
.alert__icon { /* 通知图标 */ }
.alert__body { /* 通知主体 */ }
.alert__title { /* 通知标题 */ }
.alert__message { /* 通知消息 */ }
.alert__close { /* 关闭按钮 */ }

/* Toast通知 */
.toast { /* Toast基础 */ }
.toast--show { /* 显示状态 */ }
.toast__progress { /* 进度条 */ }
```

#### 6. HTMX增强组件
```css
/* HTMX表单 */
.htmx-form { /* HTMX增强表单 */ }
.htmx-form--loading { /* 表单提交中 */ }
.htmx-form--success { /* 提交成功 */ }
.htmx-form--error { /* 提交失败 */ }

/* HTMX按钮 */
.htmx-btn { /* HTMX增强按钮 */ }
.htmx-btn--loading { /* 按钮加载中 */ }

/* HTMX容器 */
.htmx-container { /* HTMX内容容器 */ }
.htmx-container--loading { /* 内容加载中 */ }
.htmx-container--loaded { /* 内容已加载 */ }
```

## 自动化检查脚本

### CSS语义化检查脚本

位置: `.specify/scripts/bash/check-css-semantics.sh`

```bash
#!/bin/bash
# CSS语义化使用检查脚本
# 检查HTML模板中是否使用了禁止的TailwindCSS原子类

echo "🔍 检查模板CSS类使用情况..."

# 禁止使用的TailwindCSS模式
FORBIDDEN_PATTERNS=(
    "bg-\w+-\d+"           # 背景颜色类 如 bg-blue-500
    "text-\w+-\d+"         # 文字颜色类 如 text-red-600  
    "border-\w+-\d+"       # 边框颜色类 如 border-gray-300
    "p-\d+"                # 内边距 如 p-4, p-6
    "m-\d+"                # 外边距 如 m-4, m-auto
    "px-\d+"               # 水平内边距 如 px-4
    "py-\d+"               # 垂直内边距 如 py-2
    "w-\d+"                # 宽度 如 w-full, w-64
    "h-\d+"                # 高度 如 h-full, h-64
    "flex.*items-center"   # Flex布局组合
    "rounded-\w+"          # 圆角 如 rounded-lg, rounded-xl
    "shadow-\w+"           # 阴影 如 shadow-md, shadow-lg
)

# 检查的目录
TEMPLATE_DIRS=(
    "app/templates"
)

violations=0
total_files=0

# 扫描模板文件
for dir in "${TEMPLATE_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        echo "📂 扫描目录: $dir"
        
        while IFS= read -r -d '' file; do
            ((total_files++))
            echo "   🔍 检查: $file"
            
            # 检查每个禁止模式
            for pattern in "${FORBIDDEN_PATTERNS[@]}"; do
                matches=$(grep -n -E "class=\"[^\"]*$pattern" "$file" || true)
                
                if [[ -n "$matches" ]]; then
                    ((violations++))
                    echo "   ❌ 发现违规使用: $pattern"
                    echo "      文件: $file"
                    echo "$matches" | while read -r match; do
                        echo "      行: $match"
                    done
                    echo ""
                fi
            done
            
        done < <(find "$dir" -name "*.html" -print0)
    else
        echo "⚠️  目录不存在: $dir"
    fi
done

# 输出总结
echo ""
echo "📊 检查总结:"
echo "   检查文件数: $total_files"
echo "   发现违规: $violations 个"

if [[ $violations -eq 0 ]]; then
    echo "✅ 所有模板都符合语义化CSS使用规范!"
    exit 0
else
    echo "❌ 发现 $violations 个CSS使用违规，请修复后重新检查"
    echo ""
    echo "🔧 修复建议:"
    echo "   1. 将TailwindCSS原子类替换为预定义的语义化组件类"
    echo "   2. 参考 docs/components/template-css-audit.md 获取正确用法"
    echo "   3. 使用 assets/css/input.css 中定义的组件类"
    exit 1
fi
```

### 使用方法

#### 1. 开发阶段检查
```bash
# 检查所有模板文件
bash .specify/scripts/bash/check-css-semantics.sh

# 检查特定目录
bash .specify/scripts/bash/check-css-semantics.sh --dir app/templates/components
```

#### 2. Git提交前钩子
在 `.git/hooks/pre-commit` 中添加：
```bash
#!/bin/bash
echo "🔍 执行CSS语义化检查..."
bash .specify/scripts/bash/check-css-semantics.sh
if [[ $? -ne 0 ]]; then
    echo "❌ CSS语义化检查失败，请修复后重新提交"
    exit 1
fi
```

#### 3. CI/CD集成
在GitHub Actions或其他CI系统中：
```yaml
- name: CSS语义化检查
  run: |
    chmod +x .specify/scripts/bash/check-css-semantics.sh
    ./.specify/scripts/bash/check-css-semantics.sh
```

## 代码审查清单

### 模板审查要点

在代码审查时，重点检查以下方面：

#### ✅ 通过条件
- [ ] 使用预定义语义化CSS类 (`.form`, `.btn`, `.modal` 等)
- [ ] CSS类名遵循BEM命名约定
- [ ] 没有直接使用TailwindCSS原子类
- [ ] 没有内联样式 (`style="..."`)
- [ ] 组件结构清晰，语义明确
- [ ] 响应式行为通过CSS类控制
- [ ] 状态变化通过CSS类切换实现

#### ❌ 拒绝条件  
- [ ] 包含TailwindCSS原子类 (`bg-blue-500`, `p-4`, `flex` 等)
- [ ] 使用内联样式
- [ ] CSS类名不符合语义化约定
- [ ] 混合使用语义类和原子类
- [ ] JavaScript直接操作样式而非CSS类
- [ ] 硬编码尺寸和颜色值

### 审查流程

1. **自动检查**: 运行CSS语义化检查脚本
2. **手动审查**: 检查组件结构和语义合理性  
3. **测试验证**: 确保样式在不同设备和主题下正常工作
4. **文档更新**: 新组件类需要更新组件库文档

## 违规修复指南

### 常见违规修复示例

#### 修复表单样式
```html
<!-- 修复前 -->
<form class="bg-white p-6 rounded-lg shadow-md border">
    <div class="mb-4">
        <input class="w-full px-3 py-2 border rounded focus:border-blue-500" />
    </div>
    <button class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        提交
    </button>
</form>

<!-- 修复后 -->
<form class="form">
    <div class="form-group">
        <input class="form-input" />
    </div>
    <button class="btn btn--primary">
        提交
    </button>
</form>
```

#### 修复布局样式
```html
<!-- 修复前 -->
<div class="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
    <div class="flex items-center space-x-3">
        <div class="w-10 h-10 bg-blue-500 rounded-full"></div>
        <div>
            <h3 class="font-semibold text-gray-900">标题</h3>
            <p class="text-sm text-gray-500">描述</p>
        </div>
    </div>
</div>

<!-- 修复后 -->
<div class="card-item">
    <div class="card-item__content">
        <div class="avatar avatar--primary"></div>
        <div class="card-item__text">
            <h3 class="card-item__title">标题</h3>
            <p class="card-item__description">描述</p>
        </div>
    </div>
</div>
```

### 批量修复工具

创建简单的查找替换脚本：
```bash
#!/bin/bash
# 批量替换常见的违规模式

# 替换按钮样式
find app/templates -name "*.html" -exec sed -i 's/class="bg-blue-500[^"]*"/class="btn btn--primary"/g' {} \;

# 替换表单输入
find app/templates -name "*.html" -exec sed -i 's/class="w-full px-3 py-2[^"]*"/class="form-input"/g' {} \;

# 替换卡片容器  
find app/templates -name "*.html" -exec sed -i 's/class="bg-white[^"]*rounded[^"]*shadow[^"]*"/class="card"/g' {} \;

echo "✅ 批量修复完成，请检查结果并手动调整"
```

## 最佳实践

### 1. 开发工作流

1. **设计阶段**: 先定义语义化组件类，再实现HTML模板
2. **开发阶段**: 严格使用预定义CSS类，不使用原子类
3. **测试阶段**: 运行CSS语义化检查，确保合规性
4. **审查阶段**: 人工检查语义合理性和可维护性

### 2. 组件扩展原则

- **优先复用**: 使用现有组件类组合实现新需求
- **语义优先**: 新类名应体现组件功能而非视觉样式  
- **模块化**: 每个组件类应该独立、可复用
- **文档同步**: 新组件类必须同时更新文档

### 3. 团队协作规范

- **统一标准**: 所有成员必须遵循语义化CSS规范
- **代码审查**: 每次提交都需要通过CSS语义化检查
- **知识分享**: 定期分享组件使用最佳实践
- **工具支持**: 使用自动化工具减少人工检查成本

---

*本文档最后更新: 2025-01-07*
*版本: v1.0.0*