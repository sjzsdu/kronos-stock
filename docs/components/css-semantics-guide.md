# CSS语义化组件系统使用指南

## 🚫 重要原则：禁止直接使用TailwindCSS类

**在模板文件中严格禁止直接使用TailwindCSS utility类**。必须使用预定义的语义化组件类。

### ❌ 错误的做法
```html
<!-- 禁止：直接使用TailwindCSS类 -->
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  提交
</button>

<div class="bg-white shadow-md rounded-lg p-6 border border-gray-200">
  <h3 class="text-lg font-semibold text-gray-900 mb-4">标题</h3>
  <p class="text-gray-600">内容</p>
</div>
```

### ✅ 正确的做法
```html
<!-- 正确：使用语义化组件类 -->
<button class="btn btn-primary">
  提交
</button>

<div class="card">
  <div class="card__header">
    <h3 class="card__title">标题</h3>
  </div>
  <div class="card__body">
    <p>内容</p>
  </div>
</div>
```

## 为什么使用语义化CSS类？

1. **一致性**：确保整个应用的视觉风格统一
2. **可维护性**：集中管理样式，修改设计系统时只需更改CSS文件
3. **可读性**：组件意图清晰，代码更容易理解
4. **主题支持**：自动支持暗色主题和响应式设计
5. **性能**：减少CSS bundle大小，提高加载速度

## 组件类别

### 1. 表单组件

#### 表单容器
```html
<!-- 基础表单 -->
<form class="form">
  <!-- 表单内容 -->
</form>

<!-- 紧凑表单 -->
<form class="form form--compact">
  <!-- 表单内容 -->
</form>

<!-- 内联表单 -->
<form class="form form--inline">
  <!-- 表单内容 -->
</form>
```

#### 表单组
```html
<!-- 垂直表单组 -->
<div class="form-group">
  <label class="form-label form-label--required">用户名</label>
  <input type="text" class="form-input" placeholder="请输入用户名">
  <p class="form-help">用户名长度为3-20个字符</p>
</div>

<!-- 水平表单组 -->
<div class="form-group form-group--horizontal">
  <label class="form-label">记住我</label>
  <input type="checkbox" class="form-checkbox">
</div>
```

#### 输入框
```html
<!-- 基础输入框 -->
<input type="text" class="form-input" placeholder="基础输入框">

<!-- 小尺寸输入框 -->
<input type="text" class="form-input form-input--sm" placeholder="小输入框">

<!-- 大尺寸输入框 -->
<input type="text" class="form-input form-input--lg" placeholder="大输入框">

<!-- 错误状态输入框 -->
<input type="text" class="form-input form-input--error" placeholder="错误输入框">
<div class="form-error">
  <i class="form-error__icon fas fa-exclamation-circle"></i>
  请输入有效的邮箱地址
</div>

<!-- 成功状态输入框 -->
<input type="text" class="form-input form-input--success" placeholder="成功输入框">
<div class="form-success">
  <i class="fas fa-check-circle"></i>
  输入格式正确
</div>

<!-- 禁用状态输入框 -->
<input type="text" class="form-input form-input--disabled" disabled placeholder="禁用输入框">
```

#### 多行文本框
```html
<!-- 基础文本框 -->
<textarea class="form-textarea" rows="4" placeholder="请输入内容"></textarea>

<!-- 可调整大小的文本框 -->
<textarea class="form-textarea form-textarea--resizable" rows="4"></textarea>
```

#### 选择框
```html
<select class="form-select">
  <option>请选择</option>
  <option value="1">选项1</option>
  <option value="2">选项2</option>
</select>
```

#### 复选框和单选按钮
```html
<!-- 复选框 -->
<div class="form-group">
  <label class="flex items-center">
    <input type="checkbox" class="form-checkbox">
    <span class="ml-2">同意服务条款</span>
  </label>
</div>

<!-- 单选按钮组 -->
<div class="form-group">
  <label class="form-label">性别</label>
  <div class="space-y-2">
    <label class="flex items-center">
      <input type="radio" name="gender" class="form-radio" value="male">
      <span class="ml-2">男</span>
    </label>
    <label class="flex items-center">
      <input type="radio" name="gender" class="form-radio" value="female">
      <span class="ml-2">女</span>
    </label>
  </div>
</div>
```

#### 开关按钮
```html
<button type="button" class="form-switch" onclick="toggleSwitch(this)">
  <span class="form-switch__toggle"></span>
</button>

<!-- 激活状态 -->
<button type="button" class="form-switch form-switch--active">
  <span class="form-switch__toggle"></span>
</button>
```

#### 文件上传
```html
<input type="file" class="form-file" accept="image/*">
```

### 2. 按钮组件

#### 基础按钮
```html
<!-- 主要按钮 -->
<button class="btn btn-primary">主要按钮</button>

<!-- 次要按钮 -->
<button class="btn btn-secondary">次要按钮</button>

<!-- 成功按钮 -->
<button class="btn btn-success">成功按钮</button>

<!-- 危险按钮 -->
<button class="btn btn-danger">危险按钮</button>

<!-- 警告按钮 -->
<button class="btn btn-warning">警告按钮</button>

<!-- 信息按钮 -->
<button class="btn btn-info">信息按钮</button>
```

