前进度： [进行中] 1. 盘点现有样式与组件分组

建议执行顺序及说明：

盘点现有样式与组件分组 (进行中)
分组：布局容器 (prediction-page)、表单区块、结果区块、摘要卡片、趋势徽章、指标网格、图表容器、数据表、备注区、错误提示、加载指示、响应式规则。
定义设计 token 映射
把 CSS 变量 -> Tailwind：primary -> colors.primary；success/danger 对应现有 up/down；warning 用现有 warning；阴影映射到 shadow, 需要时扩展 shadow-light / shadow-medium。
规划组件化策略
纯 utility：表单、表格单元格、网格布局。
组件类：prediction-card / summary-card / trend-badge / metric / prediction-table-wrapper / error-box。
编写迁移分批计划
Phase 1：引入新组件类（不删旧 CSS），HTML 加上双类。
Phase 2：移除 HTML 里的旧类，保留新类。
Phase 3：删除未被引用的旧选择器。
Phase 4：文档与截图验证。
列出 Tailwind 类替换清单
e.g. .prediction-page -> max-w-6xl mx-auto p-5 md:p-6
.prediction-form -> bg-white rounded-md p-6 shadow-sm space-y-4
.form-group label -> block mb-1 font-medium text-slate-700
.btn-predict -> inline-flex items-center gap-2 bg-primary text-white text-sm font-medium px-5 py-2.5 rounded-md hover:bg-primary-dark transition
.prediction-chart -> h-72 flex items-center justify-center bg-slate-50 rounded-md text-slate-400
.summary-metrics -> grid gap-4 sm:grid-cols-2 lg:grid-cols-4
.metric -> flex flex-col items-center text-center bg-white/10 rounded-md p-3
.prediction-chart-container -> bg-white rounded-md p-5 shadow-sm
.prediction-data-table -> bg-white rounded-md p-5 shadow-sm
表格：table w-full text-xs md:text-sm border-collapse 等
新增/调整 tailwind.config.cjs
若需：添加 gradient（可用默认 bg-gradient-to-tr）。
加一个自定义阴影 key：'prediction': '0 4px 12px rgba(0,0,0,0.15)'。
在 input.css 添加组件层
@layer components 里加入：.prediction-card、.trend-badge-*、.metric、.prediction-table-wrapper。
重写 prediction.html 模板结构
移除 <link ... [prediction.css](http://_vscodecontentref_/7)>；替换所有旧类。
提取动态状态样式逻辑
模板中：class="change-value {{ 'text-up' if item.change>0 else 'text-down' }}"。
表格样式 Tailwind 化
thead: bg-slate-50 text-slate-600 text-xs font-semibold
zebra / hover: hover:bg-primary/5.
响应式方案替换
原 max-width 768 -> md:；480 -> sm:。
加载与状态指示统一
Loading: htmx-indicator inline-flex items-center gap-2 text-primary text-sm ml-3.
错误信息组件化
.error-box: flex gap-4 p-5 rounded-md border bg-red-50 border-red-200 text-red-700.
渐进式删除旧 CSS
使用 grep 确认无引用再删 prediction.css。
增加文档与迁移说明
新建 docs/MIGRATION_TAILWIND_PREDICTION.md。
回归测试与视觉检查
桌面 / iPhone 模拟宽度 / 早晚色（若有 dark mode）。
清理未使用的自定义变量
移除 prediction.css，保留需要的 gradient via utilities。
如果你希望，我可以继续把未完成项逐条推进并实际修改文件。告诉我是否现在继续执行下一步（例如完善 token 映射并给出具体 config 和组件代码片段）。需要我继续吗？