# 稳定布局架构设计

## 🎯 设计原则

**零弹动，完全稳定的嵌套布局系统**

- `base.html`: 负责上下结构（header + 内容区域）
- `sidebar.html`: 在内容区域中负责左右结构（aside + main）  
- 只有右侧 main 可以滚动
- 任何地方都不会出现页面弹动

## 📐 布局架构

### Base Layout (base.html)
```html
<body class="h-screen overflow-hidden">
  <div class="flex flex-col h-screen">
    <!-- Header: 固定高度 -->
    <header class="app-header">...</header>
    
    <!-- Content Area: 占满剩余空间 -->
    <div class="flex-1 overflow-hidden">
      {% block body %}{% endblock %}
    </div>
  </div>
</body>
```

### Sidebar Layout (sidebar.html)
```html
{% extends "layouts/base.html" %}
{% block body %}
<div class="flex h-full bg-gray-50">
  <!-- 左侧：固定宽度，内部可滚动 -->
  <aside class="sidebar-panel w-64">
    <div class="sidebar-content">...</div>
  </aside>
  
  <!-- 右侧：唯一外部滚动区域 -->
  <main class="flex-1 overflow-y-auto">
    {% block content %}{% endblock %}
  </main>
</div>
{% endblock %}
```

### Regular Page Layout
```html
{% extends "layouts/base.html" %}
{% block body %}
<div class="page-layout">
  <div class="page-content">
    <!-- 内容 -->
  </div>
</div>
{% endblock %}
```

## 🔧 CSS 组件类

### 布局容器
```css
/* Header 组件 */
.app-header {
  @apply flex-shrink-0 z-40 w-full border-b border-slate-200 
         bg-white/95 backdrop-blur shadow-sm;
}

/* 侧边栏组件 */  
.sidebar-panel {
  @apply flex-shrink-0 h-full overflow-hidden;
}

.sidebar-content {
  @apply h-full overflow-y-auto;
}

/* 页面布局 */
.page-layout {
  @apply h-full overflow-y-auto;
}

.page-content {
  @apply min-h-full p-6;
}
```

## 🎮 滚动控制规则

### 滚动层级
1. **body**: `overflow: hidden` - 禁用页面级滚动
2. **header**: `flex-shrink-0` - 绝不滚动，固定显示
3. **content area**: `flex-1 overflow-hidden` - 容器不滚动
4. **sidebar**: `overflow-hidden` 面板 + `overflow-y-auto` 内容
5. **main**: `overflow-y-auto` - 唯一的主滚动区域

### 布局稳定性
- **固定尺寸**: `h-screen`, `h-full` 确保精确高度
- **弹性布局**: `flex-1` 自动占满剩余空间
- **滚动隔离**: 每个滚动区域都有明确边界
- **无嵌套滚动**: 避免滚动区域嵌套造成的问题

## 📱 响应式策略

### 桌面端
- Header 固定在顶部
- Sidebar 固定在左侧（可折叠）
- Main 区域滚动

### 移动端  
- Header 固定在顶部
- Sidebar 变为叠加层导航
- Main 区域全宽滚动

## ✅ 测试检查点

### 布局稳定性测试
- [ ] 页面加载后无任何弹动
- [ ] 内容切换时布局不变形
- [ ] 侧边栏展开/收起无抖动
- [ ] 窗口大小调整时保持稳定

### 滚动行为测试  
- [ ] 只有指定区域可滚动
- [ ] Header 始终固定可见
- [ ] 侧边栏内容正确滚动
- [ ] 主内容区域滚动流畅
- [ ] 无双重滚动条出现

### 交互功能测试
- [ ] 移动端菜单正常工作
- [ ] 侧边栏折叠功能正常
- [ ] 键盘导航功能正常
- [ ] 无滚动穿透问题

## 🚀 使用指南

### 创建普通页面
```html
{% extends "layouts/base.html" %}
{% block body %}
<div class="page-layout">
  <div class="page-content">
    <h1>页面标题</h1>
    <!-- 内容会自动滚动 -->
  </div>
</div>
{% endblock %}
```

### 创建侧边栏页面
```html
{% extends "layouts/sidebar.html" %}
{% block content %}
<div class="p-6">
  <h1>管理面板</h1>
  <!-- 内容会在右侧滚动 -->
</div>  
{% endblock %}
```

这个架构确保了完全稳定、无弹动的用户体验！