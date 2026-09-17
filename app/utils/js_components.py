"""
JavaScript组件基础架构
提供组件注册、生命周期管理、事件系统等核心功能
"""
from typing import Dict, List, Optional, Any
from flask import current_app, request, jsonify
import json
import os


class JSComponentManager:
    """JavaScript组件管理器"""
    
    def __init__(self):
        # 组件注册表
        self.components = {}
        
        # 组件配置
        self.component_config = {
            'base_path': '/static/js/components/',
            'auto_init': True,
            'lazy_loading': True,
            'cache_enabled': True
        }
        
        # 预定义组件列表
        self.core_components = {
            'smart_form': {
                'name': '智能表单组件',
                'description': '自动验证、动态字段、多步骤表单',
                'dependencies': ['validation', 'animation'],
                'file': 'smart-form.js',
                'css': 'smart-form.css',
                'config': {
                    'auto_validate': True,
                    'show_errors': True,
                    'save_draft': True
                }
            },
            'data_visualization': {
                'name': '数据可视化组件',
                'description': '图表展示、数据分析、交互式图形',
                'dependencies': ['charts', 'animation'],
                'file': 'data-visualization.js',
                'css': 'data-visualization.css',
                'config': {
                    'chart_types': ['line', 'bar', 'pie', 'scatter'],
                    'interactive': True,
                    'responsive': True
                }
            },
            'realtime_updates': {
                'name': '实时更新组件',
                'description': 'WebSocket连接、实时数据、推送通知',
                'dependencies': ['websocket', 'notification'],
                'file': 'realtime-updates.js',
                'css': 'realtime-updates.css',
                'config': {
                    'auto_reconnect': True,
                    'heartbeat_interval': 30000,
                    'max_retries': 5
                }
            },
            'interactive_charts': {
                'name': '交互式图表组件',
                'description': '股票图表、技术指标、缩放拖拽',
                'dependencies': ['charts', 'gesture', 'animation'],
                'file': 'interactive-charts.js',
                'css': 'interactive-charts.css',
                'config': {
                    'indicators': ['MA', 'MACD', 'RSI', 'BOLL'],
                    'zoom_enabled': True,
                    'crosshair': True
                }
            },
            'modal_dialog': {
                'name': '模态对话框组件',
                'description': '弹窗管理、层级控制、无障碍访问',
                'dependencies': ['animation', 'accessibility'],
                'file': 'modal-dialog.js',
                'css': 'modal-dialog.css',
                'config': {
                    'backdrop_close': True,
                    'escape_close': True,
                    'focus_trap': True
                }
            },
            'navigation': {
                'name': '导航组件',
                'description': '菜单导航、面包屑、侧边栏',
                'dependencies': ['animation', 'responsive'],
                'file': 'navigation.js',
                'css': 'navigation.css',
                'config': {
                    'auto_collapse': True,
                    'breadcrumbs': True,
                    'search_enabled': True
                }
            },
            'tooltip': {
                'name': '工具提示组件',
                'description': '悬停提示、帮助信息、定位控制',
                'dependencies': ['positioning', 'animation'],
                'file': 'tooltip.js',
                'css': 'tooltip.css',
                'config': {
                    'trigger': 'hover',
                    'placement': 'auto',
                    'delay': 500
                }
            }
        }
    
    def generate_component_framework(self) -> str:
        """生成组件框架JavaScript代码"""
        framework_js = '''
        /**
         * Kronos Stock 组件系统框架
         * 提供组件注册、生命周期管理、事件系统
         */
        
        // 全局组件系统
        window.KronosComponents = (function() {
            'use strict';
            
            // 组件注册表
            const components = new Map();
            const instances = new Map();
            const config = {
                autoInit: true,
                lazyLoading: true,
                debug: false
            };
            
            // 事件系统
            const eventBus = new EventTarget();
            
            // 基础组件类
            class BaseComponent {
                constructor(element, options = {}) {
                    this.element = element;
                    this.options = { ...this.defaultOptions, ...options };
                    this.id = this.generateId();
                    this.state = 'initialized';
                    this.listeners = new Map();
                    
                    // 绑定生命周期
                    this.init();
                }
                
                // 默认选项（子类可覆盖）
                get defaultOptions() {
                    return {
                        debug: false,
                        autoStart: true
                    };
                }
                
                // 生成唯一ID
                generateId() {
                    return `component-${Math.random().toString(36).substr(2, 9)}`;
                }
                
                // 初始化方法（子类实现）
                init() {
                    this.log('Component initialized');
                    this.state = 'ready';
                    this.emit('init');
                    
                    if (this.options.autoStart) {
                        this.start();
                    }
                }
                
                // 启动组件（子类实现）
                start() {
                    this.log('Component started');
                    this.state = 'active';
                    this.emit('start');
                }
                
                // 停止组件（子类实现）
                stop() {
                    this.log('Component stopped');
                    this.state = 'inactive';
                    this.emit('stop');
                }
                
                // 销毁组件
                destroy() {
                    this.log('Component destroying');
                    this.stop();
                    this.removeAllListeners();
                    this.state = 'destroyed';
                    this.emit('destroy');
                    
                    // 从实例映射中移除
                    instances.delete(this.element);
                }
                
                // 事件监听
                on(event, handler) {
                    if (!this.listeners.has(event)) {
                        this.listeners.set(event, new Set());
                    }
                    this.listeners.get(event).add(handler);
                    return this;
                }
                
                // 移除事件监听
                off(event, handler) {
                    if (this.listeners.has(event)) {
                        if (handler) {
                            this.listeners.get(event).delete(handler);
                        } else {
                            this.listeners.delete(event);
                        }
                    }
                    return this;
                }
                
                // 触发事件
                emit(event, data = null) {
                    // 触发组件内部事件
                    if (this.listeners.has(event)) {
                        this.listeners.get(event).forEach(handler => {
                            try {
                                handler.call(this, { type: event, data, target: this });
                            } catch (error) {
                                this.error('Event handler error:', error);
                            }
                        });
                    }
                    
                    // 触发全局事件
                    eventBus.dispatchEvent(new CustomEvent('component:' + event, {
                        detail: { component: this, data }
                    }));
                }
                
                // 获取/设置状态
                getState() {
                    return this.state;
                }
                
                setState(newState) {
                    const oldState = this.state;
                    this.state = newState;
                    this.emit('statechange', { oldState, newState });
                }
                
                // 日志方法
                log(...args) {
                    if (this.options.debug || config.debug) {
                        console.log(`[${this.constructor.name}:${this.id}]`, ...args);
                    }
                }
                
                error(...args) {
                    console.error(`[${this.constructor.name}:${this.id}]`, ...args);
                }
                
                // 移除所有事件监听器
                removeAllListeners() {
                    this.listeners.clear();
                }
                
                // 查找子元素
                $(selector) {
                    return this.element.querySelector(selector);
                }
                
                $$(selector) {
                    return this.element.querySelectorAll(selector);
                }
                
                // DOM事件绑定
                bindEvent(selector, event, handler) {
                    const elements = typeof selector === 'string' ? 
                        this.$$(selector) : [selector];
                    
                    elements.forEach(element => {
                        element.addEventListener(event, handler.bind(this));
                    });
                }
                
                // 获取选项值
                getOption(key, defaultValue = null) {
                    return this.options[key] !== undefined ? 
                        this.options[key] : defaultValue;
                }
                
                // 设置选项值
                setOption(key, value) {
                    this.options[key] = value;
                    this.emit('optionchange', { key, value });
                }
            }
            
            // 组件系统主要方法
            return {
                // 注册组件
                register(name, componentClass, options = {}) {
                    if (components.has(name)) {
                        console.warn(`Component "${name}" already registered, overriding`);
                    }
                    
                    components.set(name, {
                        class: componentClass,
                        options: options
                    });
                    
                    console.log(`Component "${name}" registered`);
                },
                
                // 创建组件实例
                create(name, element, options = {}) {
                    if (!components.has(name)) {
                        throw new Error(`Component "${name}" not registered`);
                    }
                    
                    const componentDef = components.get(name);
                    const instance = new componentDef.class(
                        element, 
                        { ...componentDef.options, ...options }
                    );
                    
                    instances.set(element, instance);
                    return instance;
                },
                
                // 获取组件实例
                getInstance(element) {
                    return instances.get(element);
                },
                
                // 销毁组件实例
                destroy(element) {
                    const instance = instances.get(element);
                    if (instance) {
                        instance.destroy();
                        return true;
                    }
                    return false;
                },
                
                // 自动初始化页面组件
                autoInit(container = document) {
                    const elements = container.querySelectorAll('[data-component]');
                    
                    elements.forEach(element => {
                        // 避免重复初始化
                        if (instances.has(element)) return;
                        
                        const componentName = element.dataset.component;
                        const options = this.parseOptions(element);
                        
                        try {
                            this.create(componentName, element, options);
                        } catch (error) {
                            console.error(`Failed to create component "${componentName}":`, error);
                        }
                    });
                },
                
                // 解析元素的配置选项
                parseOptions(element) {
                    const options = {};
                    
                    // 解析 data-* 属性
                    Object.keys(element.dataset).forEach(key => {
                        if (key.startsWith('component') && key !== 'component') {
                            const optionKey = key.replace('component', '').toLowerCase();
                            let value = element.dataset[key];
                            
                            // 尝试解析JSON
                            try {
                                value = JSON.parse(value);
                            } catch (e) {
                                // 保持原字符串
                            }
                            
                            options[optionKey] = value;
                        }
                    });
                    
                    return options;
                },
                
                // 全局事件监听
                on(event, handler) {
                    eventBus.addEventListener('component:' + event, handler);
                },
                
                // 移除全局事件监听
                off(event, handler) {
                    eventBus.removeEventListener('component:' + event, handler);
                },
                
                // 配置系统
                configure(newConfig) {
                    Object.assign(config, newConfig);
                },
                
                // 获取配置
                getConfig() {
                    return { ...config };
                },
                
                // 获取基础组件类
                BaseComponent,
                
                // 获取所有已注册组件
                getRegistered() {
                    return Array.from(components.keys());
                },
                
                // 获取所有组件实例
                getInstances() {
                    return Array.from(instances.values());
                }
            };
        })();
        
        // DOM加载完成后自动初始化
        document.addEventListener('DOMContentLoaded', function() {
            if (KronosComponents.getConfig().autoInit) {
                KronosComponents.autoInit();
            }
        });
        
        // HTMX集成 - 内容更新后重新初始化组件
        if (typeof htmx !== 'undefined') {
            document.addEventListener('htmx:afterSwap', function(event) {
                KronosComponents.autoInit(event.detail.target);
            });
        }
        
        // 导出基础组件类供其他组件继承
        window.BaseComponent = KronosComponents.BaseComponent;
        '''
        
        return framework_js
    
    def generate_component_loader(self) -> str:
        """生成组件加载器"""
        loader_js = '''
        /**
         * 组件动态加载器
         * 支持按需加载、依赖管理、缓存控制
         */
        
        window.ComponentLoader = (function() {
            'use strict';
            
            const loadedComponents = new Set();
            const loadingPromises = new Map();
            const componentDependencies = new Map();
            
            // 组件配置
            const config = {
                basePath: '/static/js/components/',
                cacheBusting: false,
                timeout: 10000
            };
            
            // 加载单个JavaScript文件
            function loadScript(src) {
                return new Promise((resolve, reject) => {
                    // 检查是否已加载
                    if (document.querySelector(`script[src="${src}"]`)) {
                        resolve();
                        return;
                    }
                    
                    const script = document.createElement('script');
                    script.src = src + (config.cacheBusting ? '?v=' + Date.now() : '');
                    script.async = true;
                    
                    script.onload = () => resolve();
                    script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
                    
                    document.head.appendChild(script);
                    
                    // 超时处理
                    setTimeout(() => {
                        reject(new Error(`Script load timeout: ${src}`));
                    }, config.timeout);
                });
            }
            
            // 加载CSS文件
            function loadCSS(href) {
                return new Promise((resolve, reject) => {
                    // 检查是否已加载
                    if (document.querySelector(`link[href="${href}"]`)) {
                        resolve();
                        return;
                    }
                    
                    const link = document.createElement('link');
                    link.rel = 'stylesheet';
                    link.href = href + (config.cacheBusting ? '?v=' + Date.now() : '');
                    
                    link.onload = () => resolve();
                    link.onerror = () => reject(new Error(`Failed to load CSS: ${href}`));
                    
                    document.head.appendChild(link);
                });
            }
            
            return {
                // 配置加载器
                configure(newConfig) {
                    Object.assign(config, newConfig);
                },
                
                // 注册组件依赖
                registerDependencies(componentName, dependencies) {
                    componentDependencies.set(componentName, dependencies);
                },
                
                // 加载组件
                async load(componentName, options = {}) {
                    // 避免重复加载
                    if (loadedComponents.has(componentName)) {
                        return Promise.resolve();
                    }
                    
                    // 如果正在加载，返回现有Promise
                    if (loadingPromises.has(componentName)) {
                        return loadingPromises.get(componentName);
                    }
                    
                    const loadPromise = this._loadComponent(componentName, options);
                    loadingPromises.set(componentName, loadPromise);
                    
                    try {
                        await loadPromise;
                        loadedComponents.add(componentName);
                        loadingPromises.delete(componentName);
                    } catch (error) {
                        loadingPromises.delete(componentName);
                        throw error;
                    }
                },
                
                // 内部加载方法
                async _loadComponent(componentName, options) {
                    const componentConfig = await this.getComponentConfig(componentName);
                    
                    // 加载依赖
                    if (componentConfig.dependencies) {
                        await Promise.all(
                            componentConfig.dependencies.map(dep => this.load(dep))
                        );
                    }
                    
                    // 加载CSS
                    if (componentConfig.css) {
                        await loadCSS(config.basePath + componentConfig.css);
                    }
                    
                    // 加载JavaScript
                    if (componentConfig.file) {
                        await loadScript(config.basePath + componentConfig.file);
                    }
                    
                    console.log(`Component "${componentName}" loaded successfully`);
                },
                
                // 获取组件配置
                async getComponentConfig(componentName) {
                    try {
                        const response = await fetch(`/api/components/${componentName}/config`);
                        if (!response.ok) {
                            throw new Error(`Component config not found: ${componentName}`);
                        }
                        return await response.json();
                    } catch (error) {
                        // 回退到默认配置
                        return {
                            file: `${componentName}.js`,
                            css: `${componentName}.css`,
                            dependencies: []
                        };
                    }
                },
                
                // 批量加载组件
                async loadMultiple(componentNames) {
                    return Promise.all(
                        componentNames.map(name => this.load(name))
                    );
                },
                
                // 预加载组件
                preload(componentNames) {
                    // 在空闲时间加载组件
                    if (window.requestIdleCallback) {
                        window.requestIdleCallback(() => {
                            this.loadMultiple(componentNames);
                        });
                    } else {
                        setTimeout(() => {
                            this.loadMultiple(componentNames);
                        }, 100);
                    }
                },
                
                // 检查组件是否已加载
                isLoaded(componentName) {
                    return loadedComponents.has(componentName);
                },
                
                // 获取已加载组件列表
                getLoaded() {
                    return Array.from(loadedComponents);
                }
            };
        })();
        '''
        
        return loader_js
    
    def get_component_config_api(self, component_name: str) -> Dict[str, Any]:
        """获取组件配置API响应"""
        if component_name in self.core_components:
            return self.core_components[component_name]
        else:
            return {
                'error': f'Component {component_name} not found',
                'available_components': list(self.core_components.keys())
            }
    
    def generate_component_registry(self) -> str:
        """生成组件注册表"""
        registry_js = f'''
        /**
         * 组件注册表
         * 包含所有可用组件的配置信息
         */
        
        window.ComponentRegistry = {{
            components: {json.dumps(self.core_components, indent=2, ensure_ascii=False)},
            
            // 获取组件配置
            getConfig(componentName) {{
                return this.components[componentName] || null;
            }},
            
            // 获取所有组件
            getAll() {{
                return Object.keys(this.components);
            }},
            
            // 检查组件是否存在
            exists(componentName) {{
                return componentName in this.components;
            }},
            
            // 获取组件依赖
            getDependencies(componentName) {{
                const config = this.getConfig(componentName);
                return config ? config.dependencies || [] : [];
            }},
            
            // 按类别获取组件
            getByCategory(category) {{
                return Object.entries(this.components)
                    .filter(([name, config]) => 
                        config.category === category
                    )
                    .map(([name, config]) => name);
            }}
        }};
        '''
        
        return registry_js


# 全局JS组件管理器
js_component_manager = JSComponentManager()


def init_js_components(app):
    """初始化JavaScript组件系统"""
    
    # 注册模板上下文处理器
    @app.context_processor
    def inject_js_component_context():
        """注入JS组件上下文到模板"""
        return {
            'js_component_manager': js_component_manager,
            'component_framework_js': js_component_manager.generate_component_framework(),
            'component_loader_js': js_component_manager.generate_component_loader(),
            'component_registry_js': js_component_manager.generate_component_registry()
        }
    
    # 注册组件配置API
    @app.route('/api/components/<component_name>/config')
    def get_component_config(component_name):
        """获取组件配置API"""
        try:
            config = js_component_manager.get_component_config_api(component_name)
            return jsonify(config)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/components')
    def list_components():
        """列出所有可用组件"""
        try:
            return jsonify({
                'components': js_component_manager.core_components,
                'count': len(js_component_manager.core_components)
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    current_app.logger.info("JavaScript组件系统已初始化")


def get_js_component_manager():
    """获取JS组件管理器实例"""
    return js_component_manager