#### 按钮尺寸
```html
<!-- 小按钮 -->
<button class="btn btn-primary btn--sm">小按钮</button>

<!-- 大按钮 -->
<button class="btn btn-primary btn--lg">大按钮</button>

<!-- 超大按钮 -->
<button class="btn btn-primary btn--xl">超大按钮</button>
```

#### 按钮样式变体
```html
<!-- 轮廓按钮 -->
<button class="btn btn-outline btn-primary">轮廓按钮</button>

<!-- 幽灵按钮 -->
<button class="btn btn-ghost">幽灵按钮</button>

<!-- 加载中按钮 -->
<button class="btn btn-primary btn--loading">加载中</button>
```

### 3. 卡片组件

#### 基础卡片
```html
<div class="card">
  <div class="card__header">
    <h3 class="card__title">卡片标题</h3>
    <p class="card__subtitle">卡片副标题</p>
  </div>
  <div class="card__body">
    <p>卡片内容区域</p>
  </div>
  <div class="card__footer">
    <button class="btn btn-primary">操作按钮</button>
  </div>
</div>
```

#### 卡片变体
```html
<!-- 带阴影的卡片 -->
<div class="card card--elevated">
  <div class="card__body">
    <p>带阴影的卡片</p>
  </div>
</div>

<!-- 悬停效果卡片 -->
<div class="card card--hover">
  <div class="card__body">
    <p>悬停时显示阴影</p>
  </div>
</div>
```

### 4. 导航组件

#### 水平导航
```html
<nav class="nav">
  <a href="#" class="nav-item nav-item--active">
    <i class="nav-item__icon fas fa-home"></i>
    首页
  </a>
  <a href="#" class="nav-item">
    <i class="nav-item__icon fas fa-chart-line"></i>
    预测
    <span class="nav-item__badge">3</span>
  </a>
  <a href="#" class="nav-item nav-item--disabled">
    <i class="nav-item__icon fas fa-cog"></i>
    设置
  </a>
</nav>
```

#### 垂直导航
```html
<nav class="nav nav--vertical">
  <a href="#" class="nav-item nav-item--active">
    <i class="nav-item__icon fas fa-home"></i>
    首页
  </a>
  <a href="#" class="nav-item">
    <i class="nav-item__icon fas fa-chart-line"></i>
    预测
  </a>
  <!-- 带子菜单的导航项 -->
  <div>
    <a href="#" class="nav-item">
      <i class="nav-item__icon fas fa-database"></i>
      数据管理
    </a>
    <nav class="nav-submenu nav-submenu--show">
      <a href="#" class="nav-subitem nav-subitem--active">股票数据</a>
      <a href="#" class="nav-subitem">市场分析</a>
    </nav>
  </div>
</nav>
```

#### 侧边栏
```html
<aside class="sidebar">
  <div class="sidebar__header">
    <h2>导航菜单</h2>
  </div>
  <div class="sidebar__content">
    <nav class="nav nav--vertical">
      <!-- 导航项 -->
    </nav>
  </div>
  <div class="sidebar__footer">
    <p>版权信息</p>
  </div>
</aside>
```

#### 面包屑导航
```html
<nav class="breadcrumb">
  <a href="#" class="breadcrumb__item">首页</a>
  <span class="breadcrumb__separator">/</span>
  <a href="#" class="breadcrumb__item">股票预测</a>
  <span class="breadcrumb__separator">/</span>
  <span class="breadcrumb__item breadcrumb__item--active">预测结果</span>
</nav>
```

#### 标签导航
```html
<nav class="tabs">
  <button class="tab tab--active">基本信息</button>
  <button class="tab">技术分析</button>
  <button class="tab">财务数据</button>
</nav>
```

### 5. 模态框组件

#### 基础模态框
```html
<div class="modal-backdrop">
  <div class="modal-dialog modal-dialog--md">
    <div class="modal-content">
      <div class="modal__header">
        <h3 class="modal__title">模态框标题</h3>
        <button class="modal__close">&times;</button>
      </div>
      <div class="modal__body">
        <p>模态框内容</p>
      </div>
      <div class="modal__footer">
        <button class="btn btn-secondary">取消</button>
        <button class="btn btn-primary">确认</button>
      </div>
    </div>
  </div>
</div>
```

#### 不同尺寸的模态框
```html
<!-- 小模态框 -->
<div class="modal-dialog modal-dialog--sm">
  <!-- 内容 -->
</div>

<!-- 大模态框 -->
<div class="modal-dialog modal-dialog--lg">
  <!-- 内容 -->
</div>

<!-- 全屏模态框 -->
<div class="modal-dialog modal-dialog--fullscreen">
  <!-- 内容 -->
</div>
```

### 6. 通知组件

