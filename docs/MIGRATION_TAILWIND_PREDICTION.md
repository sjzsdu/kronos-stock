# Tailwind CSS 迁移指南

## 简介

本文档记录了 Kronos 项目从传统 CSS 到 Tailwind CSS 的迁移过程，重点是预测页面 (prediction) 的重构。迁移目标是简化样式管理、提高可维护性，并为设计系统建立一致的基础。

## 设计 Token 映射

### 颜色

| 旧变量/命名      | Tailwind 映射                   | 用途                |
|-----------------|--------------------------------|-------------------|
| `--primary`     | `colors.primary`               | 品牌主色、按钮、强调  |
| `--up-color`    | `colors.up`                    | 上涨/看多趋势颜色    |
| `--down-color`  | `colors.down`                  | 下跌/看空趋势颜色    |
| `--gold-color`  | `colors.gold`                  | 目标价格突出显示     |
| `--neutral-*`   | `slate-50` 到 `slate-900`       | 中性色阶，替代灰度   |

### 阴影

| 旧变量/命名           | Tailwind 映射                    | 用途                |
|---------------------|--------------------------------|-------------------|
| `.card-shadow`      | `shadow-prediction`            | 预测卡片、主要内容块   |
| `.shadow-sm`        | `shadow-prediction-sm`         | 按钮、小组件的轻微阴影  |

### 圆角

使用 Tailwind 默认的圆角系统：
- `rounded-md` (6px) - 按钮、卡片
- `rounded-lg` (8px) - 大型卡片、预测结果容器
- `rounded-full` - 徽章、指示器

## 组件化策略

### 通过 @layer components 抽象的组件

```css
@layer components {
  .prediction-container {
    @apply max-w-5xl mx-auto px-4 py-6 md:py-8;
  }
  
  .prediction-section {
    @apply bg-white rounded-lg shadow-prediction p-5 md:p-6;
  }
  
  .prediction-chart-placeholder {
    @apply h-64 border border-slate-200 rounded-lg flex items-center justify-center bg-slate-50;
  }
  
  .prediction-form {
    @apply flex flex-col gap-5;
  }
  
  .form-group {
    @apply flex flex-col gap-2;
  }
  
  .loading-indicator {
    @apply flex items-center justify-center gap-2 text-primary py-4;
  }
  
  .btn-predict {
    @apply bg-primary text-white rounded-md px-5 py-3 font-medium shadow-prediction-sm hover:bg-primary-dark transition-colors;
  }
  
  .prediction-results {
    @apply mt-6 flex flex-col gap-4;
  }
}
```

### 使用纯工具类的元素

* 表单输入: `class="w-full px-4 py-2.5 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"`
* 表格: `class="w-full border-collapse divide-y divide-slate-200"`
* 表格行: `class="hover:bg-slate-50"`
* 趋势指示器: `class="inline-flex items-center gap-1 text-up font-medium"`

## 响应式断点策略

| 断点名称 | 宽度      | 用途                            |
|---------|----------|--------------------------------|
| `xs`    | 480px    | 极小屏幕（小型手机）            |
| `sm`    | 640px    | 小屏幕（默认 Tailwind）         |
| `md`    | 768px    | 中屏幕（平板）                 |
| `lg`    | 1024px   | 大屏幕（桌面）                 |

## 动态状态类映射

通过在模板中使用条件类名来动态应用样式：

```html
<span class="text-{{ 'up' if value > 0 else 'down' }}">{{ value }}%</span>
```

通用状态类推荐：

```
text-up - 用于上涨/增长/积极数值的文本颜色
text-down - 用于下跌/减少/消极数值的文本颜色
bg-up-50 - 轻微上涨背景色（用于徽章等）
bg-down-50 - 轻微下跌背景色
```

## 表格样式指南

预测结果表格应使用以下 Tailwind 工具类组合：

```html
<table class="w-full border-collapse divide-y divide-slate-200">
  <thead>
    <tr class="bg-slate-50">
      <th class="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">指标</th>
      <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">当前值</th>
      <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">预测值</th>
      <th class="px-4 py-3 text-center text-xs font-medium text-slate-500 uppercase tracking-wider">变化</th>
    </tr>
  </thead>
  <tbody class="bg-white divide-y divide-slate-200">
    <tr class="hover:bg-slate-50">
      <td class="px-4 py-3 whitespace-nowrap text-sm font-medium text-slate-900">收盘价</td>
      <td class="px-4 py-3 whitespace-nowrap text-sm text-center text-slate-700">{{ current_price }}</td>
      <td class="px-4 py-3 whitespace-nowrap text-sm text-center font-medium text-slate-900">{{ prediction.price }}</td>
      <td class="px-4 py-3 whitespace-nowrap text-sm text-center">
        <span class="text-{{ 'up' if prediction.change > 0 else 'down' }}">{{ prediction.change }}%</span>
      </td>
    </tr>
  </tbody>
</table>
```

## 错误与加载状态

### 加载指示器

```html
<div class="htmx-indicator loading-indicator">
  <i class="fas fa-spinner fa-spin"></i>
  <span>加载中...</span>
</div>
```

### 错误消息框

```html
<div class="bg-red-50 border border-red-200 text-red-700 rounded-md px-5 py-4 flex gap-4">
  <i class="fas fa-exclamation-circle text-lg"></i>
  <div>
    <h4 class="font-semibold">预测失败</h4>
    <p class="text-sm">{{ error_message }}</p>
  </div>
</div>
```

## 迁移步骤

1. **准备阶段**：配置 tailwind.config.cjs 并添加自定义扩展
2. **组件抽象**：在 assets/css/input.css 中定义关键组件
3. **页面改写**：重构 prediction.html 使用 Tailwind 工具类
4. **清理**：删除 prediction.css 并确认没有依赖
5. **回归测试**：确保跨设备显示一致且功能正常

## 注意事项

- 始终保持 JS 交互钩子类独立于视觉样式（例如：使用 .sidebar-toggle 类名而非纯视觉类）
- HTMX 指示器类 (hx-indicator) 已与 Tailwind 类集成
- 为避免样式冲突，已彻底移除旧 CSS 文件链接

## 后续建议

- 创建标准化组件库文档，便于团队参考
- 扩展 Tailwind 预设到其他页面和组件
- 考虑使用 PostCSS 插件进一步优化输出