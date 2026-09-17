/**
 * 工具提示组件 - 支持智能定位、内容格式化、触发控制、主题样式等提示功能
 */
class Tooltip extends BaseComponent {
    constructor() {
        super('tooltip');
        
        this.tooltips = new Map(); // 活跃的工具提示
        this.config = {
            defaultDelay: 500,
            hideDelay: 100,
            arrow: true,
            animation: 'fade',
            placement: 'top',
            trigger: 'hover',
            theme: 'dark',
            offset: 10,
            maxWidth: 300,
            zIndex: 1000,
            boundary: 'viewport'
        };
        
        this.eventHandlers = new Map(); // 事件处理器存储
        this.showTimer = null;
        this.hideTimer = null;
        this.currentTooltip = null;
        
        // 位置计算缓存
        this.positionCache = new Map();
        
        this.init();
    }

    init() {
        this.createTooltipContainer();
        this.bindEvents();
        this.initializeExistingTooltips();
    }

    /**
     * 创建工具提示容器
     */
    createTooltipContainer() {
        this.container = document.createElement('div');
        this.container.id = 'tooltip-container';
        this.container.className = 'tooltip-container';
        this.container.setAttribute('aria-live', 'polite');
        document.body.appendChild(this.container);
    }

    /**
     * 绑定全局事件
     */
    bindEvents() {
        // 全局鼠标移动 - 用于跟踪鼠标位置
        document.addEventListener('mousemove', (e) => {
            this.mouseX = e.clientX;
            this.mouseY = e.clientY;
        });

        // 全局点击 - 隐藏所有工具提示
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.tooltip, .tooltip-trigger')) {
                this.hideAll();
            }
        });

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAll();
            }
        });

        // 窗口滚动和调整
        window.addEventListener('scroll', () => {
            this.updatePositions();
        }, { passive: true });

        window.addEventListener('resize', () => {
            this.updatePositions();
            this.positionCache.clear();
        }, { passive: true });
    }

    /**
     * 初始化现有的工具提示
     */
    initializeExistingTooltips() {
        const elements = document.querySelectorAll('[data-tooltip], [title]');
        elements.forEach(element => this.addTooltip(element));
    }

    /**
     * 添加工具提示
     */
    addTooltip(element, options = {}) {
        if (!element) return null;

        const config = { ...this.config, ...options };
        
        // 获取内容
        let content = config.content || 
                     element.getAttribute('data-tooltip') || 
                     element.getAttribute('title') ||
                     element.getAttribute('data-title');

        if (!content && !config.html) return null;

        // 清除原生title属性避免重复显示
        if (element.hasAttribute('title')) {
            element.setAttribute('data-original-title', element.getAttribute('title'));
            element.removeAttribute('title');
        }

        const tooltipId = this.generateId();
        element.setAttribute('data-tooltip-id', tooltipId);
        element.classList.add('tooltip-trigger');

        const tooltipData = {
            id: tooltipId,
            element: element,
            content: content,
            config: config,
            tooltip: null,
            isVisible: false
        };

        this.tooltips.set(tooltipId, tooltipData);
        this.bindTooltipEvents(element, tooltipData);

        return tooltipId;
    }

    /**
     * 绑定工具提示事件
     */
    bindTooltipEvents(element, tooltipData) {
        const { config } = tooltipData;
        const handlers = {};

        // 根据触发方式绑定事件
        switch (config.trigger) {
            case 'hover':
                handlers.mouseenter = (e) => this.show(tooltipData.id, e);
                handlers.mouseleave = () => this.hide(tooltipData.id);
                break;

            case 'focus':
                handlers.focus = (e) => this.show(tooltipData.id, e);
                handlers.blur = () => this.hide(tooltipData.id);
                break;

            case 'click':
                handlers.click = (e) => {
                    e.preventDefault();
                    this.toggle(tooltipData.id, e);
                };
                break;

            case 'manual':
                // 手动控制，不绑定事件
                break;

            default:
                // 组合触发器
                if (config.trigger.includes('hover')) {
                    handlers.mouseenter = (e) => this.show(tooltipData.id, e);
                    handlers.mouseleave = () => this.hide(tooltipData.id);
                }
                if (config.trigger.includes('focus')) {
                    handlers.focus = (e) => this.show(tooltipData.id, e);
                    handlers.blur = () => this.hide(tooltipData.id);
                }
                if (config.trigger.includes('click')) {
                    handlers.click = (e) => {
                        e.preventDefault();
                        this.toggle(tooltipData.id, e);
                    };
                }
        }

        // 绑定事件处理器
        Object.entries(handlers).forEach(([event, handler]) => {
            element.addEventListener(event, handler);
        });

        // 存储处理器以便后续移除
        this.eventHandlers.set(tooltipData.id, handlers);
    }

    /**
     * 显示工具提示
     */
    show(tooltipId, event = null) {
        const tooltipData = this.tooltips.get(tooltipId);
        if (!tooltipData) return;

        // 清除隐藏定时器
        if (this.hideTimer) {
            clearTimeout(this.hideTimer);
            this.hideTimer = null;
        }

        // 如果已经显示，直接返回
        if (tooltipData.isVisible) return;

        // 隐藏其他工具提示（根据配置）
        if (tooltipData.config.exclusive !== false) {
            this.hideAll(tooltipId);
        }

        // 设置显示定时器
        this.showTimer = setTimeout(() => {
            this.createTooltip(tooltipData, event);
            this.emit('show', { tooltipId, element: tooltipData.element });
        }, tooltipData.config.delay || this.config.defaultDelay);
    }

    /**
     * 创建工具提示DOM
     */
    createTooltip(tooltipData, event = null) {
        if (tooltipData.tooltip) return; // 已存在

        const { config, content } = tooltipData;
        
        // 创建工具提示元素
        const tooltip = document.createElement('div');
        tooltip.className = `tooltip tooltip-${config.theme} tooltip-${config.placement}`;
        tooltip.setAttribute('role', 'tooltip');
        tooltip.setAttribute('id', `tooltip-${tooltipData.id}`);
        
        if (config.animation) {
            tooltip.classList.add(`tooltip-${config.animation}`);
        }

        // 设置样式
        Object.assign(tooltip.style, {
            position: 'absolute',
            zIndex: config.zIndex || this.config.zIndex,
            maxWidth: `${config.maxWidth || this.config.maxWidth}px`,
            visibility: 'hidden',
            opacity: '0'
        });

        // 创建内容
        this.setTooltipContent(tooltip, content, config);

        // 创建箭头
        if (config.arrow !== false) {
            const arrow = document.createElement('div');
            arrow.className = 'tooltip-arrow';
            tooltip.appendChild(arrow);
        }

        // 添加到容器
        this.container.appendChild(tooltip);
        tooltipData.tooltip = tooltip;

        // 计算位置并显示
        this.positionTooltip(tooltipData, event);
        this.showTooltip(tooltipData);
    }

    /**
     * 设置工具提示内容
     */
    setTooltipContent(tooltip, content, config) {
        const contentDiv = document.createElement('div');
        contentDiv.className = 'tooltip-content';

        if (config.html) {
            // HTML 内容
            if (typeof config.html === 'string') {
                contentDiv.innerHTML = this.sanitizeHTML(config.html);
            } else if (config.html instanceof HTMLElement) {
                contentDiv.appendChild(config.html.cloneNode(true));
            }
        } else {
            // 文本内容格式化
            const formattedContent = this.formatContent(content, config);
            
            if (config.allowHTML && this.isHTML(formattedContent)) {
                contentDiv.innerHTML = this.sanitizeHTML(formattedContent);
            } else {
                contentDiv.textContent = formattedContent;
            }
        }

        // 添加标题（如果有）
        if (config.title) {
            const title = document.createElement('div');
            title.className = 'tooltip-title';
            title.textContent = config.title;
            tooltip.appendChild(title);
        }

        tooltip.appendChild(contentDiv);

        // 添加关闭按钮（如果需要）
        if (config.closable) {
            const closeBtn = document.createElement('button');
            closeBtn.className = 'tooltip-close';
            closeBtn.innerHTML = '×';
            closeBtn.setAttribute('aria-label', '关闭提示');
            closeBtn.addEventListener('click', () => this.hide(tooltipData.id));
            tooltip.appendChild(closeBtn);
        }
    }

    /**
     * 内容格式化
     */
    formatContent(content, config) {
        if (!content) return '';

        let formatted = content;

        // 处理换行符
        if (config.preserveLineBreaks) {
            formatted = formatted.replace(/\n/g, '<br>');
        }

        // 处理特殊格式
        if (config.format) {
            switch (config.format) {
                case 'markdown':
                    formatted = this.parseSimpleMarkdown(formatted);
                    break;
                case 'currency':
                    formatted = this.formatCurrency(formatted);
                    break;
                case 'date':
                    formatted = this.formatDate(formatted);
                    break;
                case 'number':
                    formatted = this.formatNumber(formatted);
                    break;
            }
        }

        // 处理模板变量
        if (config.template) {
            formatted = this.processTemplate(formatted, config.template);
        }

        return formatted;
    }

    /**
     * 简单的Markdown解析
     */
    parseSimpleMarkdown(text) {
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    /**
     * 货币格式化
     */
    formatCurrency(value, currency = 'CNY') {
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency
        }).format(num);
    }

    /**
     * 日期格式化
     */
    formatDate(value) {
        const date = new Date(value);
        if (isNaN(date.getTime())) return value;
        
        return date.toLocaleDateString('zh-CN', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }

    /**
     * 数字格式化
     */
    formatNumber(value) {
        const num = parseFloat(value);
        if (isNaN(num)) return value;
        
        return new Intl.NumberFormat('zh-CN').format(num);
    }

    /**
     * 模板处理
     */
    processTemplate(content, templateData) {
        let result = content;
        
        Object.entries(templateData).forEach(([key, value]) => {
            const regex = new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, 'g');
            result = result.replace(regex, value);
        });
        
        return result;
    }

    /**
     * 智能定位工具提示
     */
    positionTooltip(tooltipData, event = null) {
        const { element, tooltip, config } = tooltipData;
        if (!tooltip) return;

        // 获取元素位置
        const elementRect = element.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        // 获取视口尺寸
        const viewport = {
            width: window.innerWidth,
            height: window.innerHeight,
            scrollX: window.scrollX,
            scrollY: window.scrollY
        };

        // 计算最佳位置
        const position = this.calculateOptimalPosition(
            elementRect, tooltipRect, viewport, config, event
        );

        // 应用位置
        Object.assign(tooltip.style, {
            left: `${position.x + viewport.scrollX}px`,
            top: `${position.y + viewport.scrollY}px`
        });

        // 更新箭头位置
        this.updateArrowPosition(tooltip, position.placement, elementRect, {
            x: position.x,
            y: position.y,
            width: tooltipRect.width,
            height: tooltipRect.height
        });

        // 更新CSS类
        tooltip.className = tooltip.className.replace(/tooltip-\w+(?=\s|$)/g, '');
        tooltip.classList.add(`tooltip-${position.placement}`);
    }

    /**
     * 计算最佳位置
     */
    calculateOptimalPosition(elementRect, tooltipRect, viewport, config, event) {
        const offset = config.offset || this.config.offset;
        let placement = config.placement || this.config.placement;
        
        // 如果是鼠标跟随模式
        if (config.followMouse && event) {
            return this.calculateMousePosition(event, tooltipRect, viewport, offset);
        }

        // 尝试首选位置
        let position = this.calculatePosition(placement, elementRect, tooltipRect, offset);
        
        // 检查是否超出边界
        if (this.isOutOfBounds(position, tooltipRect, viewport, config.boundary)) {
            // 尝试其他位置
            const alternatives = this.getAlternativePlacements(placement);
            
            for (const altPlacement of alternatives) {
                const altPosition = this.calculatePosition(altPlacement, elementRect, tooltipRect, offset);
                
                if (!this.isOutOfBounds(altPosition, tooltipRect, viewport, config.boundary)) {
                    position = altPosition;
                    placement = altPlacement;
                    break;
                }
            }
            
            // 如果所有位置都超出边界，调整到边界内
            if (this.isOutOfBounds(position, tooltipRect, viewport, config.boundary)) {
                position = this.adjustToBoundary(position, tooltipRect, viewport);
            }
        }

        return { ...position, placement };
    }

    /**
     * 计算鼠标跟随位置
     */
    calculateMousePosition(event, tooltipRect, viewport, offset) {
        let x = event.clientX + offset;
        let y = event.clientY + offset;

        // 边界检查和调整
        if (x + tooltipRect.width > viewport.width) {
            x = event.clientX - tooltipRect.width - offset;
        }
        
        if (y + tooltipRect.height > viewport.height) {
            y = event.clientY - tooltipRect.height - offset;
        }

        return { x: Math.max(0, x), y: Math.max(0, y), placement: 'mouse' };
    }

    /**
     * 根据placement计算位置
     */
    calculatePosition(placement, elementRect, tooltipRect, offset) {
        let x, y;

        switch (placement) {
            case 'top':
                x = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                y = elementRect.top - tooltipRect.height - offset;
                break;

            case 'bottom':
                x = elementRect.left + (elementRect.width - tooltipRect.width) / 2;
                y = elementRect.bottom + offset;
                break;

            case 'left':
                x = elementRect.left - tooltipRect.width - offset;
                y = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                break;

            case 'right':
                x = elementRect.right + offset;
                y = elementRect.top + (elementRect.height - tooltipRect.height) / 2;
                break;

            case 'top-start':
                x = elementRect.left;
                y = elementRect.top - tooltipRect.height - offset;
                break;

            case 'top-end':
                x = elementRect.right - tooltipRect.width;
                y = elementRect.top - tooltipRect.height - offset;
                break;

            case 'bottom-start':
                x = elementRect.left;
                y = elementRect.bottom + offset;
                break;

            case 'bottom-end':
                x = elementRect.right - tooltipRect.width;
                y = elementRect.bottom + offset;
                break;

            case 'left-start':
                x = elementRect.left - tooltipRect.width - offset;
                y = elementRect.top;
                break;

            case 'left-end':
                x = elementRect.left - tooltipRect.width - offset;
                y = elementRect.bottom - tooltipRect.height;
                break;

            case 'right-start':
                x = elementRect.right + offset;
                y = elementRect.top;
                break;

            case 'right-end':
                x = elementRect.right + offset;
                y = elementRect.bottom - tooltipRect.height;
                break;

            default:
                x = elementRect.left;
                y = elementRect.top - tooltipRect.height - offset;
        }

        return { x, y };
    }

    /**
     * 获取备选位置
     */
    getAlternativePlacements(placement) {
        const alternatives = {
            'top': ['bottom', 'left', 'right'],
            'bottom': ['top', 'left', 'right'],
            'left': ['right', 'top', 'bottom'],
            'right': ['left', 'top', 'bottom']
        };

        const base = placement.split('-')[0];
        return alternatives[base] || ['top', 'bottom', 'left', 'right'];
    }

    /**
     * 检查是否超出边界
     */
    isOutOfBounds(position, tooltipRect, viewport, boundary) {
        if (boundary === 'none') return false;

        const bounds = {
            left: 0,
            top: 0,
            right: viewport.width,
            bottom: viewport.height
        };

        return (
            position.x < bounds.left ||
            position.y < bounds.top ||
            position.x + tooltipRect.width > bounds.right ||
            position.y + tooltipRect.height > bounds.bottom
        );
    }

    /**
     * 调整到边界内
     */
    adjustToBoundary(position, tooltipRect, viewport) {
        return {
            x: Math.max(0, Math.min(position.x, viewport.width - tooltipRect.width)),
            y: Math.max(0, Math.min(position.y, viewport.height - tooltipRect.height))
        };
    }

    /**
     * 更新箭头位置
     */
    updateArrowPosition(tooltip, placement, elementRect, tooltipRect) {
        const arrow = tooltip.querySelector('.tooltip-arrow');
        if (!arrow) return;

        const arrowSize = 6; // 箭头尺寸
        
        // 清除之前的样式
        arrow.style.cssText = '';
        
        // 计算箭头位置
        switch (placement.split('-')[0]) {
            case 'top':
                arrow.style.bottom = `-${arrowSize}px`;
                arrow.style.left = '50%';
                arrow.style.transform = 'translateX(-50%)';
                break;

            case 'bottom':
                arrow.style.top = `-${arrowSize}px`;
                arrow.style.left = '50%';
                arrow.style.transform = 'translateX(-50%)';
                break;

            case 'left':
                arrow.style.right = `-${arrowSize}px`;
                arrow.style.top = '50%';
                arrow.style.transform = 'translateY(-50%)';
                break;

            case 'right':
                arrow.style.left = `-${arrowSize}px`;
                arrow.style.top = '50%';
                arrow.style.transform = 'translateY(-50%)';
                break;
        }

        // 调整箭头指向元素中心
        this.adjustArrowToElement(arrow, placement, elementRect, tooltipRect);
    }

    /**
     * 调整箭头指向元素
     */
    adjustArrowToElement(arrow, placement, elementRect, tooltipRect) {
        const base = placement.split('-')[0];
        
        if (base === 'top' || base === 'bottom') {
            // 水平调整
            const elementCenter = elementRect.left + elementRect.width / 2;
            const tooltipLeft = tooltipRect.x;
            const offset = elementCenter - tooltipLeft;
            const arrowLeft = Math.max(12, Math.min(offset, tooltipRect.width - 12));
            arrow.style.left = `${arrowLeft}px`;
        } else {
            // 垂直调整
            const elementCenter = elementRect.top + elementRect.height / 2;
            const tooltipTop = tooltipRect.y;
            const offset = elementCenter - tooltipTop;
            const arrowTop = Math.max(12, Math.min(offset, tooltipRect.height - 12));
            arrow.style.top = `${arrowTop}px`;
        }
    }

    /**
     * 显示动画
     */
    showTooltip(tooltipData) {
        const { tooltip, config } = tooltipData;
        
        tooltip.style.visibility = 'visible';
        
        // 触发重排以确保动画正常
        tooltip.offsetHeight;
        
        // 应用显示样式
        if (config.animation === 'fade') {
            tooltip.style.opacity = '1';
        } else if (config.animation === 'scale') {
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'scale(1)';
        } else if (config.animation === 'slide') {
            tooltip.style.opacity = '1';
            tooltip.style.transform = 'translateY(0)';
        }

        tooltipData.isVisible = true;
        this.currentTooltip = tooltipData.id;

        // 绑定工具提示内部事件
        this.bindTooltipInternalEvents(tooltip, tooltipData);
    }

    /**
     * 绑定工具提示内部事件
     */
    bindTooltipInternalEvents(tooltip, tooltipData) {
        // 鼠标悬停保持显示
        if (tooltipData.config.trigger === 'hover') {
            tooltip.addEventListener('mouseenter', () => {
                if (this.hideTimer) {
                    clearTimeout(this.hideTimer);
                    this.hideTimer = null;
                }
            });

            tooltip.addEventListener('mouseleave', () => {
                this.hide(tooltipData.id);
            });
        }

        // 可交互内容的事件委托
        tooltip.addEventListener('click', (e) => {
            if (e.target.matches('a, button, [data-action]')) {
                this.emit('tooltipAction', {
                    action: e.target.getAttribute('data-action'),
                    element: e.target,
                    tooltipId: tooltipData.id
                });
            }
        });
    }

    /**
     * 隐藏工具提示
     */
    hide(tooltipId) {
        const tooltipData = this.tooltips.get(tooltipId);
        if (!tooltipData || !tooltipData.isVisible) return;

        // 清除显示定时器
        if (this.showTimer) {
            clearTimeout(this.showTimer);
            this.showTimer = null;
        }

        const { tooltip, config } = tooltipData;
        
        // 设置隐藏定时器
        this.hideTimer = setTimeout(() => {
            this.hideTooltip(tooltipData);
            this.emit('hide', { tooltipId, element: tooltipData.element });
        }, config.hideDelay || this.config.hideDelay);
    }

    /**
     * 隐藏动画
     */
    hideTooltip(tooltipData) {
        const { tooltip, config } = tooltipData;
        if (!tooltip) return;

        // 应用隐藏样式
        if (config.animation === 'fade') {
            tooltip.style.opacity = '0';
        } else if (config.animation === 'scale') {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'scale(0.8)';
        } else if (config.animation === 'slide') {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(-10px)';
        }

        // 延迟移除DOM
        setTimeout(() => {
            if (tooltip.parentNode) {
                tooltip.parentNode.removeChild(tooltip);
            }
            tooltipData.tooltip = null;
            tooltipData.isVisible = false;
            
            if (this.currentTooltip === tooltipData.id) {
                this.currentTooltip = null;
            }
        }, 300);
    }

    /**
     * 切换显示状态
     */
    toggle(tooltipId, event = null) {
        const tooltipData = this.tooltips.get(tooltipId);
        if (!tooltipData) return;

        if (tooltipData.isVisible) {
            this.hide(tooltipId);
        } else {
            this.show(tooltipId, event);
        }
    }

    /**
     * 隐藏所有工具提示
     */
    hideAll(exceptId = null) {
        this.tooltips.forEach((tooltipData, id) => {
            if (id !== exceptId && tooltipData.isVisible) {
                this.hide(id);
            }
        });
    }

    /**
     * 更新所有工具提示位置
     */
    updatePositions() {
        this.tooltips.forEach((tooltipData) => {
            if (tooltipData.isVisible && tooltipData.tooltip) {
                this.positionTooltip(tooltipData);
            }
        });
    }

    /**
     * 更新工具提示内容
     */
    updateContent(tooltipId, content, options = {}) {
        const tooltipData = this.tooltips.get(tooltipId);
        if (!tooltipData) return;

        tooltipData.content = content;
        Object.assign(tooltipData.config, options);

        if (tooltipData.tooltip) {
            const contentDiv = tooltipData.tooltip.querySelector('.tooltip-content');
            if (contentDiv) {
                this.setTooltipContent(tooltipData.tooltip, content, tooltipData.config);
                // 重新定位
                this.positionTooltip(tooltipData);
            }
        }
    }

    /**
     * 移除工具提示
     */
    removeTooltip(tooltipId) {
        const tooltipData = this.tooltips.get(tooltipId);
        if (!tooltipData) return;

        // 隐藏工具提示
        if (tooltipData.isVisible) {
            this.hide(tooltipId);
        }

        // 移除事件监听器
        const handlers = this.eventHandlers.get(tooltipId);
        if (handlers) {
            Object.entries(handlers).forEach(([event, handler]) => {
                tooltipData.element.removeEventListener(event, handler);
            });
            this.eventHandlers.delete(tooltipId);
        }

        // 清理元素属性
        tooltipData.element.removeAttribute('data-tooltip-id');
        tooltipData.element.classList.remove('tooltip-trigger');

        // 恢复原生title
        const originalTitle = tooltipData.element.getAttribute('data-original-title');
        if (originalTitle) {
            tooltipData.element.setAttribute('title', originalTitle);
            tooltipData.element.removeAttribute('data-original-title');
        }

        this.tooltips.delete(tooltipId);
    }

    /**
     * 工具方法
     */
    generateId() {
        return 'tooltip_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    isHTML(str) {
        return /<\/?[a-z][\s\S]*>/i.test(str);
    }

    sanitizeHTML(html) {
        // 简单的HTML清理，实际使用建议使用专门的库如DOMPurify
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
            .replace(/on\w+="[^"]*"/gi, '');
    }

    /**
     * 静态方法 - 快速创建工具提示
     */
    static create(element, content, options = {}) {
        if (!window.tooltipInstance) {
            window.tooltipInstance = new Tooltip();
        }
        return window.tooltipInstance.addTooltip(element, { content, ...options });
    }

    /**
     * 静态方法 - 显示工具提示
     */
    static show(element, content, options = {}) {
        const tooltipId = Tooltip.create(element, content, options);
        if (tooltipId && window.tooltipInstance) {
            window.tooltipInstance.show(tooltipId);
        }
        return tooltipId;
    }

    /**
     * 静态方法 - 隐藏工具提示
     */
    static hide(tooltipId) {
        if (window.tooltipInstance) {
            window.tooltipInstance.hide(tooltipId);
        }
    }

    /**
     * 清理资源
     */
    destroy() {
        // 清理所有工具提示
        const tooltipIds = Array.from(this.tooltips.keys());
        tooltipIds.forEach(id => this.removeTooltip(id));

        // 清理定时器
        if (this.showTimer) {
            clearTimeout(this.showTimer);
        }
        if (this.hideTimer) {
            clearTimeout(this.hideTimer);
        }

        // 移除容器
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }

        super.destroy();
    }
}

// 自动初始化
if (typeof window !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.tooltipInstance) {
            window.tooltipInstance = new Tooltip();
        }
    });
}

// 导出
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Tooltip;
} else if (typeof window !== 'undefined') {
    window.Tooltip = Tooltip;
}