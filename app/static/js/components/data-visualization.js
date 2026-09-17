/**
 * 数据可视化组件
 * 支持多种图表类型和实时数据更新
 */

class DataVisualization extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'DataVisualization';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            type: 'line', // line, bar, pie, scatter, candlestick
            width: '100%',
            height: '400px',
            responsive: true,
            theme: 'light',
            animation: true,
            realtime: false,
            updateInterval: 5000,
            maxDataPoints: 100,
            showLegend: true,
            showGrid: true,
            showTooltip: true,
            colors: ['#3b82f6', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6'],
            locale: 'zh-CN'
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // 图表实例和数据
        this.chart = null;
        this.data = [];
        this.series = [];
        this.updateTimer = null;
        this.isDestroyed = false;
        
        // 事件绑定
        this.boundHandlers = {
            resize: this.handleResize.bind(this),
            visibilityChange: this.handleVisibilityChange.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            await this.loadDependencies();
            this.createContainer();
            this.setupEventListeners();
            
            if (this.config.data) {
                await this.setData(this.config.data);
            }
            
            if (this.config.realtime) {
                this.startRealTimeUpdate();
            }
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化数据可视化组件失败');
            throw error;
        }
    }
    
    /**
     * 加载依赖库
     */
    async loadDependencies() {
        // 检查是否已加载 Plotly
        if (typeof Plotly === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdn.plot.ly/plotly-latest.min.js';
            script.charset = 'utf-8';
            
            return new Promise((resolve, reject) => {
                script.onload = () => {
                    // 设置本地化
                    Plotly.setPlotConfig({
                        locale: this.config.locale,
                        responsive: true
                    });
                    resolve();
                };
                script.onerror = () => reject(new Error('无法加载 Plotly.js'));
                document.head.appendChild(script);
            });
        }
    }
    
    /**
     * 创建容器
     */
    createContainer() {
        this.container.className = `data-visualization ${this.config.theme}`;
        this.container.innerHTML = `
            <div class="chart-header" ${this.config.title ? '' : 'style="display: none;"'}>
                <h3 class="chart-title">${this.config.title || ''}</h3>
                <div class="chart-controls">
                    <button class="chart-control-btn" data-action="refresh" title="刷新数据">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button class="chart-control-btn" data-action="fullscreen" title="全屏显示">
                        <i class="fas fa-expand"></i>
                    </button>
                    <button class="chart-control-btn" data-action="download" title="下载图表">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
            </div>
            <div class="chart-container" style="width: ${this.config.width}; height: ${this.config.height};">
                <div class="chart-loading" style="display: none;">
                    <div class="loading-spinner"></div>
                    <span class="loading-text">正在加载图表...</span>
                </div>
                <div class="chart-error" style="display: none;">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span class="error-text">图表加载失败</span>
                    <button class="retry-btn">重试</button>
                </div>
                <div class="chart-canvas" id="${this.getId()}-canvas"></div>
            </div>
            <div class="chart-footer" ${this.config.showLegend ? '' : 'style="display: none;"'}>
                <div class="chart-legend"></div>
                <div class="chart-stats">
                    <span class="data-points">数据点: 0</span>
                    <span class="last-updated">最后更新: --</span>
                </div>
            </div>
        `;
        
        // 获取关键元素引用
        this.elements = {
            header: this.container.querySelector('.chart-header'),
            title: this.container.querySelector('.chart-title'),
            controls: this.container.querySelector('.chart-controls'),
            chartContainer: this.container.querySelector('.chart-container'),
            loading: this.container.querySelector('.chart-loading'),
            error: this.container.querySelector('.chart-error'),
            canvas: this.container.querySelector('.chart-canvas'),
            footer: this.container.querySelector('.chart-footer'),
            legend: this.container.querySelector('.chart-legend'),
            stats: this.container.querySelector('.chart-stats')
        };
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 控制按钮事件
        this.elements.controls.addEventListener('click', (e) => {
            const action = e.target.closest('[data-action]')?.dataset.action;
            if (action) {
                this.handleControlAction(action);
            }
        });
        
        // 重试按钮
        this.elements.error.querySelector('.retry-btn')
            .addEventListener('click', () => this.refresh());
        
        // 窗口大小变化
        if (this.config.responsive) {
            window.addEventListener('resize', this.boundHandlers.resize);
        }
        
        // 页面可见性变化
        document.addEventListener('visibilitychange', this.boundHandlers.visibilityChange);
    }
    
    /**
     * 设置数据
     */
    async setData(data, options = {}) {
        try {
            this.showLoading();
            
            // 数据验证和处理
            const processedData = this.processData(data);
            this.data = processedData;
            
            // 创建或更新图表
            await this.renderChart();
            
            this.hideLoading();
            this.updateStats();
            
            this.emit('dataChanged', { data: processedData });
            
        } catch (error) {
            this.showError('数据加载失败');
            this.handleError(error, '设置图表数据失败');
        }
    }
    
    /**
     * 处理数据
     */
    processData(rawData) {
        if (!rawData) return [];
        
        // 根据图表类型处理数据
        switch (this.config.type) {
            case 'line':
            case 'scatter':
                return this.processLineData(rawData);
            case 'bar':
                return this.processBarData(rawData);
            case 'pie':
                return this.processPieData(rawData);
            case 'candlestick':
                return this.processCandlestickData(rawData);
            default:
                return rawData;
        }
    }
    
    /**
     * 处理线图数据
     */
    processLineData(data) {
        if (Array.isArray(data) && data.length > 0) {
            // 如果是单一数据系列
            if (typeof data[0] === 'number') {
                return [{
                    x: data.map((_, i) => i),
                    y: data,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: '数据系列1'
                }];
            }
            
            // 如果是多个数据系列
            if (Array.isArray(data[0])) {
                return data.map((series, i) => ({
                    x: series.x || series.map((_, j) => j),
                    y: series.y || series,
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: series.name || `数据系列${i + 1}`,
                    line: { color: this.config.colors[i % this.config.colors.length] }
                }));
            }
            
            // 如果是对象格式
            if (data[0].x !== undefined && data[0].y !== undefined) {
                return [{
                    x: data.map(d => d.x),
                    y: data.map(d => d.y),
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: '数据系列1'
                }];
            }
        }
        
        return [];
    }
    
    /**
     * 处理柱状图数据
     */
    processBarData(data) {
        if (Array.isArray(data)) {
            return [{
                x: data.map(d => d.label || d.x),
                y: data.map(d => d.value || d.y),
                type: 'bar',
                name: '数据',
                marker: { color: this.config.colors[0] }
            }];
        }
        return [];
    }
    
    /**
     * 处理饼图数据
     */
    processPieData(data) {
        if (Array.isArray(data)) {
            return [{
                labels: data.map(d => d.label),
                values: data.map(d => d.value),
                type: 'pie',
                marker: { colors: this.config.colors }
            }];
        }
        return [];
    }
    
    /**
     * 处理K线图数据
     */
    processCandlestickData(data) {
        if (Array.isArray(data)) {
            return [{
                x: data.map(d => d.date || d.x),
                open: data.map(d => d.open),
                high: data.map(d => d.high),
                low: data.map(d => d.low),
                close: data.map(d => d.close),
                type: 'candlestick',
                name: 'OHLC'
            }];
        }
        return [];
    }
    
    /**
     * 渲染图表
     */
    async renderChart() {
        if (!this.data || this.data.length === 0) return;
        
        const layout = this.createLayout();
        const config = this.createPlotConfig();
        
        try {
            if (this.chart) {
                // 更新现有图表
                await Plotly.react(this.elements.canvas, this.data, layout, config);
            } else {
                // 创建新图表
                await Plotly.newPlot(this.elements.canvas, this.data, layout, config);
                this.chart = this.elements.canvas;
                
                // 绑定图表事件
                this.bindChartEvents();
            }
        } catch (error) {
            throw new Error(`渲染图表失败: ${error.message}`);
        }
    }
    
    /**
     * 创建布局配置
     */
    createLayout() {
        return {
            title: {
                text: this.config.title,
                font: { size: 16, color: '#374151' }
            },
            showlegend: this.config.showLegend,
            responsive: this.config.responsive,
            autosize: true,
            margin: { l: 50, r: 50, t: 60, b: 50 },
            xaxis: {
                showgrid: this.config.showGrid,
                gridcolor: '#e5e7eb',
                title: this.config.xAxisTitle
            },
            yaxis: {
                showgrid: this.config.showGrid,
                gridcolor: '#e5e7eb',
                title: this.config.yAxisTitle
            },
            plot_bgcolor: this.config.theme === 'dark' ? '#1f2937' : '#ffffff',
            paper_bgcolor: this.config.theme === 'dark' ? '#111827' : '#ffffff',
            font: {
                color: this.config.theme === 'dark' ? '#f9fafb' : '#374151'
            }
        };
    }
    
    /**
     * 创建Plotly配置
     */
    createPlotConfig() {
        return {
            responsive: this.config.responsive,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: `chart_${Date.now()}`,
                height: 500,
                width: 700,
                scale: 1
            }
        };
    }
    
    /**
     * 绑定图表事件
     */
    bindChartEvents() {
        // 点击事件
        this.elements.canvas.on('plotly_click', (data) => {
            this.emit('chartClick', { data });
        });
        
        // 悬停事件
        this.elements.canvas.on('plotly_hover', (data) => {
            this.emit('chartHover', { data });
        });
        
        // 缩放事件
        this.elements.canvas.on('plotly_relayout', (eventData) => {
            this.emit('chartZoom', { eventData });
        });
    }
    
    /**
     * 添加数据点
     */
    addDataPoint(point, seriesIndex = 0) {
        if (!this.data[seriesIndex]) return;
        
        const series = this.data[seriesIndex];
        
        // 添加新数据点
        if (Array.isArray(series.x)) {
            series.x.push(point.x);
            series.y.push(point.y);
        }
        
        // 限制数据点数量
        if (series.x.length > this.config.maxDataPoints) {
            series.x.shift();
            series.y.shift();
        }
        
        // 更新图表
        this.updateChart();
        this.updateStats();
    }
    
    /**
     * 更新图表
     */
    async updateChart() {
        if (!this.chart) return;
        
        try {
            await Plotly.redraw(this.elements.canvas);
            this.emit('chartUpdated');
        } catch (error) {
            this.handleError(error, '更新图表失败');
        }
    }
    
    /**
     * 开始实时更新
     */
    startRealTimeUpdate() {
        if (this.updateTimer) return;
        
        this.updateTimer = setInterval(async () => {
            if (!document.hidden && !this.isDestroyed) {
                await this.fetchRealTimeData();
            }
        }, this.config.updateInterval);
        
        this.emit('realTimeStarted');
    }
    
    /**
     * 停止实时更新
     */
    stopRealTimeUpdate() {
        if (this.updateTimer) {
            clearInterval(this.updateTimer);
            this.updateTimer = null;
            this.emit('realTimeStopped');
        }
    }
    
    /**
     * 获取实时数据
     */
    async fetchRealTimeData() {
        if (!this.config.dataUrl) return;
        
        try {
            const response = await fetch(this.config.dataUrl);
            const newData = await response.json();
            
            if (newData && newData.length > 0) {
                // 添加新数据点或更新数据
                if (this.config.appendData) {
                    newData.forEach(point => this.addDataPoint(point));
                } else {
                    await this.setData(newData);
                }
            }
        } catch (error) {
            this.handleError(error, '获取实时数据失败');
        }
    }
    
    /**
     * 控制操作处理
     */
    handleControlAction(action) {
        switch (action) {
            case 'refresh':
                this.refresh();
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
     * 刷新图表
     */
    async refresh() {
        try {
            if (this.config.realtime) {
                await this.fetchRealTimeData();
            } else if (this.config.dataUrl) {
                const response = await fetch(this.config.dataUrl);
                const data = await response.json();
                await this.setData(data);
            } else {
                await this.updateChart();
            }
        } catch (error) {
            this.handleError(error, '刷新图表失败');
        }
    }
    
    /**
     * 切换全屏
     */
    toggleFullscreen() {
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            this.container.requestFullscreen().catch(err => {
                console.warn('无法进入全屏模式:', err);
            });
        }
    }
    
    /**
     * 下载图表
     */
    downloadChart() {
        if (!this.chart) return;
        
        Plotly.downloadImage(this.elements.canvas, {
            format: 'png',
            width: 1200,
            height: 800,
            filename: `chart_${Date.now()}`
        });
    }
    
    /**
     * 更新统计信息
     */
    updateStats() {
        const totalPoints = this.data.reduce((sum, series) => {
            return sum + (series.x ? series.x.length : 0);
        }, 0);
        
        this.elements.stats.querySelector('.data-points').textContent = `数据点: ${totalPoints}`;
        this.elements.stats.querySelector('.last-updated').textContent = 
            `最后更新: ${new Date().toLocaleTimeString('zh-CN')}`;
    }
    
    /**
     * 显示加载状态
     */
    showLoading() {
        this.elements.loading.style.display = 'flex';
        this.elements.error.style.display = 'none';
        this.elements.canvas.style.display = 'none';
    }
    
    /**
     * 隐藏加载状态
     */
    hideLoading() {
        this.elements.loading.style.display = 'none';
        this.elements.canvas.style.display = 'block';
    }
    
    /**
     * 显示错误
     */
    showError(message) {
        this.elements.error.style.display = 'flex';
        this.elements.error.querySelector('.error-text').textContent = message;
        this.elements.loading.style.display = 'none';
        this.elements.canvas.style.display = 'none';
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        if (this.chart && this.config.responsive) {
            Plotly.Plots.resize(this.elements.canvas);
        }
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // 页面隐藏时暂停更新
            if (this.config.realtime && this.updateTimer) {
                this.stopRealTimeUpdate();
            }
        } else {
            // 页面可见时恢复更新
            if (this.config.realtime && !this.updateTimer) {
                this.startRealTimeUpdate();
            }
        }
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 停止实时更新
        this.stopRealTimeUpdate();
        
        // 销毁图表
        if (this.chart) {
            Plotly.purge(this.elements.canvas);
            this.chart = null;
        }
        
        // 移除事件监听器
        window.removeEventListener('resize', this.boundHandlers.resize);
        document.removeEventListener('visibilitychange', this.boundHandlers.visibilityChange);
        
        this.isDestroyed = true;
        
        super.destroy();
    }
}

// 注册组件
if (typeof JSComponentManager !== 'undefined') {
    JSComponentManager.register('data-visualization', DataVisualization);
}

// 导出组件（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataVisualization;
}