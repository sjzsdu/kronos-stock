/**
 * 模态对话框组件
 * 支持多层级模态、动画效果、拖拽调整、键盘导航等功能
 */

class Modal extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'Modal';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            title: '',
            content: '',
            size: 'medium', // small, medium, large, fullscreen, auto
            animation: 'fade', // fade, slide, zoom, flip
            backdrop: true, // 是否显示遮罩
            closable: true, // 是否可关闭
            draggable: false, // 是否可拖拽
            resizable: false, // 是否可调整大小
            persistent: false, // 点击遮罩是否关闭
            autoFocus: true, // 自动聚焦
            trapFocus: true, // 焦点陷阱
            
            // 按钮配置
            showCloseButton: true,
            buttons: [], // { text: 'OK', type: 'primary', action: 'confirm' }
            
            // 位置配置
            position: 'center', // center, top, bottom, custom
            offset: { x: 0, y: 0 },
            
            // 事件回调
            onShow: null,
            onHide: null,
            onConfirm: null,
            onCancel: null
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // 状态管理
        this.isVisible = false;
        this.isAnimating = false;
        this.zIndex = this.getNextZIndex();
        
        // 拖拽状态
        this.isDragging = false;
        this.dragStartPos = { x: 0, y: 0 };
        this.modalStartPos = { x: 0, y: 0 };
        
        // 调整大小状态
        this.isResizing = false;
        this.resizeHandle = null;
        this.resizeStartSize = { width: 0, height: 0 };
        
        // 焦点管理
        this.previousActiveElement = null;
        this.focusableElements = [];
        this.currentFocusIndex = -1;
        
        // 事件绑定
        this.boundHandlers = {
            keydown: this.handleKeydown.bind(this),
            mousedown: this.handleMouseDown.bind(this),
            mousemove: this.handleMouseMove.bind(this),
            mouseup: this.handleMouseUp.bind(this),
            resize: this.handleWindowResize.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            this.createModal();
            this.setupEventListeners();
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化模态对话框组件失败');
            throw error;
        }
    }
    
    /**
     * 创建模态对话框
     */
    createModal() {
        // 创建模态容器
        this.modal = document.createElement('div');
        this.modal.className = `modal modal-${this.config.size} modal-${this.config.animation}`;
        this.modal.style.zIndex = this.zIndex;
        
        // 创建遮罩层
        if (this.config.backdrop) {
            this.backdrop = document.createElement('div');
            this.backdrop.className = 'modal-backdrop';
            this.modal.appendChild(this.backdrop);
        }
        
        // 创建对话框主体
        this.dialog = document.createElement('div');
        this.dialog.className = `modal-dialog ${this.config.draggable ? 'draggable' : ''}`;
        this.dialog.setAttribute('role', 'dialog');
        this.dialog.setAttribute('aria-modal', 'true');
        
        if (this.config.title) {
            this.dialog.setAttribute('aria-labelledby', `modal-title-${this.getId()}`);
        }
        
        this.dialog.innerHTML = `
            <div class="modal-content">
                ${this.config.title ? `
                    <div class="modal-header ${this.config.draggable ? 'draggable-handle' : ''}">
                        <h3 class="modal-title" id="modal-title-${this.getId()}">${this.config.title}</h3>
                        ${this.config.showCloseButton ? `
                            <button type="button" class="modal-close" aria-label="关闭对话框">
                                <i class="fas fa-times"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : ''}
                
                <div class="modal-body">
                    ${this.config.content}
                </div>
                
                ${this.config.buttons.length > 0 ? `
                    <div class="modal-footer">
                        ${this.config.buttons.map(btn => `
                            <button type="button" 
                                    class="modal-btn modal-btn-${btn.type || 'secondary'}" 
                                    data-action="${btn.action || 'close'}">
                                ${btn.text}
                            </button>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
            
            ${this.config.resizable ? `
                <div class="resize-handles">
                    <div class="resize-handle resize-n" data-direction="n"></div>
                    <div class="resize-handle resize-e" data-direction="e"></div>
                    <div class="resize-handle resize-s" data-direction="s"></div>
                    <div class="resize-handle resize-w" data-direction="w"></div>
                    <div class="resize-handle resize-ne" data-direction="ne"></div>
                    <div class="resize-handle resize-nw" data-direction="nw"></div>
                    <div class="resize-handle resize-se" data-direction="se"></div>
                    <div class="resize-handle resize-sw" data-direction="sw"></div>
                </div>
            ` : ''}
        `;
        
        this.modal.appendChild(this.dialog);
        
        // 获取关键元素引用
        this.elements = {
            backdrop: this.backdrop,
            dialog: this.dialog,
            content: this.dialog.querySelector('.modal-content'),
            header: this.dialog.querySelector('.modal-header'),
            title: this.dialog.querySelector('.modal-title'),
            closeBtn: this.dialog.querySelector('.modal-close'),
            body: this.dialog.querySelector('.modal-body'),
            footer: this.dialog.querySelector('.modal-footer'),
            buttons: this.dialog.querySelectorAll('.modal-btn')
        };
        
        // 初始化位置
        this.setPosition();
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 关闭按钮
        if (this.elements.closeBtn) {
            this.elements.closeBtn.addEventListener('click', () => this.hide());
        }
        
        // 遮罩点击
        if (this.backdrop && !this.config.persistent) {
            this.backdrop.addEventListener('click', () => this.hide());
        }
        
        // 按钮事件
        this.elements.buttons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.handleButtonClick(action, e.target);
            });
        });
        
        // 拖拽事件
        if (this.config.draggable && this.elements.header) {
            this.elements.header.addEventListener('mousedown', (e) => {
                if (e.target.closest('.modal-close')) return;
                this.startDragging(e);
            });
        }
        
        // 调整大小事件
        if (this.config.resizable) {
            this.dialog.querySelectorAll('.resize-handle').forEach(handle => {
                handle.addEventListener('mousedown', (e) => {
                    this.startResizing(e, handle.dataset.direction);
                });
            });
        }
        
        // 全局事件
        document.addEventListener('keydown', this.boundHandlers.keydown);
        document.addEventListener('mousemove', this.boundHandlers.mousemove);
        document.addEventListener('mouseup', this.boundHandlers.mouseup);
        window.addEventListener('resize', this.boundHandlers.resize);
    }
    
    /**
     * 显示模态对话框
     */
    async show() {
        if (this.isVisible || this.isAnimating) return;
        
        this.isAnimating = true;
        
        // 保存当前焦点元素
        this.previousActiveElement = document.activeElement;
        
        // 添加到DOM
        document.body.appendChild(this.modal);
        
        // 注册到全局管理器
        Modal.register(this);
        
        // 添加body类
        document.body.classList.add('modal-open');
        
        // 强制重排以启用动画
        this.modal.offsetHeight;
        
        // 显示动画
        this.modal.classList.add('show');
        
        // 等待动画完成
        await this.waitForAnimation();
        
        this.isVisible = true;
        this.isAnimating = false;
        
        // 设置焦点
        if (this.config.autoFocus) {
            this.setInitialFocus();
        }
        
        // 更新焦点元素列表
        this.updateFocusableElements();
        
        // 触发事件
        if (this.config.onShow) {
            this.config.onShow(this);
        }
        
        this.emit('show', { modal: this });
    }
    
    /**
     * 隐藏模态对话框
     */
    async hide() {
        if (!this.isVisible || this.isAnimating) return;
        
        this.isAnimating = true;
        
        // 隐藏动画
        this.modal.classList.remove('show');
        this.modal.classList.add('hide');
        
        // 等待动画完成
        await this.waitForAnimation();
        
        // 从DOM移除
        if (this.modal.parentNode) {
            this.modal.parentNode.removeChild(this.modal);
        }
        
        // 从全局管理器注销
        Modal.unregister(this);
        
        // 移除body类（如果没有其他模态）
        if (Modal.getActiveModals().length === 0) {
            document.body.classList.remove('modal-open');
        }
        
        this.isVisible = false;
        this.isAnimating = false;
        
        // 恢复焦点
        if (this.previousActiveElement) {
            this.previousActiveElement.focus();
            this.previousActiveElement = null;
        }
        
        // 触发事件
        if (this.config.onHide) {
            this.config.onHide(this);
        }
        
        this.emit('hide', { modal: this });
    }
    
    /**
     * 等待动画完成
     */
    waitForAnimation() {
        return new Promise(resolve => {
            const duration = this.getAnimationDuration();
            setTimeout(resolve, duration);
        });
    }
    
    /**
     * 获取动画持续时间
     */
    getAnimationDuration() {
        const computed = getComputedStyle(this.modal);
        const duration = computed.transitionDuration || computed.animationDuration;
        return parseFloat(duration) * 1000 || 300;
    }
    
    /**
     * 设置位置
     */
    setPosition() {
        const positions = {
            center: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
            top: { top: '10%', left: '50%', transform: 'translateX(-50%)' },
            bottom: { bottom: '10%', left: '50%', transform: 'translateX(-50%)' }
        };
        
        const pos = positions[this.config.position];
        if (pos) {
            Object.assign(this.dialog.style, pos);
        }
        
        // 自定义偏移
        if (this.config.offset.x || this.config.offset.y) {
            const currentTransform = this.dialog.style.transform || '';
            this.dialog.style.transform = 
                `${currentTransform} translate(${this.config.offset.x}px, ${this.config.offset.y}px)`;
        }
    }
    
    /**
     * 设置内容
     */
    setContent(content) {
        if (this.elements.body) {
            this.elements.body.innerHTML = content;
        }
        this.config.content = content;
        this.updateFocusableElements();
    }
    
    /**
     * 设置标题
     */
    setTitle(title) {
        if (this.elements.title) {
            this.elements.title.textContent = title;
        }
        this.config.title = title;
    }
    
    /**
     * 处理按钮点击
     */
    handleButtonClick(action, button) {
        const eventData = { action, button, modal: this };
        
        switch (action) {
            case 'confirm':
                if (this.config.onConfirm) {
                    const result = this.config.onConfirm(eventData);
                    if (result === false) return; // 阻止关闭
                }
                this.emit('confirm', eventData);
                this.hide();
                break;
                
            case 'cancel':
                if (this.config.onCancel) {
                    const result = this.config.onCancel(eventData);
                    if (result === false) return; // 阻止关闭
                }
                this.emit('cancel', eventData);
                this.hide();
                break;
                
            default:
                this.emit('buttonClick', eventData);
                if (action === 'close' || !action) {
                    this.hide();
                }
        }
    }
    
    /**
     * 键盘事件处理
     */
    handleKeydown(event) {
        if (!this.isVisible || this !== Modal.getTopModal()) return;
        
        switch (event.key) {
            case 'Escape':
                if (this.config.closable) {
                    event.preventDefault();
                    this.hide();
                }
                break;
                
            case 'Tab':
                if (this.config.trapFocus) {
                    this.handleTabNavigation(event);
                }
                break;
                
            case 'Enter':
                if (event.target.classList.contains('modal-btn')) {
                    event.preventDefault();
                    event.target.click();
                }
                break;
        }
    }
    
    /**
     * Tab导航处理
     */
    handleTabNavigation(event) {
        this.updateFocusableElements();
        
        if (this.focusableElements.length === 0) return;
        
        const currentIndex = this.focusableElements.indexOf(document.activeElement);
        let nextIndex;
        
        if (event.shiftKey) {
            // Shift+Tab - 向前
            nextIndex = currentIndex <= 0 ? this.focusableElements.length - 1 : currentIndex - 1;
        } else {
            // Tab - 向后
            nextIndex = currentIndex >= this.focusableElements.length - 1 ? 0 : currentIndex + 1;
        }
        
        event.preventDefault();
        this.focusableElements[nextIndex].focus();
    }
    
    /**
     * 更新可聚焦元素列表
     */
    updateFocusableElements() {
        const selectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
        this.focusableElements = Array.from(this.dialog.querySelectorAll(selectors))
            .filter(el => !el.disabled && !el.hidden);
    }
    
    /**
     * 设置初始焦点
     */
    setInitialFocus() {
        this.updateFocusableElements();
        
        // 优先级：第一个主按钮 > 关闭按钮 > 第一个可聚焦元素
        let targetElement = this.dialog.querySelector('.modal-btn-primary') ||
                          this.elements.closeBtn ||
                          this.focusableElements[0];
        
        if (targetElement) {
            targetElement.focus();
        }
    }
    
    /**
     * 开始拖拽
     */
    startDragging(event) {
        if (!this.config.draggable) return;
        
        event.preventDefault();
        this.isDragging = true;
        
        this.dragStartPos = { x: event.clientX, y: event.clientY };
        
        const rect = this.dialog.getBoundingClientRect();
        this.modalStartPos = { x: rect.left, y: rect.top };
        
        this.dialog.classList.add('dragging');
        document.body.classList.add('dragging');
    }
    
    /**
     * 处理拖拽移动
     */
    handleDragMove(event) {
        if (!this.isDragging) return;
        
        const deltaX = event.clientX - this.dragStartPos.x;
        const deltaY = event.clientY - this.dragStartPos.y;
        
        const newX = this.modalStartPos.x + deltaX;
        const newY = this.modalStartPos.y + deltaY;
        
        // 边界检测
        const maxX = window.innerWidth - this.dialog.offsetWidth;
        const maxY = window.innerHeight - this.dialog.offsetHeight;
        
        const constrainedX = Math.max(0, Math.min(newX, maxX));
        const constrainedY = Math.max(0, Math.min(newY, maxY));
        
        this.dialog.style.left = constrainedX + 'px';
        this.dialog.style.top = constrainedY + 'px';
        this.dialog.style.transform = 'none';
    }
    
    /**
     * 开始调整大小
     */
    startResizing(event, direction) {
        if (!this.config.resizable) return;
        
        event.preventDefault();
        event.stopPropagation();
        
        this.isResizing = true;
        this.resizeHandle = direction;
        this.dragStartPos = { x: event.clientX, y: event.clientY };
        
        const rect = this.dialog.getBoundingClientRect();
        this.resizeStartSize = { width: rect.width, height: rect.height };
        this.modalStartPos = { x: rect.left, y: rect.top };
        
        this.dialog.classList.add('resizing');
        document.body.classList.add('resizing');
    }
    
    /**
     * 处理调整大小移动
     */
    handleResizeMove(event) {
        if (!this.isResizing) return;
        
        const deltaX = event.clientX - this.dragStartPos.x;
        const deltaY = event.clientY - this.dragStartPos.y;
        
        let newWidth = this.resizeStartSize.width;
        let newHeight = this.resizeStartSize.height;
        let newX = this.modalStartPos.x;
        let newY = this.modalStartPos.y;
        
        // 根据调整方向计算新尺寸和位置
        const direction = this.resizeHandle;
        
        if (direction.includes('e')) {
            newWidth += deltaX;
        }
        if (direction.includes('w')) {
            newWidth -= deltaX;
            newX += deltaX;
        }
        if (direction.includes('s')) {
            newHeight += deltaY;
        }
        if (direction.includes('n')) {
            newHeight -= deltaY;
            newY += deltaY;
        }
        
        // 最小尺寸限制
        const minWidth = 300;
        const minHeight = 200;
        
        newWidth = Math.max(newWidth, minWidth);
        newHeight = Math.max(newHeight, minHeight);
        
        // 最大尺寸限制
        const maxWidth = window.innerWidth - 40;
        const maxHeight = window.innerHeight - 40;
        
        newWidth = Math.min(newWidth, maxWidth);
        newHeight = Math.min(newHeight, maxHeight);
        
        // 应用新尺寸和位置
        this.dialog.style.width = newWidth + 'px';
        this.dialog.style.height = newHeight + 'px';
        this.dialog.style.left = newX + 'px';
        this.dialog.style.top = newY + 'px';
        this.dialog.style.transform = 'none';
    }
    
    /**
     * 鼠标按下事件
     */
    handleMouseDown(event) {
        // 这里可以处理其他鼠标按下事件
    }
    
    /**
     * 鼠标移动事件
     */
    handleMouseMove(event) {
        if (this.isDragging) {
            this.handleDragMove(event);
        } else if (this.isResizing) {
            this.handleResizeMove(event);
        }
    }
    
    /**
     * 鼠标释放事件
     */
    handleMouseUp(event) {
        if (this.isDragging) {
            this.isDragging = false;
            this.dialog.classList.remove('dragging');
            document.body.classList.remove('dragging');
        }
        
        if (this.isResizing) {
            this.isResizing = false;
            this.resizeHandle = null;
            this.dialog.classList.remove('resizing');
            document.body.classList.remove('resizing');
        }
    }
    
    /**
     * 窗口大小变化处理
     */
    handleWindowResize() {
        if (this.isVisible && this.config.size === 'fullscreen') {
            // 全屏模式下重新调整
            this.setPosition();
        }
    }
    
    /**
     * 获取下一个z-index值
     */
    getNextZIndex() {
        return Modal.getNextZIndex();
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 隐藏模态
        if (this.isVisible) {
            this.hide();
        }
        
        // 移除事件监听器
        document.removeEventListener('keydown', this.boundHandlers.keydown);
        document.removeEventListener('mousemove', this.boundHandlers.mousemove);
        document.removeEventListener('mouseup', this.boundHandlers.mouseup);
        window.removeEventListener('resize', this.boundHandlers.resize);
        
        // 从全局管理器移除
        Modal.unregister(this);
        
        super.destroy();
    }
}

