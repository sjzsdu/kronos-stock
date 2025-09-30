# 双布局系统使用指南

项目现在支持两种主要布局模式，每种都有最优化的滚动行为。

## 🎯 布局模式

### 1. 基础布局 (base.html)
**适用于**: 主页、预测页面、设置页面等不需要侧边栏的页面

**特点**:
- Header 固定在顶部
- Main 内容区域可滚动
- 完全响应式设计
- 移动端优化导航

**使用方法**:
```html
{% extends "layouts/base.html" %}

{% block body %}
<div class="page-content">
    <!-- 你的页面内容 -->
    <h1>页面标题</h1>
    <p>页面内容...</p>
</div>
{% endblock %}
```

### 2. 侧边栏布局 (sidebar.html)
**适用于**: 管理面板、数据展示、需要持久导航的页面

**特点**:
- 左侧固定宽度侧边栏
- 右侧主内容可滚动
- 侧边栏可折叠
- 全屏高度布局

**使用方法**:
```html
{% extends "layouts/sidebar.html" %}

{% block content %}
<!-- 直接放内容，无需额外容器 -->
<div class="p-6">
    <h1>管理面板</h1>
    <div>内容...</div>
</div>
{% endblock %}
```

## 🔧 技术实现

### 基础布局滚动策略
```css
.app-layout {
  @apply flex flex-col h-screen;  /* 全屏高度 */
}

.main-content {
  @apply flex-1 overflow-y-auto;  /* 主内容滚动 */
}

body {
  overflow: hidden;  /* 禁用外层滚动 */
}
```

### 侧边栏布局滚动策略
```css
.sidebar-layout {
  @apply absolute inset-0 flex;  /* 覆盖基础布局 */
}

.sidebar-aside {
  @apply flex-shrink-0 h-full;  /* 侧边栏固定 */
}

.sidebar-main {
  @apply flex-1 overflow-y-auto;  /* 主内容滚动 */
}
```

## 📱 响应式行为

### 基础布局
- **桌面**: Header + 滚动主内容
- **移动**: Header + 侧滑菜单 + 滚动主内容

### 侧边栏布局  
- **桌面**: 侧边栏 + 滚动主内容
- **移动**: 建议在移动端使用基础布局

## 🎨 样式组件

### 通用组件类
```css
.page-content       /* 标准页面内容容器 */
.app-header         /* 应用头部 */
.main-content       /* 主内容区域 */
.sidebar-layout     /* 侧边栏布局容器 */
.sidebar-main       /* 侧边栏主内容 */
.sidebar-aside      /* 侧边栏区域 */
```

### 使用示例

**基础页面**:
```html
{% extends "layouts/base.html" %}
{% block body %}
<div class="page-content">
    <div class="max-w-4xl mx-auto">
        <!-- 内容 -->
    </div>
</div>
{% endblock %}
```

**侧边栏页面**:
```html
{% extends "layouts/sidebar.html" %}
{% block content %}
<div class="p-6 max-w-full">
    <!-- 内容 -->
</div>
{% endblock %}
```

## ✅ 布局选择指南

| 页面类型 | 推荐布局 | 原因 |
|---------|---------|------|
| 首页/着陆页 | base.html | 需要干净的展示界面 |
| 预测界面 | base.html | 主要功能页面，需要最大内容空间 |
| 管理后台 | sidebar.html | 需要持久导航和多层级菜单 |
| 数据分析 | sidebar.html | 需要侧边工具栏和过滤器 |
| 设置页面 | base.html | 简单配置页面 |
| 用户资料 | base.html | 表单为主的页面 |

## 🚀 最佳实践

1. **内容组织**: 使用语义化的 HTML 结构
2. **滚动体验**: 让内容自然滚动，避免嵌套滚动
3. **响应式**: 考虑移动端的用户体验
4. **导航一致性**: 在同类型页面中保持布局一致

这个双布局系统为不同类型的页面提供了最优的用户体验！