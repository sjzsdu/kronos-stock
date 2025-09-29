# 表单元素高度统一指南

## 问题描述
在 Kronos Stock 项目中，不同的表单元素（input、select、button）由于默认样式不同，会产生高度不一致的问题（42px、44px、40px等）。

## 解决方案

### 1. 使用统一高度系统
我们定义了 `.form-control-height` 基础类，统一使用 Tailwind 的 `h-11`（44px）高度：

```css
.form-control-height {
  @apply h-11 flex items-center;
}
```

### 2. 推荐的组合方式

#### 表单字段组合
使用这个组合确保所有表单元素高度一致：

```html
<!-- 输入框 -->
<input class="form-input" type="text">

<!-- 选择框 -->
<select class="form-select">
  <option>选项</option>
</select>

<!-- 按钮 -->
<button class="btn-primary btn-icon">
  <i class="fas fa-search"></i>
  搜索
</button>
```

#### 完整表单示例
```html
<form class="form-grid">
  <div class="form-field">
    <label class="form-label">日期</label>
    <input type="date" class="form-input">
  </div>
  
  <div class="form-field">
    <label class="form-label">类型</label>
    <select class="form-select">
      <option>全部</option>
      <option>选项1</option>
    </select>
  </div>
  
  <div class="form-field">
    <label class="form-label">&nbsp;</label>
    <button class="btn-primary btn-icon btn-full">
      <i class="fas fa-search"></i>
      查询
    </button>
  </div>
</form>
```

### 3. 快速类组合

#### 避免重复的基础样式
- **`.input-base`** - 输入框基础样式（边框、圆角、聚焦效果）
- **`.btn-base-style`** - 按钮基础样式（内边距、圆角、过渡、图标间距）

#### 使用示例
```html
<!-- 自定义输入框 -->
<input class="input-base form-control-height bg-gray-50" type="text">

<!-- 自定义按钮 -->
<button class="btn-base-style form-control-height bg-green-500 text-white hover:bg-green-600">
  <i class="fas fa-plus"></i>
  添加
</button>
```

### 4. 筛选器专用类
筛选器使用 `.filter-input` 和 `.filter-select`，自动继承统一高度：

```html
<div class="filter-container">
  <div class="filter-field">
    <label class="form-label">搜索</label>
    <input class="filter-input" placeholder="输入关键词">
  </div>
  
  <div class="filter-field">
    <label class="form-label">状态</label>
    <select class="filter-select">
      <option>全部</option>
    </select>
  </div>
</div>
```

## 最佳实践

### ✅ 推荐做法
```html
<!-- 使用组件类，高度自动统一 -->
<input class="form-input" type="text">
<select class="form-select">...</select>
<button class="btn-primary">按钮</button>
```

### ❌ 不推荐做法
```html
<!-- 手动写 Tailwind 类，容易高度不一致 -->
<input class="w-full px-3 py-2 border rounded-lg" type="text">
<select class="w-full px-3 py-1 border rounded-lg">...</select>
<button class="px-4 py-2 bg-blue-500 rounded-lg">按钮</button>
```

### 🔧 如需自定义
```html
<!-- 基于组件类进行扩展 -->
<input class="form-input bg-yellow-50 border-yellow-300" type="text">
<button class="btn-primary w-32">自定义宽度</button>
```

## 高度对齐原理

1. **统一基础高度**: 所有控件使用 `h-11` (44px)
2. **Flex 垂直居中**: 使用 `flex items-center` 确保内容垂直居中
3. **一致的内边距**: 按钮和输入框使用相同的水平内边距逻辑

## 兼容性说明

- 支持所有现代浏览器
- 移动端友好（touch-friendly 44px 最小触控目标）
- 键盘导航友好
- 屏幕阅读器兼容

这种方式既保证了高度统一，又保持了灵活性，避免了重复编写相同的样式代码。