// 静态方法和属性 - 全局模态管理器
Modal.activeModals = [];
Modal.baseZIndex = 1000;

/**
 * 注册活跃模态
 */
Modal.register = function(modal) {
    Modal.activeModals.push(modal);
};

/**
 * 注销模态
 */
Modal.unregister = function(modal) {
    const index = Modal.activeModals.indexOf(modal);
    if (index > -1) {
        Modal.activeModals.splice(index, 1);
    }
};

/**
 * 获取活跃模态列表
 */
Modal.getActiveModals = function() {
    return Modal.activeModals.slice();
};

/**
 * 获取顶层模态
 */
Modal.getTopModal = function() {
    return Modal.activeModals[Modal.activeModals.length - 1];
};

/**
 * 获取下一个z-index值
 */
Modal.getNextZIndex = function() {
    return Modal.baseZIndex + Modal.activeModals.length * 10;
};

/**
 * 关闭所有模态
 */
Modal.closeAll = function() {
    const modals = Modal.getActiveModals();
    modals.forEach(modal => modal.hide());
};

/**
 * 创建简单的确认对话框
 */
Modal.confirm = function(options) {
    return new Promise(resolve => {
        const modal = new Modal(document.body, {
            title: options.title || '确认',
            content: options.message || '确定要执行此操作吗？',
            size: 'small',
            buttons: [
                { text: '取消', type: 'secondary', action: 'cancel' },
                { text: '确认', type: 'primary', action: 'confirm' }
            ],
            onConfirm: () => resolve(true),
            onCancel: () => resolve(false),
            onHide: () => resolve(false)
        });
        
        modal.init().then(() => modal.show());
    });
};

/**
 * 创建简单的提示对话框
 */
Modal.alert = function(options) {
    return new Promise(resolve => {
        const modal = new Modal(document.body, {
            title: options.title || '提示',
            content: options.message || '',
            size: 'small',
            buttons: [
                { text: '确定', type: 'primary', action: 'confirm' }
            ],
            onConfirm: () => resolve(),
            onHide: () => resolve()
        });
        
        modal.init().then(() => modal.show());
    });
};

// 注册组件
if (typeof JSComponentManager !== 'undefined') {
    JSComponentManager.register('modal', Modal);
}

// 导出组件（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Modal;
}