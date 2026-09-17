/**
 * JavaScript组件基础架构
 * 提供组件注册、生命周期管理、事件系统等核心功能
 */

/**
 * 基础组件类 - 所有组件的基类
 */
class BaseComponent {
    constructor(name, options = {}) {
        this.name = name;
        this.options = { ...this.getDefaultOptions(), ...options };
        this.initialized = false;
        this.destroyed = false;
        this.eventListeners = new Map();
        this.children = new Map();
        
        // 生成唯一ID
        this.id = this.generateId();
        
        // 自动注册到管理器
        if (window.jsComponentManager) {
            window.jsComponentManager.register(this);
        }
    }

    /**
     * 获取默认配置
     */
    getDefaultOptions() {
        return {
            autoInit: true,
            debug: false,
            container: null,
            events: {}
        };
    }

    /**
     * 初始化组件
     */
    init() {
        if (this.initialized) return this;
        
        this.log('初始化组件');
        
        try {
            // 查找容器
            if (this.options.container) {
                this.container = this.getElement(this.options.container);
            }
            
            // 绑定事件
            this.bindEvents();
            
            // 调用子类初始化方法
            if (typeof this.onInit === 'function') {
                this.onInit();
            }
            
            this.initialized = true;
            this.emit('init', { component: this });
            
            this.log('组件初始化完成');
        } catch (error) {
            this.error('组件初始化失败', error);
        }
        
        return this;
    }

    /**
     * 销毁组件
     */
    destroy() {
        if (this.destroyed) return;
        
        this.log('销毁组件');
        
        try {
            // 移除事件监听器
            this.removeAllListeners();
            
            // 销毁子组件
            this.children.forEach(child => child.destroy());
            this.children.clear();
            
            // 调用子类销毁方法
            if (typeof this.onDestroy === 'function') {
                this.onDestroy();
            }
            
            this.destroyed = true;
            this.emit('destroy', { component: this });
            
            // 从管理器中注销
            if (window.jsComponentManager) {
                window.jsComponentManager.unregister(this.id);
            }
            
            this.log('组件销毁完成');
        } catch (error) {
            this.error('组件销毁失败', error);
        }
    }

    /**
     * 绑定事件
     */
    bindEvents() {
        const events = this.options.events || {};
        
        Object.entries(events).forEach(([event, handler]) => {
            if (typeof handler === 'function') {
                this.on(event, handler);
            } else if (typeof handler === 'string' && typeof this[handler] === 'function') {
                this.on(event, this[handler].bind(this));
            }
        });
    }

    /**
     * 事件监听
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, new Set());
        }
        this.eventListeners.get(event).add(callback);
        return this;
    }

    /**
     * 移除事件监听
     */
    off(event, callback = null) {
        if (!this.eventListeners.has(event)) return this;
        
        if (callback) {
            this.eventListeners.get(event).delete(callback);
        } else {
            this.eventListeners.delete(event);
        }
        
        return this;
    }

