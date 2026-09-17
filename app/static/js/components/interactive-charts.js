/**
 * 交互式图表组件
 * 支持多种交互功能：缩放、平移、选择、标注等
 */

class InteractiveCharts extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'InteractiveCharts';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            type: 'line', // line, candlestick, volume, scatter
            width: '100%',
            height: '400px',
            responsive: true,
            theme: 'light',
            
            // 交互功能
            enableZoom: true,
            enablePan: true,
            enableCrosshair: true,
            enableSelection: true,
            enableAnnotations: true,
            enableBrush: false,
            
            // 工具栏
            showToolbar: true,
            toolbarPosition: 'top', // top, bottom, left, right
            
            // 数据相关
            realTimeUpdate: false,
            maxDataPoints: 1000,
            
            // 样式
            colors: {
                primary: '#3b82f6',
                secondary: '#22c55e',
                danger: '#ef4444',
                warning: '#f59e0b',
                grid: '#e5e7eb',
                text: '#374151'
            },
            
            // 默认数据
            data: null
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // 图表相关
        this.chart = null;
        this.chartData = [];
        this.annotations = [];
        this.selectedRange = null;
        this.crosshairPosition = null;
        
        // 交互状态
        this.isZooming = false;
        this.isPanning = false;
        this.isSelecting = false;
        this.isAnnotating = false;
        
        // 工具状态
        this.currentTool = 'cursor';
        this.annotationMode = null;
        
        // 事件绑定
        this.boundHandlers = {
            resize: this.handleResize.bind(this),
            keydown: this.handleKeydown.bind(this),
            contextMenu: this.handleContextMenu.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            await this.loadDependencies();
            this.createContainer();
            this.createToolbar();
            this.setupEventListeners();
            
            if (this.config.data) {
                await this.setData(this.config.data);
            }
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化交互式图表组件失败');
            throw error;
        }
    }
    
    /**
     * 加载依赖库
     */
    async loadDependencies() {
        // 检查 D3.js
        if (typeof d3 === 'undefined') {
            await this.loadScript('https://d3js.org/d3.v7.min.js');
        }
        
        // 检查 Plotly.js（如果需要）
        if (this.config.type === 'candlestick' && typeof Plotly === 'undefined') {
            await this.loadScript('https://cdn.plot.ly/plotly-latest.min.js');
        }
    }
    
    /**
     * 加载脚本
     */
    loadScript(url) {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = url;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`无法加载脚本: ${url}`));
            document.head.appendChild(script);
        });
    }
    
    /**
     * 创建容器
     */
    createContainer() {
        this.container.className = `interactive-charts ${this.config.theme}`;
        this.container.innerHTML = `
            <div class="chart-wrapper">
                <div class="chart-toolbar" ${this.config.showToolbar ? '' : 'style="display: none;"'}></div>
                <div class="chart-container">
                    <div class="chart-canvas"></div>
                    <div class="chart-overlay">
                        <div class="crosshair-container">
                            <div class="crosshair-line crosshair-x"></div>
                            <div class="crosshair-line crosshair-y"></div>
                            <div class="crosshair-tooltip"></div>
                        </div>
                        <div class="selection-box"></div>
                        <div class="annotations-container"></div>
                    </div>
                </div>
                <div class="chart-info">
                    <div class="chart-status"></div>
                    <div class="chart-coordinates"></div>
                </div>
            </div>
        `;
        
        // 获取关键元素引用
        this.elements = {
            wrapper: this.container.querySelector('.chart-wrapper'),
            toolbar: this.container.querySelector('.chart-toolbar'),
            chartContainer: this.container.querySelector('.chart-container'),
            canvas: this.container.querySelector('.chart-canvas'),
            overlay: this.container.querySelector('.chart-overlay'),
            crosshair: {
                container: this.container.querySelector('.crosshair-container'),
                x: this.container.querySelector('.crosshair-x'),
                y: this.container.querySelector('.crosshair-y'),
                tooltip: this.container.querySelector('.crosshair-tooltip')
            },
            selectionBox: this.container.querySelector('.selection-box'),
            annotationsContainer: this.container.querySelector('.annotations-container'),
            status: this.container.querySelector('.chart-status'),
            coordinates: this.container.querySelector('.chart-coordinates')
        };
        
        // 设置容器尺寸
        this.elements.chartContainer.style.width = this.config.width;
        this.elements.chartContainer.style.height = this.config.height;
    }
    
    /**
     * 创建工具栏
     */
    createToolbar() {
        if (!this.config.showToolbar) return;
        
        const tools = [
            { id: 'cursor', icon: 'fas fa-mouse-pointer', title: '选择工具', group: 'basic' },
            { id: 'zoom', icon: 'fas fa-search-plus', title: '缩放工具', group: 'basic' },
            { id: 'pan', icon: 'fas fa-hand-paper', title: '平移工具', group: 'basic' },
            { id: 'crosshair', icon: 'fas fa-crosshairs', title: '十字线', group: 'basic', toggle: true },
            { id: 'separator1', type: 'separator' },
            { id: 'line', icon: 'fas fa-minus', title: '绘制直线', group: 'annotation' },
            { id: 'rectangle', icon: 'far fa-square', title: '绘制矩形', group: 'annotation' },
            { id: 'circle', icon: 'far fa-circle', title: '绘制圆形', group: 'annotation' },
            { id: 'text', icon: 'fas fa-font', title: '添加文本', group: 'annotation' },
            { id: 'separator2', type: 'separator' },
            { id: 'reset', icon: 'fas fa-home', title: '重置视图', group: 'action' },
            { id: 'fullscreen', icon: 'fas fa-expand', title: '全屏', group: 'action' },
            { id: 'download', icon: 'fas fa-download', title: '下载图表', group: 'action' }
        ];
        
        this.elements.toolbar.innerHTML = tools.map(tool => {
            if (tool.type === 'separator') {
                return '<div class="toolbar-separator"></div>';
            }
            
            return `
                <button class="toolbar-btn ${tool.toggle ? 'toggle-btn' : ''}" 
                        data-tool="${tool.id}" 
                        title="${tool.title}"
                        data-group="${tool.group}">
                    <i class="${tool.icon}"></i>
                </button>
            `;
        }).join('');
        
        // 设置默认激活工具
        this.setActiveTool('cursor');
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 工具栏事件
        if (this.config.showToolbar) {
            this.elements.toolbar.addEventListener('click', (e) => {
                const toolBtn = e.target.closest('.toolbar-btn');
                if (toolBtn) {
                    this.handleToolClick(toolBtn.dataset.tool);
                }
            });
        }
        
        // 图表容器事件
        const chartContainer = this.elements.chartContainer;
        
        // 鼠标事件
        chartContainer.addEventListener('mousedown', this.handleMouseDown.bind(this));
        chartContainer.addEventListener('mousemove', this.handleMouseMove.bind(this));
        chartContainer.addEventListener('mouseup', this.handleMouseUp.bind(this));
        chartContainer.addEventListener('mouseleave', this.handleMouseLeave.bind(this));
        chartContainer.addEventListener('wheel', this.handleWheel.bind(this));
        
        // 双击事件
        chartContainer.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        
        // 右键菜单
        chartContainer.addEventListener('contextmenu', this.boundHandlers.contextMenu);
        
        // 键盘事件
        document.addEventListener('keydown', this.boundHandlers.keydown);
        
        // 窗口大小变化
        if (this.config.responsive) {
            window.addEventListener('resize', this.boundHandlers.resize);
        }
    }
    
    /**
     * 设置数据
     */
    async setData(data) {
        try {
            this.chartData = this.processData(data);
            await this.renderChart();
            this.updateStatus('数据已加载');
            this.emit('dataChanged', { data: this.chartData });
        } catch (error) {
            this.handleError(error, '设置图表数据失败');
        }
    }
    
    /**
     * 处理数据
     */
    processData(rawData) {
        // 根据图表类型处理数据
        switch (this.config.type) {
            case 'line':
                return this.processLineData(rawData);
            case 'candlestick':
                return this.processCandlestickData(rawData);
            case 'volume':
                return this.processVolumeData(rawData);
            case 'scatter':
                return this.processScatterData(rawData);
            default:
                return rawData;
        }
    }
    
    /**
     * 处理线图数据
     */
    processLineData(data) {
        if (!Array.isArray(data)) return [];
        
        return data.map((d, i) => ({
            x: d.x !== undefined ? d.x : i,
            y: d.y !== undefined ? d.y : d,
            timestamp: d.timestamp || Date.now() + i * 1000,
            value: d.value || d.y || d
        }));
    }
    
    /**
     * 处理K线数据
     */
    processCandlestickData(data) {
        if (!Array.isArray(data)) return [];
        
        return data.map(d => ({
            timestamp: new Date(d.date || d.timestamp),
            open: parseFloat(d.open),
            high: parseFloat(d.high),
            low: parseFloat(d.low),
            close: parseFloat(d.close),
            volume: parseInt(d.volume || 0)
        }));
    }
    
    /**
     * 处理成交量数据
     */
    processVolumeData(data) {
        return this.processCandlestickData(data).map(d => ({
            timestamp: d.timestamp,
            volume: d.volume,
            price: d.close
        }));
    }
    
    /**
     * 处理散点图数据
     */
    processScatterData(data) {
        if (!Array.isArray(data)) return [];
        
        return data.map(d => ({
            x: parseFloat(d.x),
            y: parseFloat(d.y),
            size: d.size || 3,
            color: d.color || this.config.colors.primary
        }));
    }
    
    /**
     * 渲染图表
     */
    async renderChart() {
        if (!this.chartData || this.chartData.length === 0) return;
        
        // 清除现有图表
        this.elements.canvas.innerHTML = '';
        
        // 根据图表类型选择渲染方法
        switch (this.config.type) {
            case 'line':
                await this.renderLineChart();
                break;
            case 'candlestick':
                await this.renderCandlestickChart();
                break;
            case 'volume':
                await this.renderVolumeChart();
                break;
            case 'scatter':
                await this.renderScatterChart();
                break;
        }
        
        this.setupChartInteractions();
    }
    
    /**
     * 渲染线图
     */
    async renderLineChart() {
        const margin = { top: 20, right: 20, bottom: 30, left: 50 };
        const width = this.elements.canvas.clientWidth - margin.left - margin.right;
        const height = this.elements.canvas.clientHeight - margin.top - margin.bottom;
        
        // 创建SVG
        const svg = d3.select(this.elements.canvas)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // 创建比例尺
        const xScale = d3.scaleLinear()
            .domain(d3.extent(this.chartData, d => d.x))
            .range([0, width]);
        
        const yScale = d3.scaleLinear()
            .domain(d3.extent(this.chartData, d => d.y))
            .range([height, 0]);
        
        // 存储比例尺供交互使用
        this.scales = { x: xScale, y: yScale };
        
        // 创建线条生成器
        const line = d3.line()
            .x(d => xScale(d.x))
            .y(d => yScale(d.y))
            .curve(d3.curveMonotoneX);
        
        // 绘制网格
        if (this.config.showGrid !== false) {
            // X轴网格
            g.selectAll('.grid-x')
                .data(xScale.ticks())
                .enter().append('line')
                .attr('class', 'grid-x')
                .attr('x1', d => xScale(d))
                .attr('x2', d => xScale(d))
                .attr('y1', 0)
                .attr('y2', height)
                .style('stroke', this.config.colors.grid)
                .style('stroke-width', 1);
            
            // Y轴网格
            g.selectAll('.grid-y')
                .data(yScale.ticks())
                .enter().append('line')
                .attr('class', 'grid-y')
                .attr('x1', 0)
                .attr('x2', width)
                .attr('y1', d => yScale(d))
                .attr('y2', d => yScale(d))
                .style('stroke', this.config.colors.grid)
                .style('stroke-width', 1);
        }
        
        // 绘制线条
        g.append('path')
            .datum(this.chartData)
            .attr('class', 'line-path')
            .attr('fill', 'none')
            .attr('stroke', this.config.colors.primary)
            .attr('stroke-width', 2)
            .attr('d', line);
        
        // 绘制数据点
        g.selectAll('.data-point')
            .data(this.chartData)
            .enter().append('circle')
            .attr('class', 'data-point')
            .attr('cx', d => xScale(d.x))
            .attr('cy', d => yScale(d.y))
            .attr('r', 3)
            .style('fill', this.config.colors.primary)
            .style('stroke', '#fff')
            .style('stroke-width', 1);
        
        // 创建坐标轴
        g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));
        
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale));
        
        this.chart = { svg, g, width, height, margin };
    }
    
    /**
     * 渲染K线图
     */
    async renderCandlestickChart() {
        // 使用Plotly渲染K线图
        if (typeof Plotly === 'undefined') {
            throw new Error('Plotly.js 库未加载');
        }
        
        const trace = {
            x: this.chartData.map(d => d.timestamp),
            open: this.chartData.map(d => d.open),
            high: this.chartData.map(d => d.high),
            low: this.chartData.map(d => d.low),
            close: this.chartData.map(d => d.close),
            type: 'candlestick',
            name: 'OHLC',
            increasing: { line: { color: this.config.colors.secondary } },
            decreasing: { line: { color: this.config.colors.danger } }
        };
        
        const layout = {
            title: '',
            xaxis: { title: '时间' },
            yaxis: { title: '价格' },
            showlegend: false,
            margin: { l: 50, r: 20, t: 20, b: 50 }
        };
        
        const config = {
            responsive: true,
            displayModeBar: false
        };
        
        await Plotly.newPlot(this.elements.canvas, [trace], layout, config);
        
        this.chart = { plotly: true };
    }
    
    /**
     * 渲染成交量图
     */
    async renderVolumeChart() {
        const margin = { top: 20, right: 20, bottom: 30, left: 50 };
        const width = this.elements.canvas.clientWidth - margin.left - margin.right;
        const height = this.elements.canvas.clientHeight - margin.top - margin.bottom;
        
        const svg = d3.select(this.elements.canvas)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // 时间和成交量比例尺
        const xScale = d3.scaleBand()
            .domain(this.chartData.map(d => d.timestamp))
            .range([0, width])
            .padding(0.1);
        
        const yScale = d3.scaleLinear()
            .domain([0, d3.max(this.chartData, d => d.volume)])
            .range([height, 0]);
        
        this.scales = { x: xScale, y: yScale };
        
        // 绘制柱状图
        g.selectAll('.volume-bar')
            .data(this.chartData)
            .enter().append('rect')
            .attr('class', 'volume-bar')
            .attr('x', d => xScale(d.timestamp))
            .attr('y', d => yScale(d.volume))
            .attr('width', xScale.bandwidth())
            .attr('height', d => height - yScale(d.volume))
            .style('fill', this.config.colors.primary)
            .style('opacity', 0.7);
        
        // 创建坐标轴
        g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale).tickFormat(d3.timeFormat('%H:%M')));
        
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale));
        
        this.chart = { svg, g, width, height, margin };
    }
    
    /**
     * 渲染散点图
     */
    async renderScatterChart() {
        const margin = { top: 20, right: 20, bottom: 30, left: 50 };
        const width = this.elements.canvas.clientWidth - margin.left - margin.right;
        const height = this.elements.canvas.clientHeight - margin.top - margin.bottom;
        
        const svg = d3.select(this.elements.canvas)
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom);
        
        const g = svg.append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // 创建比例尺
        const xScale = d3.scaleLinear()
            .domain(d3.extent(this.chartData, d => d.x))
            .range([0, width]);
        
        const yScale = d3.scaleLinear()
            .domain(d3.extent(this.chartData, d => d.y))
            .range([height, 0]);
        
        this.scales = { x: xScale, y: yScale };
        
        // 绘制散点
        g.selectAll('.scatter-point')
            .data(this.chartData)
            .enter().append('circle')
            .attr('class', 'scatter-point')
            .attr('cx', d => xScale(d.x))
            .attr('cy', d => yScale(d.y))
            .attr('r', d => d.size)
            .style('fill', d => d.color)
            .style('stroke', '#fff')
            .style('stroke-width', 1);
        
        // 创建坐标轴
        g.append('g')
            .attr('class', 'x-axis')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));
        
        g.append('g')
            .attr('class', 'y-axis')
            .call(d3.axisLeft(yScale));
        
        this.chart = { svg, g, width, height, margin };
    }
    
    /**
     * 设置图表交互
     */
    setupChartInteractions() {
        if (!this.chart || this.chart.plotly) return;
        
        // 缩放和平移
        if (this.config.enableZoom || this.config.enablePan) {
            const zoom = d3.zoom()
                .scaleExtent([0.1, 10])
                .on('zoom', (event) => this.handleZoom(event));
            
            this.chart.svg.call(zoom);
        }
    }
    
    /**
     * 处理工具点击
     */
    handleToolClick(toolId) {
        switch (toolId) {
            case 'cursor':
            case 'zoom':
            case 'pan':
                this.setActiveTool(toolId);
                break;
            case 'crosshair':
                this.toggleCrosshair();
                break;
            case 'line':
            case 'rectangle':
            case 'circle':
            case 'text':
                this.setActiveTool('annotation');
                this.annotationMode = toolId;
                break;
            case 'reset':
                this.resetView();
                break;
            case 'fullscreen':
                this.toggleFullscreen();
                break;
            case 'download':
                this.downloadChart();
                break;
        }
    }
    
    /**
     * 设置激活工具
     */
    setActiveTool(tool) {
        this.currentTool = tool;
        
        // 更新工具栏UI
        this.elements.toolbar.querySelectorAll('.toolbar-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = this.elements.toolbar.querySelector(`[data-tool="${tool}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
        
        // 更新光标样式
        this.updateCursor();
        
        this.emit('toolChanged', { tool });
    }
    
    /**
     * 更新光标样式
     */
    updateCursor() {
        const cursors = {
            cursor: 'default',
            zoom: 'zoom-in',
            pan: 'move',
            annotation: 'crosshair'
        };
        
        this.elements.chartContainer.style.cursor = cursors[this.currentTool] || 'default';
    }
    
    /**
     * 处理鼠标按下事件
     */
    handleMouseDown(event) {
        event.preventDefault();
        
        const rect = this.elements.chartContainer.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        switch (this.currentTool) {
            case 'zoom':
                this.startSelection(x, y);
                break;
            case 'pan':
                this.startPanning(x, y);
                break;
            case 'annotation':
                this.startAnnotation(x, y);
                break;
        }
    }
    
    /**
     * 处理鼠标移动事件
     */
    handleMouseMove(event) {
        const rect = this.elements.chartContainer.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // 更新十字线
        if (this.config.enableCrosshair) {
            this.updateCrosshair(x, y);
        }
        
        // 更新坐标显示
        this.updateCoordinates(x, y);
        
        // 处理拖拽操作
        if (this.isSelecting) {
            this.updateSelection(x, y);
        } else if (this.isPanning) {
            this.updatePanning(x, y);
        } else if (this.isAnnotating) {
            this.updateAnnotation(x, y);
        }
    }
    
    /**
     * 处理鼠标抬起事件
     */
    handleMouseUp(event) {
        if (this.isSelecting) {
            this.endSelection();
        } else if (this.isPanning) {
            this.endPanning();
        } else if (this.isAnnotating) {
            this.endAnnotation();
        }
    }
    
    /**
     * 处理鼠标离开事件
     */
    handleMouseLeave(event) {
        this.hideCrosshair();
        this.elements.coordinates.textContent = '';
    }
    
    /**
     * 处理滚轮事件
     */
    handleWheel(event) {
        if (!this.config.enableZoom) return;
        
        event.preventDefault();
        
        const delta = event.deltaY > 0 ? 0.9 : 1.1;
        this.zoomChart(delta, event.offsetX, event.offsetY);
    }
    
    /**
     * 处理双击事件
     */
    handleDoubleClick(event) {
        if (this.currentTool === 'zoom') {
            this.resetView();
        }
    }
    
    /**
     * 处理右键菜单
     */
    handleContextMenu(event) {
        event.preventDefault();
        
        // 显示自定义右键菜单
        this.showContextMenu(event.clientX, event.clientY);
    }
    
    /**
     * 处理键盘事件
     */
    handleKeydown(event) {
        if (!this.container.contains(document.activeElement)) return;
        
        switch (event.key) {
            case 'Escape':
                this.cancelCurrentOperation();
                break;
            case 'Delete':
                this.deleteSelectedAnnotations();
                break;
            case 'c':
                if (event.ctrlKey || event.metaKey) {
                    this.copySelection();
                }
                break;
            case 'v':
                if (event.ctrlKey || event.metaKey) {
                    this.pasteSelection();
                }
                break;
        }
    }
    
    /**
     * 更新十字线
     */
    updateCrosshair(x, y) {
        if (!this.config.enableCrosshair) return;
        
        this.elements.crosshair.container.style.display = 'block';
        this.elements.crosshair.x.style.left = `${x}px`;
        this.elements.crosshair.y.style.top = `${y}px`;
        
        // 显示工具提示
        if (this.scales) {
            const dataX = this.scales.x.invert ? this.scales.x.invert(x - this.chart.margin.left) : x;
            const dataY = this.scales.y.invert ? this.scales.y.invert(y - this.chart.margin.top) : y;
            
            this.elements.crosshair.tooltip.textContent = `(${dataX.toFixed(2)}, ${dataY.toFixed(2)})`;
            this.elements.crosshair.tooltip.style.left = `${x + 10}px`;
            this.elements.crosshair.tooltip.style.top = `${y - 30}px`;
            this.elements.crosshair.tooltip.style.display = 'block';
        }
    }
    
    /**
     * 隐藏十字线
     */
    hideCrosshair() {
        this.elements.crosshair.container.style.display = 'none';
        this.elements.crosshair.tooltip.style.display = 'none';
    }
    
    /**
     * 切换十字线
     */
    toggleCrosshair() {
        this.config.enableCrosshair = !this.config.enableCrosshair;
        
        const btn = this.elements.toolbar.querySelector('[data-tool="crosshair"]');
        if (btn) {
            btn.classList.toggle('active', this.config.enableCrosshair);
        }
        
        if (!this.config.enableCrosshair) {
            this.hideCrosshair();
        }
    }
    
    /**
     * 更新坐标显示
     */
    updateCoordinates(x, y) {
        if (this.scales) {
            const dataX = this.scales.x.invert ? this.scales.x.invert(x - this.chart.margin.left) : x;
            const dataY = this.scales.y.invert ? this.scales.y.invert(y - this.chart.margin.top) : y;
            
            this.elements.coordinates.textContent = `X: ${dataX.toFixed(2)}, Y: ${dataY.toFixed(2)}`;
        }
    }
    
    /**
     * 重置视图
     */
    resetView() {
        if (this.chart && this.chart.svg && !this.chart.plotly) {
            // D3图表重置
            this.chart.svg.transition().duration(750)
                .call(d3.zoom().transform, d3.zoomIdentity);
        } else if (this.chart && this.chart.plotly) {
            // Plotly图表重置
            Plotly.Fx.hover(this.elements.canvas, []);
            Plotly.relayout(this.elements.canvas, {
                'xaxis.autorange': true,
                'yaxis.autorange': true
            });
        }
        
        this.updateStatus('视图已重置');
    }
    
    /**
     * 切换全屏
     */
    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            this.container.requestFullscreen();
        }
    }
    
    /**
     * 下载图表
     */
    downloadChart() {
        if (this.chart && this.chart.plotly) {
            // Plotly图表下载
            Plotly.downloadImage(this.elements.canvas, {
                format: 'png',
                width: 1200,
                height: 800,
                filename: `chart_${Date.now()}`
            });
        } else if (this.chart && this.chart.svg) {
            // D3/SVG图表下载
            this.downloadSVGChart();
        }
    }
    
    /**
     * 下载SVG图表
     */
    downloadSVGChart() {
        const svgData = new XMLSerializer().serializeToString(this.chart.svg.node());
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        
        img.onload = () => {
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
            
            const link = document.createElement('a');
            link.download = `chart_${Date.now()}.png`;
            link.href = canvas.toDataURL();
            link.click();
        };
        
        img.src = 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svgData)));
    }
    
    /**
     * 更新状态
     */
    updateStatus(message) {
        this.elements.status.textContent = message;
        setTimeout(() => {
            this.elements.status.textContent = '';
        }, 3000);
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        if (this.config.responsive) {
            setTimeout(() => {
                this.renderChart();
            }, 100);
        }
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 移除事件监听器
        window.removeEventListener('resize', this.boundHandlers.resize);
        document.removeEventListener('keydown', this.boundHandlers.keydown);
        
        // 销毁图表
        if (this.chart && this.chart.plotly) {
            Plotly.purge(this.elements.canvas);
        }
        
        super.destroy();
    }
}

// 注册组件
if (typeof JSComponentManager !== 'undefined') {
    JSComponentManager.register('interactive-charts', InteractiveCharts);
}

// 导出组件（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InteractiveCharts;
}