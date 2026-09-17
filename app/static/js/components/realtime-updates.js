/**
 * 实时更新组件
 * 管理WebSocket连接和实时数据流
 */

class RealTimeUpdates extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'RealTimeUpdates';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            wsUrl: null, // WebSocket URL
            reconnectInterval: 5000,
            maxReconnectAttempts: 5,
            heartbeatInterval: 30000,
            autoConnect: true,
            topics: [], // 订阅的主题
            queueSize: 100, // 消息队列大小
            showStatus: true,
            showMetrics: false,
            enableLogging: false
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // WebSocket 相关
        this.ws = null;
        this.wsUrl = this.config.wsUrl || this.generateWebSocketUrl();
        this.reconnectAttempts = 0;
        this.reconnectTimer = null;
        this.heartbeatTimer = null;
        this.isConnecting = false;
        this.isDestroyed = false;
        
        // 消息和订阅管理
        this.messageQueue = [];
        this.subscriptions = new Map();
        this.messageHandlers = new Map();
        
        // 状态和指标
        this.connectionState = 'disconnected';
        this.metrics = {
            messagesReceived: 0,
            messagesSent: 0,
            bytesReceived: 0,
            bytesSent: 0,
            reconnectCount: 0,
            lastMessageTime: null,
            connectionTime: null
        };
        
        // 事件绑定
        this.boundHandlers = {
            visibilityChange: this.handleVisibilityChange.bind(this),
            beforeUnload: this.handleBeforeUnload.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            this.createContainer();
            this.setupEventListeners();
            
            if (this.config.autoConnect) {
                await this.connect();
            }
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化实时更新组件失败');
            throw error;
        }
    }
    
    /**
     * 生成WebSocket URL
     */
    generateWebSocketUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/ws/realtime`;
    }
    
    /**
     * 创建容器
     */
    createContainer() {
        this.container.className = 'realtime-updates';
        this.container.innerHTML = `
            <div class="status-panel" ${this.config.showStatus ? '' : 'style="display: none;"'}>
                <div class="connection-status">
                    <div class="status-indicator disconnected"></div>
                    <span class="status-text">已断开</span>
                </div>
                <div class="connection-actions">
                    <button class="action-btn connect-btn" data-action="connect">连接</button>
                    <button class="action-btn disconnect-btn" data-action="disconnect" disabled>断开</button>
                    <button class="action-btn reconnect-btn" data-action="reconnect" disabled>重连</button>
                </div>
            </div>
            
            <div class="metrics-panel" ${this.config.showMetrics ? '' : 'style="display: none;"'}>
                <div class="metric-item">
                    <span class="metric-label">接收消息:</span>
                    <span class="metric-value" id="messages-received">0</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">发送消息:</span>
                    <span class="metric-value" id="messages-sent">0</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">连接时间:</span>
                    <span class="metric-value" id="connection-time">--</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">重连次数:</span>
                    <span class="metric-value" id="reconnect-count">0</span>
                </div>
            </div>
            
            <div class="message-log" style="display: none;">
                <div class="log-header">
                    <h4>消息日志</h4>
                    <button class="log-clear">清空</button>
                </div>
                <div class="log-content"></div>
            </div>
        `;
        
        // 获取关键元素引用
        this.elements = {
            statusPanel: this.container.querySelector('.status-panel'),
            statusIndicator: this.container.querySelector('.status-indicator'),
            statusText: this.container.querySelector('.status-text'),
            connectBtn: this.container.querySelector('.connect-btn'),
            disconnectBtn: this.container.querySelector('.disconnect-btn'),
            reconnectBtn: this.container.querySelector('.reconnect-btn'),
            metricsPanel: this.container.querySelector('.metrics-panel'),
            messageLog: this.container.querySelector('.message-log'),
            logContent: this.container.querySelector('.log-content'),
            logClear: this.container.querySelector('.log-clear')
        };
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 按钮事件
        this.elements.statusPanel.addEventListener('click', (e) => {
            const action = e.target.dataset.action;
            if (action) {
                this.handleActionClick(action);
            }
        });
        
        // 清空日志
        this.elements.logClear.addEventListener('click', () => {
            this.clearMessageLog();
        });
        
        // 页面可见性变化
        document.addEventListener('visibilitychange', this.boundHandlers.visibilityChange);
        
        // 页面卸载前断开连接
        window.addEventListener('beforeunload', this.boundHandlers.beforeUnload);
    }
    
    /**
     * 连接WebSocket
     */
    async connect() {
        if (this.ws?.readyState === WebSocket.OPEN || this.isConnecting) {
            return;
        }
        
        this.isConnecting = true;
        this.updateConnectionState('connecting');
        
        try {
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = (event) => {
                this.handleOpen(event);
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(event);
            };
            
            this.ws.onclose = (event) => {
                this.handleClose(event);
            };
            
            this.ws.onerror = (event) => {
                this.handleError(event, 'WebSocket连接错误');
            };
            
        } catch (error) {
            this.isConnecting = false;
            this.updateConnectionState('error');
            this.handleError(error, 'WebSocket连接失败');
            throw error;
        }
    }
    
    /**
     * 断开连接
     */
    disconnect() {
        this.clearReconnectTimer();
        this.clearHeartbeatTimer();
        
        if (this.ws) {
            this.ws.close(1000, '用户主动断开');
        }
        
        this.updateConnectionState('disconnected');
    }
    
    /**
     * 处理连接打开
     */
    handleOpen(event) {
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        this.metrics.connectionTime = new Date();
        
        this.updateConnectionState('connected');
        this.startHeartbeat();
        
        // 重新订阅所有主题
        this.resubscribeAll();
        
        this.log('WebSocket连接已建立');
        this.emit('connected', { event });
    }
    
    /**
     * 处理接收到的消息
     */
    handleMessage(event) {
        try {
            const data = JSON.parse(event.data);
            
            // 更新指标
            this.metrics.messagesReceived++;
            this.metrics.bytesReceived += event.data.length;
            this.metrics.lastMessageTime = new Date();
            
            this.updateMetrics();
            this.logMessage('received', data);
            
            // 处理不同类型的消息
            this.processMessage(data);
            
        } catch (error) {
            this.handleError(error, '处理WebSocket消息失败');
        }
    }
    
    /**
     * 处理连接关闭
     */
    handleClose(event) {
        this.isConnecting = false;
        this.clearHeartbeatTimer();
        
        if (event.wasClean) {
            this.updateConnectionState('disconnected');
            this.log(`连接已断开: ${event.reason}`);
        } else {
            this.updateConnectionState('error');
            this.log(`连接意外断开: ${event.code}`);
            
            // 自动重连
            if (!this.isDestroyed && this.reconnectAttempts < this.config.maxReconnectAttempts) {
                this.scheduleReconnect();
            }
        }
        
        this.emit('disconnected', { event });
    }
    
    /**
     * 处理消息
     */
    processMessage(data) {
        const { type, topic, payload } = data;
        
        switch (type) {
            case 'heartbeat':
                this.handleHeartbeat(payload);
                break;
            case 'subscription_ack':
                this.handleSubscriptionAck(topic, payload);
                break;
            case 'data':
                this.handleDataMessage(topic, payload);
                break;
            case 'error':
                this.handleServerError(payload);
                break;
            default:
                this.log(`未知消息类型: ${type}`);
        }
    }
    
    /**
     * 处理心跳消息
     */
    handleHeartbeat(payload) {
        // 发送心跳响应
        this.send({
            type: 'heartbeat_pong',
            timestamp: Date.now()
        });
    }
    
    /**
     * 处理订阅确认
     */
    handleSubscriptionAck(topic, payload) {
        this.log(`订阅确认: ${topic}`);
        this.emit('subscriptionAck', { topic, payload });
    }
    
    /**
     * 处理数据消息
     */
    handleDataMessage(topic, payload) {
        // 调用注册的处理函数
        const handler = this.messageHandlers.get(topic);
        if (handler) {
            handler(payload, topic);
        }
        
        // 触发通用事件
        this.emit('dataMessage', { topic, payload });
        
        // 添加到消息队列
        this.addToQueue({ topic, payload, timestamp: Date.now() });
    }
    
    /**
     * 处理服务器错误
     */
    handleServerError(payload) {
        this.log(`服务器错误: ${payload.message}`, 'error');
        this.emit('serverError', { error: payload });
    }
    
    /**
     * 发送消息
     */
    send(data) {
        if (this.ws?.readyState === WebSocket.OPEN) {
            const message = JSON.stringify(data);
            this.ws.send(message);
            
            // 更新指标
            this.metrics.messagesSent++;
            this.metrics.bytesSent += message.length;
            
            this.updateMetrics();
            this.logMessage('sent', data);
            
            return true;
        }
        
        this.log('无法发送消息: 连接未建立', 'warn');
        return false;
    }
    
    /**
     * 订阅主题
     */
    subscribe(topic, handler) {
        // 注册处理函数
        if (handler) {
            this.messageHandlers.set(topic, handler);
        }
        
        // 记录订阅
        this.subscriptions.set(topic, {
            handler,
            subscribedAt: new Date()
        });
        
        // 发送订阅请求
        const success = this.send({
            type: 'subscribe',
            topic: topic
        });
        
        if (success) {
            this.log(`订阅主题: ${topic}`);
            this.emit('subscribe', { topic });
        }
        
        return success;
    }
    
    /**
     * 取消订阅
     */
    unsubscribe(topic) {
        // 移除处理函数和记录
        this.messageHandlers.delete(topic);
        this.subscriptions.delete(topic);
        
        // 发送取消订阅请求
        const success = this.send({
            type: 'unsubscribe',
            topic: topic
        });
        
        if (success) {
            this.log(`取消订阅: ${topic}`);
            this.emit('unsubscribe', { topic });
        }
        
        return success;
    }
    
    /**
     * 重新订阅所有主题
     */
    resubscribeAll() {
        for (const [topic] of this.subscriptions) {
            this.send({
                type: 'subscribe',
                topic: topic
            });
        }
    }
    
    /**
     * 开始心跳
     */
    startHeartbeat() {
        this.clearHeartbeatTimer();
        
        this.heartbeatTimer = setInterval(() => {
            this.send({
                type: 'heartbeat_ping',
                timestamp: Date.now()
            });
        }, this.config.heartbeatInterval);
    }
    
    /**
     * 清除心跳定时器
     */
    clearHeartbeatTimer() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }
    
    /**
     * 安排重连
     */
    scheduleReconnect() {
        if (this.reconnectTimer || this.isDestroyed) return;
        
        this.reconnectAttempts++;
        this.metrics.reconnectCount++;
        
        const delay = Math.min(
            this.config.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
            30000
        );
        
        this.log(`将在 ${delay}ms 后尝试第 ${this.reconnectAttempts} 次重连`);
        
        this.reconnectTimer = setTimeout(async () => {
            this.reconnectTimer = null;
            
            try {
                await this.connect();
            } catch (error) {
                this.log(`重连失败: ${error.message}`, 'error');
            }
        }, delay);
        
        this.updateMetrics();
    }
    
    /**
     * 清除重连定时器
     */
    clearReconnectTimer() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
    }
    
    /**
     * 添加消息到队列
     */
    addToQueue(message) {
        this.messageQueue.push(message);
        
        // 限制队列大小
        if (this.messageQueue.length > this.config.queueSize) {
            this.messageQueue.shift();
        }
    }
    
    /**
     * 获取消息队列
     */
    getMessageQueue() {
        return [...this.messageQueue];
    }
    
    /**
     * 清空消息队列
     */
    clearMessageQueue() {
        this.messageQueue = [];
    }
    
    /**
     * 更新连接状态
     */
    updateConnectionState(state) {
        this.connectionState = state;
        
        // 更新UI
        this.elements.statusIndicator.className = `status-indicator ${state}`;
        
        const stateTexts = {
            'disconnected': '已断开',
            'connecting': '连接中...',
            'connected': '已连接',
            'error': '连接错误'
        };
        
        this.elements.statusText.textContent = stateTexts[state] || state;
        
        // 更新按钮状态
        this.elements.connectBtn.disabled = ['connecting', 'connected'].includes(state);
        this.elements.disconnectBtn.disabled = !['connected'].includes(state);
        this.elements.reconnectBtn.disabled = ['connecting', 'connected'].includes(state);
        
        this.emit('stateChanged', { state });
    }
    
    /**
     * 更新指标显示
     */
    updateMetrics() {
        if (!this.config.showMetrics) return;
        
        this.container.querySelector('#messages-received').textContent = 
            this.metrics.messagesReceived.toLocaleString();
        
        this.container.querySelector('#messages-sent').textContent = 
            this.metrics.messagesSent.toLocaleString();
        
        this.container.querySelector('#connection-time').textContent = 
            this.metrics.connectionTime ? 
            this.formatDuration(Date.now() - this.metrics.connectionTime.getTime()) : '--';
        
        this.container.querySelector('#reconnect-count').textContent = 
            this.metrics.reconnectCount.toString();
    }
    
    /**
     * 格式化持续时间
     */
    formatDuration(ms) {
        const seconds = Math.floor(ms / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes % 60}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    }
    
    /**
     * 记录消息
     */
    logMessage(direction, data) {
        if (!this.config.enableLogging) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${direction}`;
        logEntry.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <span class="log-direction">[${direction.toUpperCase()}]</span>
            <span class="log-data">${JSON.stringify(data, null, 2)}</span>
        `;
        
        this.elements.logContent.appendChild(logEntry);
        this.elements.logContent.scrollTop = this.elements.logContent.scrollHeight;
        
        // 限制日志条目数量
        const entries = this.elements.logContent.querySelectorAll('.log-entry');
        if (entries.length > 100) {
            entries[0].remove();
        }
    }
    
    /**
     * 清空消息日志
     */
    clearMessageLog() {
        this.elements.logContent.innerHTML = '';
    }
    
    /**
     * 记录日志
     */
    log(message, level = 'info') {
        if (this.config.enableLogging) {
            console.log(`[RealTimeUpdates] ${message}`);
        }
        
        this.emit('log', { message, level });
    }
    
    /**
     * 处理按钮点击
     */
    async handleActionClick(action) {
        switch (action) {
            case 'connect':
                await this.connect();
                break;
            case 'disconnect':
                this.disconnect();
                break;
            case 'reconnect':
                this.disconnect();
                await new Promise(resolve => setTimeout(resolve, 1000));
                await this.connect();
                break;
        }
    }
    
    /**
     * 处理页面可见性变化
     */
    handleVisibilityChange() {
        if (document.hidden) {
            // 页面隐藏时可以选择断开连接以节省资源
            if (this.config.pauseOnHidden) {
                this.disconnect();
            }
        } else {
            // 页面显示时重新连接
            if (this.config.pauseOnHidden && this.connectionState === 'disconnected') {
                this.connect();
            }
        }
    }
    
    /**
     * 处理页面卸载前事件
     */
    handleBeforeUnload() {
        this.disconnect();
    }
    
    /**
     * 获取连接状态
     */
    getConnectionState() {
        return this.connectionState;
    }
    
    /**
     * 获取指标数据
     */
    getMetrics() {
        return { ...this.metrics };
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        this.isDestroyed = true;
        
        // 断开连接
        this.disconnect();
        
        // 清除定时器
        this.clearReconnectTimer();
        this.clearHeartbeatTimer();
        
        // 移除事件监听器
        document.removeEventListener('visibilitychange', this.boundHandlers.visibilityChange);
        window.removeEventListener('beforeunload', this.boundHandlers.beforeUnload);
        
        // 清空数据
        this.messageQueue = [];
        this.subscriptions.clear();
        this.messageHandlers.clear();
        
        super.destroy();
    }
}

// 注册组件
if (typeof JSComponentManager !== 'undefined') {
    JSComponentManager.register('realtime-updates', RealTimeUpdates);
}

// 导出组件（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealTimeUpdates;
}