    /**
     * 触发事件
     */
    emit(event, data = {}) {
        // 触发组件自身事件
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback.call(this, { ...data, component: this, event });
                } catch (error) {
                    this.error(`事件处理器执行错误: ${event}`, error);
                }
            });
        }
        
        // 触发全局事件
        if (window.jsComponentManager) {
            window.jsComponentManager.emit(`${this.name}:${event}`, {
                ...data,
                component: this,
                componentName: this.name,
                componentId: this.id
            });
        }
        
        return this;
    }

    /**
     * 添加子组件
     */
    addChild(component) {
        if (component instanceof BaseComponent) {
            this.children.set(component.id, component);
            component.parent = this;
            this.emit('childAdded', { child: component });
        }
        return this;
    }

    /**
     * 移除子组件
     */
    removeChild(componentId) {
        const component = this.children.get(componentId);
        if (component) {
            component.destroy();
            this.children.delete(componentId);
            this.emit('childRemoved', { childId: componentId });
        }
        return this;
    }

    /**
     * 获取DOM元素
     */
    getElement(selector) {
        if (typeof selector === 'string') {
            return document.querySelector(selector);
        } else if (selector instanceof HTMLElement) {
            return selector;
        }
        return null;
    }

    /**
     * 获取多个DOM元素
     */
    getElements(selector) {
        if (typeof selector === 'string') {
            return document.querySelectorAll(selector);
        }
        return [];
    }

    /**
     * 移除所有事件监听器
     */
    removeAllListeners() {
        this.eventListeners.clear();
    }

    /**
     * 生成唯一ID
     */
    generateId() {
        return `${this.name}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * 日志记录
     */
    log(message, ...args) {
        if (this.options.debug) {
            console.log(`[${this.name}:${this.id}]`, message, ...args);
        }
    }

    /**
     * 错误记录
     */
    error(message, error = null) {
        console.error(`[${this.name}:${this.id}]`, message, error);
        this.emit('error', { message, error });
    }

    /**
     * 获取配置
     */
    getConfig(key, defaultValue = null) {
        return this.options[key] !== undefined ? this.options[key] : defaultValue;
    }

    /**
     * 设置配置
     */
    setConfig(key, value) {
        this.options[key] = value;
        this.emit('configChanged', { key, value });
        return this;
    }
}

/**
 * JavaScript组件管理器
 */
class JSComponentManager {
    constructor() {
        // 组件注册表
        this.components = new Map();
        this.componentTypes = new Map();
        
        // 事件系统
        this.eventListeners = new Map();
        
        // 配置
        this.config = {
            autoInit: true,
            debug: false,
            lazyLoad: false,
            basePath: '/static/js/components/'
        };
        
        // 依赖加载器
        this.dependencies = new Map();
        this.loadedDependencies = new Set();
        
        // 初始化状态
        this.initialized = false;
        
        this.init();
    }

    /**
     * 初始化管理器
     */
    init() {
        if (this.initialized) return;
        
        this.log('初始化组件管理器');
        
        // 注册基础组件类型
        this.registerComponentType('base', BaseComponent);
        
        // 绑定全局事件
        this.bindGlobalEvents();
        
        // 自动发现已存在的组件
        this.discoverComponents();
        
        this.initialized = true;
        this.emit('managerInit');
        
        this.log('组件管理器初始化完成');
    }

    /**
     * 注册组件类型
     */
    registerComponentType(name, componentClass) {
        if (typeof componentClass === 'function') {
            this.componentTypes.set(name, componentClass);
            this.log(`注册组件类型: ${name}`);
        }
        return this;
    }

    /**
     * 注册组件实例
     */
    register(component) {
        if (component instanceof BaseComponent) {
            this.components.set(component.id, component);
            this.emit('componentRegistered', { component });
            this.log(`注册组件: ${component.name}#${component.id}`);
        }
        return this;
    }

    /**
     * 注销组件
     */
    unregister(componentId) {
        if (this.components.has(componentId)) {
            const component = this.components.get(componentId);
            this.components.delete(componentId);
            this.emit('componentUnregistered', { componentId, component });
            this.log(`注销组件: ${componentId}`);
        }
        return this;
    }

    /**
     * 获取组件
     */
    get(componentId) {
        return this.components.get(componentId);
    }

    /**
     * 根据名称获取组件
     */
    getByName(name) {
        return Array.from(this.components.values()).filter(c => c.name === name);
    }

    /**
     * 获取所有组件
     */
    getAll() {
        return Array.from(this.components.values());
    }

    /**
     * 创建组件
     */
    create(type, options = {}) {
        const ComponentClass = this.componentTypes.get(type);
        if (!ComponentClass) {
            throw new Error(`未知的组件类型: ${type}`);
        }
        
        const component = new ComponentClass(type, options);
        
        if (this.config.autoInit) {
            component.init();
        }
        
        return component;
    }

    /**
     * 销毁组件
     */
    destroy(componentId) {
        const component = this.get(componentId);
        if (component) {
            component.destroy();
        }
        return this;
    }

    /**
     * 销毁所有组件
     */
    destroyAll() {
        this.components.forEach(component => component.destroy());
        this.components.clear();
        return this;
    }

    /**
     * 事件监听
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, new Set());
        }
        this.eventListeners.get(event).add(callback);
        return this;
    }

    /**
     * 移除事件监听
     */
    off(event, callback = null) {
        if (!this.eventListeners.has(event)) return this;
        
        if (callback) {
            this.eventListeners.get(event).delete(callback);
        } else {
            this.eventListeners.delete(event);
        }
        
        return this;
    }

    /**
     * 触发事件
     */
    emit(event, data = {}) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback.call(this, { ...data, event, manager: this });
                } catch (error) {
                    this.error(`全局事件处理器执行错误: ${event}`, error);
                }
            });
        }
        return this;
    }

    /**
     * 加载依赖
     */
    async loadDependency(name, url = null) {
        if (this.loadedDependencies.has(name)) {
            return Promise.resolve();
        }
        
        const dependencyUrl = url || this.dependencies.get(name);
        if (!dependencyUrl) {
            throw new Error(`未找到依赖: ${name}`);
        }
        
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = dependencyUrl;
            script.onload = () => {
                this.loadedDependencies.add(name);
                this.log(`依赖加载完成: ${name}`);
                resolve();
            };
            script.onerror = () => {
                this.error(`依赖加载失败: ${name}`);
                reject(new Error(`Failed to load dependency: ${name}`));
            };
            
            document.head.appendChild(script);
        });
    }

    /**
     * 注册依赖
     */
    registerDependency(name, url) {
        this.dependencies.set(name, url);
        return this;
    }

    /**
     * 绑定全局事件
     */
    bindGlobalEvents() {
        // DOM加载完成事件
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.emit('domReady');
                if (this.config.autoInit) {
                    this.initAllComponents();
                }
            });
        } else {
            setTimeout(() => {
                this.emit('domReady');
                if (this.config.autoInit) {
                    this.initAllComponents();
                }
            }, 0);
        }

        // 窗口加载完成事件
        window.addEventListener('load', () => {
            this.emit('windowLoad');
        });

        // 页面卸载事件
        window.addEventListener('beforeunload', () => {
            this.emit('beforeUnload');
            this.destroyAll();
        });

        // 错误处理
        window.addEventListener('error', (event) => {
            this.emit('globalError', { 
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno,
                error: event.error
            });
        });
    }

    /**
     * 自动发现组件
     */
    discoverComponents() {
        // 查找带有组件标识的元素
        const elements = document.querySelectorAll('[data-component]');
        elements.forEach(element => {
            const componentType = element.getAttribute('data-component');
            const componentOptions = this.parseDataAttributes(element);
            
            try {
                this.create(componentType, {
                    ...componentOptions,
                    container: element
                });
            } catch (error) {
                this.error(`自动创建组件失败: ${componentType}`, error);
            }
        });
    }

    /**
     * 解析data属性
     */
    parseDataAttributes(element) {
        const options = {};
        
        Array.from(element.attributes).forEach(attr => {
            if (attr.name.startsWith('data-') && attr.name !== 'data-component') {
                const key = attr.name
                    .replace('data-', '')
                    .replace(/-([a-z])/g, (match, letter) => letter.toUpperCase());
                
                let value = attr.value;
                
                // 尝试解析JSON
                try {
                    value = JSON.parse(value);
                } catch {
                    // 尝试解析布尔值和数字
                    if (value === 'true') value = true;
                    else if (value === 'false') value = false;
                    else if (!isNaN(value) && !isNaN(parseFloat(value))) {
                        value = parseFloat(value);
                    }
                }
                
                options[key] = value;
            }
        });
        
        return options;
    }

    /**
     * 初始化所有组件
     */
    initAllComponents() {
        this.components.forEach(component => {
            if (!component.initialized) {
                try {
                    component.init();
                } catch (error) {
                    this.error(`组件初始化失败: ${component.name}#${component.id}`, error);
                }
            }
        });
    }

    /**
     * 获取统计信息
     */
    getStats() {
        const stats = {
            totalComponents: this.components.size,
            componentTypes: this.componentTypes.size,
            loadedDependencies: this.loadedDependencies.size,
            componentsByType: {}
        };
        
        this.components.forEach(component => {
            const type = component.name;
            stats.componentsByType[type] = (stats.componentsByType[type] || 0) + 1;
        });
        
        return stats;
    }

    /**
     * 日志记录
     */
    log(message, ...args) {
        if (this.config.debug) {
            console.log('[JSComponentManager]', message, ...args);
        }
    }

    /**
     * 错误记录
     */
    error(message, error = null) {
        console.error('[JSComponentManager]', message, error);
        this.emit('error', { message, error });
    }

    /**
     * 设置配置
     */
    setConfig(config) {
        Object.assign(this.config, config);
        this.emit('configChanged', { config: this.config });
        return this;
    }
}

// 全局初始化
if (typeof window !== 'undefined') {
    // 确保只有一个管理器实例
    if (!window.jsComponentManager) {
        window.jsComponentManager = new JSComponentManager();
        
        // 导出到全局
        window.BaseComponent = BaseComponent;
        window.JSComponentManager = JSComponentManager;
    }
}

// 模块导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { BaseComponent, JSComponentManager };
}

// AMD导出
if (typeof define === 'function' && define.amd) {
    define(() => ({ BaseComponent, JSComponentManager }));
}