#### 警告框
```html
<!-- 成功消息 -->
<div class="alert alert-success">
  <i class="alert__icon fas fa-check-circle"></i>
  <div class="alert__content">
    <div class="alert__title">操作成功</div>
    <div class="alert__message">数据已保存成功</div>
  </div>
  <button class="alert__close">&times;</button>
</div>

<!-- 错误消息 -->
<div class="alert alert-error">
  <i class="alert__icon fas fa-exclamation-circle"></i>
  <div class="alert__content">
    <div class="alert__title">操作失败</div>
    <div class="alert__message">请检查输入的数据格式</div>
  </div>
  <button class="alert__close">&times;</button>
</div>

<!-- 警告消息 -->
<div class="alert alert-warning">
  <i class="alert__icon fas fa-exclamation-triangle"></i>
  <div class="alert__content">
    <div class="alert__message">此操作不可撤销，请谨慎操作</div>
  </div>
</div>

<!-- 信息消息 -->
<div class="alert alert-info">
  <i class="alert__icon fas fa-info-circle"></i>
  <div class="alert__content">
    <div class="alert__message">系统将在5分钟后进行维护</div>
  </div>
</div>
```

#### Toast通知
```html
<div class="toast">
  <div class="toast__header">
    <span class="toast__title">通知标题</span>
    <button class="toast__close">&times;</button>
  </div>
  <div class="toast__body">
    通知内容
  </div>
  <div class="toast__progress" style="width: 50%;"></div>
</div>
```

#### 通知列表
```html
<div class="notification-list">
  <div class="notification-item notification-item--unread">
    <div class="notification-item__header">
      <span class="notification-item__title">新消息</span>
      <span class="notification-item__time">2分钟前</span>
    </div>
    <div class="notification-item__message">
      您有一条新的股票预测结果
    </div>
    <div class="notification-item__actions">
      <button class="btn btn--sm btn-primary">查看</button>
      <button class="btn btn--sm btn-secondary">忽略</button>
    </div>
  </div>
</div>
```

#### 徽章
```html
<!-- 基础徽章 -->
<span class="badge badge-primary">新</span>

<!-- 不同类型的徽章 -->
<span class="badge badge-success">成功</span>
<span class="badge badge-danger">错误</span>
<span class="badge badge-warning">警告</span>

<!-- 不同尺寸的徽章 -->
<span class="badge badge-primary badge--sm">小</span>
<span class="badge badge-primary badge--lg">大</span>
```

## 响应式设计

所有组件类都自带响应式支持。对于特殊的响应式需求，可以结合TailwindCSS的响应式前缀：

```html
<!-- 在移动端使用小按钮，桌面端使用大按钮 -->
<button class="btn btn-primary btn--sm md:btn--lg">
  响应式按钮
</button>

<!-- 在移动端垂直排列表单，桌面端水平排列 -->
<div class="form-group md:form-group--horizontal">
  <!-- 表单内容 -->
</div>
```

## 暗色主题

所有组件类都自动支持暗色主题。只需在根元素添加 `dark` 类：

```html
<html class="dark">
  <!-- 所有组件会自动应用暗色主题 -->
</html>
```

## 自定义扩展

如果需要创建新的组件变体，请在 `assets/css/input.css` 文件的 `@layer components` 区域添加：

```css
@layer components {
  /* 自定义按钮变体 */
  .btn-custom {
    @apply btn bg-purple-600 text-white border-purple-600 hover:bg-purple-700;
  }
  
  /* 自定义卡片变体 */
  .card--featured {
    @apply card border-2 border-primary bg-primary-light;
  }
}
```

## 组件类命名规范

遵循BEM（Block Element Modifier）命名约定：

- **Block（块）**：`.card`, `.btn`, `.form`
- **Element（元素）**：`.card__header`, `.btn__icon`, `.form__label`
- **Modifier（修饰符）**：`.btn--lg`, `.card--elevated`, `.form--inline`

## 调试和开发技巧

1. **使用浏览器开发工具**检查应用的组件类
2. **避免混用**语义化类和TailwindCSS utility类
3. **优先使用现有组件类**，确需自定义时才扩展
4. **保持一致性**，同类型的元素使用相同的组件类
5. **测试暗色主题**，确保在两种主题下都正常显示

## 常见问题

### Q: 为什么不能直接使用TailwindCSS类？
A: 直接使用utility类会导致样式分散、难以维护，且无法保证设计一致性。语义化类提供了更好的抽象层。

### Q: 如何处理特殊的样式需求？
A: 优先尝试组合现有的组件类。如果确实需要，可以在CSS文件中扩展新的组件类。

### Q: 组件类在暗色主题下不正常怎么办？
A: 检查是否正确添加了 `.dark` 前缀的样式定义，确保所有组件类都有对应的暗色变体。

### Q: 如何确保新的组件类不被Purge移除？
A: 在 `tailwind.config.cjs` 的 `safelist` 中添加相应的模式匹配规则。

---

**记住：始终使用语义化组件类，禁止在模板中直接使用TailwindCSS utility类！**