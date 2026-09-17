/**
 * 导航组件
 * 提供动态菜单、面包屑、标签页、侧边栏等导航功能
 */

class Navigation extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'Navigation';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            type: 'navbar', // navbar, sidebar, tabs, breadcrumb, dropdown
            position: 'top', // top, bottom, left, right
            sticky: false, // 是否固定位置
            collapsible: true, // 是否可折叠
            responsive: true, // 响应式
            
            // 菜单数据
            items: [],
            
            // 样式配置
            theme: 'light', // light, dark, auto
            variant: 'default', // default, minimal, compact
            
            // 行为配置
            activeClass: 'active',
            expandOnHover: false,
            closeOnClick: true,
            multiLevel: true,
            
            // 标签页配置
            closable: false, // 标签是否可关闭
            draggable: false, // 标签是否可拖拽
            
            // 侧边栏配置
            collapsedWidth: '60px',
            expandedWidth: '250px',
            
            // 事件回调
            onItemClick: null,
            onItemSelect: null,
            beforeNavigate: null
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // 状态管理
        this.isCollapsed = false;
        this.activeItem = null;
        this.openDropdowns = new Set();
        this.history = [];
        
        // 标签页管理
        this.tabs = new Map();
        this.activeTab = null;
        
        // 事件绑定
        this.boundHandlers = {
            resize: this.handleResize.bind(this),
            click: this.handleGlobalClick.bind(this),
            keydown: this.handleKeydown.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            this.createNavigation();
            this.setupEventListeners();
            this.renderItems();
            
            if (this.config.responsive) {
                this.initResponsive();
            }
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化导航组件失败');
            throw error;
        }
    }
    
    /**
     * 创建导航结构
     */
    createNavigation() {
        this.container.className = `navigation navigation-${this.config.type} navigation-${this.config.theme} navigation-${this.config.variant}`;
        
        if (this.config.position) {
            this.container.classList.add(`navigation-${this.config.position}`);
        }
        
        if (this.config.sticky) {
            this.container.classList.add('navigation-sticky');
        }
        
        // 根据导航类型创建不同结构
        switch (this.config.type) {
            case 'navbar':
                this.createNavbar();
                break;
            case 'sidebar':
                this.createSidebar();
                break;
            case 'tabs':
                this.createTabs();
                break;
            case 'breadcrumb':
                this.createBreadcrumb();
                break;
            case 'dropdown':
                this.createDropdown();
                break;
        }
    }
    
    /**
     * 创建顶部导航栏
     */
    createNavbar() {
        this.container.innerHTML = `
            <div class="navbar-container">
                <div class="navbar-brand">
                    <a href="#" class="brand-link">
                        <img class="brand-logo" src="" alt="Logo" style="display: none;">
                        <span class="brand-text"></span>
                    </a>
                </div>
                
                ${this.config.collapsible ? `
                    <button class="navbar-toggle" aria-label="切换导航菜单">
                        <span class="toggle-icon">
                            <span></span>
                            <span></span>
                            <span></span>
                        </span>
                    </button>
                ` : ''}
                
                <div class="navbar-collapse">
                    <ul class="navbar-nav"></ul>
                </div>
                
                <div class="navbar-actions">
                    <!-- 用户操作区域 -->
                </div>
            </div>
        `;
        
        this.elements = {
            container: this.container.querySelector('.navbar-container'),
            brand: this.container.querySelector('.navbar-brand'),
            toggle: this.container.querySelector('.navbar-toggle'),
            collapse: this.container.querySelector('.navbar-collapse'),
            nav: this.container.querySelector('.navbar-nav'),
            actions: this.container.querySelector('.navbar-actions')
        };
    }
    
    /**
     * 创建侧边栏
     */
    createSidebar() {
        this.container.innerHTML = `
            <div class="sidebar-header">
                <div class="sidebar-brand">
                    <img class="brand-logo" src="" alt="Logo" style="display: none;">
                    <span class="brand-text"></span>
                </div>
                ${this.config.collapsible ? `
                    <button class="sidebar-toggle" aria-label="折叠侧边栏">
                        <i class="fas fa-angle-left"></i>
                    </button>
                ` : ''}
            </div>
            
            <div class="sidebar-content">
                <nav class="sidebar-nav">
                    <ul class="nav-list"></ul>
                </nav>
            </div>
            
            <div class="sidebar-footer">
                <!-- 底部内容 -->
            </div>
        `;
        
        this.elements = {
            header: this.container.querySelector('.sidebar-header'),
            brand: this.container.querySelector('.sidebar-brand'),
            toggle: this.container.querySelector('.sidebar-toggle'),
            content: this.container.querySelector('.sidebar-content'),
            nav: this.container.querySelector('.nav-list'),
            footer: this.container.querySelector('.sidebar-footer')
        };
        
        // 设置侧边栏宽度
        this.container.style.width = this.config.expandedWidth;
    }
    
    /**
     * 创建标签页
     */
    createTabs() {
        this.container.innerHTML = `
            <div class="tabs-header">
                <div class="tabs-nav-wrapper">
                    <button class="tabs-scroll-btn tabs-scroll-left" style="display: none;">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <div class="tabs-nav-container">
                        <ul class="tabs-nav"></ul>
                    </div>
                    <button class="tabs-scroll-btn tabs-scroll-right" style="display: none;">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
                <div class="tabs-actions">
                    ${this.config.closable ? `
                        <button class="tabs-close-all" title="关闭所有标签">
                            <i class="fas fa-times"></i>
                        </button>
                    ` : ''}
                </div>
            </div>
            
            <div class="tabs-content">
                <!-- 标签页内容区域 -->
            </div>
        `;
        
        this.elements = {
            header: this.container.querySelector('.tabs-header'),
            navWrapper: this.container.querySelector('.tabs-nav-wrapper'),
            navContainer: this.container.querySelector('.tabs-nav-container'),
            nav: this.container.querySelector('.tabs-nav'),
            scrollLeft: this.container.querySelector('.tabs-scroll-left'),
            scrollRight: this.container.querySelector('.tabs-scroll-right'),
            actions: this.container.querySelector('.tabs-actions'),
            content: this.container.querySelector('.tabs-content')
        };
    }
    
    /**
     * 创建面包屑
     */
    createBreadcrumb() {
        this.container.innerHTML = `
            <ol class="breadcrumb-list" role="navigation" aria-label="面包屑导航">
                <!-- 面包屑项目 -->
            </ol>
        `;
        
        this.elements = {
            list: this.container.querySelector('.breadcrumb-list')
        };
    }
    
    /**
     * 创建下拉菜单
     */
    createDropdown() {
        this.container.innerHTML = `
            <div class="dropdown-trigger">
                <button class="dropdown-button" aria-haspopup="true" aria-expanded="false">
                    <span class="dropdown-text">请选择</span>
                    <i class="dropdown-icon fas fa-chevron-down"></i>
                </button>
            </div>
            
            <div class="dropdown-menu" role="menu">
                <ul class="dropdown-list"></ul>
            </div>
        `;
        
        this.elements = {
            trigger: this.container.querySelector('.dropdown-trigger'),
            button: this.container.querySelector('.dropdown-button'),
            text: this.container.querySelector('.dropdown-text'),
            icon: this.container.querySelector('.dropdown-icon'),
            menu: this.container.querySelector('.dropdown-menu'),
            list: this.container.querySelector('.dropdown-list')
        };
    }
    
    /**
     * 设置事件监听器
     */
    setupEventListeners() {
        // 切换按钮
        if (this.elements.toggle) {
            this.elements.toggle.addEventListener('click', () => {
                this.toggle();
            });
        }
        
        // 全局点击事件
        document.addEventListener('click', this.boundHandlers.click);
        
        // 键盘事件
        this.container.addEventListener('keydown', this.boundHandlers.keydown);
        
        // 窗口大小变化
        if (this.config.responsive) {
            window.addEventListener('resize', this.boundHandlers.resize);
        }
        
        // 标签页滚动按钮
        if (this.config.type === 'tabs') {
            this.elements.scrollLeft?.addEventListener('click', () => this.scrollTabs('left'));
            this.elements.scrollRight?.addEventListener('click', () => this.scrollTabs('right'));
        }
    }
    
    /**
     * 渲染导航项目
     */
    renderItems() {
        if (!this.config.items || this.config.items.length === 0) return;
        
        const targetContainer = this.getItemsContainer();
        if (!targetContainer) return;
        
        targetContainer.innerHTML = '';
        
        this.config.items.forEach(item => {
            const element = this.createItemElement(item);
            targetContainer.appendChild(element);
        });
        
        // 标签页需要更新滚动状态
        if (this.config.type === 'tabs') {
            this.updateTabsScroll();
        }
    }
    
    /**
     * 获取项目容器
     */
    getItemsContainer() {
        switch (this.config.type) {
            case 'navbar':
                return this.elements.nav;
            case 'sidebar':
                return this.elements.nav;
            case 'tabs':
                return this.elements.nav;
            case 'breadcrumb':
                return this.elements.list;
            case 'dropdown':
                return this.elements.list;
            default:
                return null;
        }
    }
    
    /**
     * 创建导航项元素
     */
    createItemElement(item, level = 0) {
        const li = document.createElement('li');
        li.className = 'nav-item';
        li.dataset.itemId = item.id || this.generateId();
        
        if (item.active) {
            li.classList.add(this.config.activeClass);
            this.activeItem = item;
        }
        
        if (item.disabled) {
            li.classList.add('nav-item-disabled');
        }
        
        if (level > 0) {
            li.classList.add(`nav-item-level-${level}`);
        }
        
        // 创建链接或按钮
        const linkElement = document.createElement(item.href ? 'a' : 'button');
        linkElement.className = 'nav-link';
        
        if (item.href) {
            linkElement.href = item.href;
            linkElement.setAttribute('data-navigate', 'true');
        }
        
        // 图标
        if (item.icon) {
            const icon = document.createElement('i');
            icon.className = item.icon;
            linkElement.appendChild(icon);
        }
        
        // 文本
        const text = document.createElement('span');
        text.className = 'nav-text';
        text.textContent = item.text || item.label;
        linkElement.appendChild(text);
        
        // 徽章
        if (item.badge) {
            const badge = document.createElement('span');
            badge.className = `nav-badge ${item.badge.type || 'primary'}`;
            badge.textContent = item.badge.text || item.badge.count;
            linkElement.appendChild(badge);
        }
        
        // 子菜单指示器
        if (item.children && item.children.length > 0) {
            const indicator = document.createElement('i');
            indicator.className = 'nav-indicator fas fa-chevron-right';
            linkElement.appendChild(indicator);
            
            li.classList.add('nav-item-parent');
        }
        
        li.appendChild(linkElement);
        
        // 创建子菜单
        if (item.children && item.children.length > 0 && this.config.multiLevel) {
            const submenu = document.createElement('ul');
            submenu.className = 'nav-submenu';
            
            item.children.forEach(child => {
                const childElement = this.createItemElement(child, level + 1);
                submenu.appendChild(childElement);
            });
            
            li.appendChild(submenu);
        }
        
        // 绑定事件
        linkElement.addEventListener('click', (e) => {
            this.handleItemClick(e, item, li);
        });
        
        // 鼠标悬停事件
        if (this.config.expandOnHover && item.children) {
            li.addEventListener('mouseenter', () => {
                this.showSubmenu(li);
            });
            
            li.addEventListener('mouseleave', () => {
                this.hideSubmenu(li);
            });
        }
        
        return li;
    }
    
    /**
     * 处理项目点击
     */
    handleItemClick(event, item, element) {
        if (item.disabled) {
            event.preventDefault();
            return;
        }
        
        // 阻止链接默认行为（如果有自定义处理）
        if (this.config.beforeNavigate) {
            const result = this.config.beforeNavigate(item, element);
            if (result === false) {
                event.preventDefault();
                return;
            }
        }
        
        // 处理子菜单切换
        if (item.children && item.children.length > 0) {
            event.preventDefault();
            this.toggleSubmenu(element);
            return;
        }
        
        // 设置活跃项
        this.setActiveItem(item, element);
        
        // 关闭移动端菜单
        if (this.config.closeOnClick && this.isMobile()) {
            this.collapse();
        }
        
        // 触发事件
        if (this.config.onItemClick) {
            this.config.onItemClick(item, element, event);
        }
        
        this.emit('itemClick', { item, element, event });
        
        // 处理标签页
        if (this.config.type === 'tabs') {
            this.handleTabClick(item, element, event);
        }
    }
    
    /**
     * 设置活跃项
     */
    setActiveItem(item, element) {
        // 移除之前的活跃状态
        this.container.querySelectorAll(`.${this.config.activeClass}`).forEach(el => {
            el.classList.remove(this.config.activeClass);
        });
        
        // 设置新的活跃状态
        element.classList.add(this.config.activeClass);
        this.activeItem = item;
        
        // 展开父级菜单
        let parent = element.parentElement?.closest('.nav-item-parent');
        while (parent) {
            parent.classList.add('nav-item-expanded');
            parent = parent.parentElement?.closest('.nav-item-parent');
        }
        
        if (this.config.onItemSelect) {
            this.config.onItemSelect(item, element);
        }
        
        this.emit('itemSelect', { item, element });
    }
    
    /**
     * 切换导航状态
     */
    toggle() {
        if (this.isCollapsed) {
            this.expand();
        } else {
            this.collapse();
        }
    }
    
    /**
     * 展开导航
     */
    expand() {
        this.container.classList.remove('navigation-collapsed');
        this.isCollapsed = false;
        
        if (this.config.type === 'sidebar') {
            this.container.style.width = this.config.expandedWidth;
        }
        
        if (this.elements.toggle) {
            this.elements.toggle.setAttribute('aria-expanded', 'true');
        }
        
        this.emit('expand');
    }
    
    /**
     * 折叠导航
     */
    collapse() {
        this.container.classList.add('navigation-collapsed');
        this.isCollapsed = true;
        
        if (this.config.type === 'sidebar') {
            this.container.style.width = this.config.collapsedWidth;
        }
        
        if (this.elements.toggle) {
            this.elements.toggle.setAttribute('aria-expanded', 'false');
        }
        
        // 关闭所有下拉菜单
        this.closeAllDropdowns();
        
        this.emit('collapse');
    }
    
    /**
     * 切换子菜单
     */
    toggleSubmenu(element) {
        const isExpanded = element.classList.contains('nav-item-expanded');
        
        if (isExpanded) {
            this.hideSubmenu(element);
        } else {
            this.showSubmenu(element);
        }
    }
    
    /**
     * 显示子菜单
     */
    showSubmenu(element) {
        element.classList.add('nav-item-expanded');
        
        const submenu = element.querySelector('.nav-submenu');
        if (submenu) {
            submenu.style.display = 'block';
        }
        
        this.openDropdowns.add(element);
    }
    
    /**
     * 隐藏子菜单
     */
    hideSubmenu(element) {
        element.classList.remove('nav-item-expanded');
        
        const submenu = element.querySelector('.nav-submenu');
        if (submenu) {
            submenu.style.display = 'none';
        }
        
        this.openDropdowns.delete(element);
    }
    
    /**
     * 关闭所有下拉菜单
     */
    closeAllDropdowns() {
        this.openDropdowns.forEach(element => {
            this.hideSubmenu(element);
        });
        this.openDropdowns.clear();
    }
    
    /**
     * 检查是否为移动设备
     */
    isMobile() {
        return window.innerWidth < 768;
    }
    
    /**
     * 处理全局点击
     */
    handleGlobalClick(event) {
        // 点击外部时关闭下拉菜单
        if (!this.container.contains(event.target)) {
            this.closeAllDropdowns();
            
            // 移动端点击外部关闭导航
            if (this.isMobile() && !this.isCollapsed) {
                this.collapse();
            }
        }
    }
    
    /**
     * 处理键盘事件
     */
    handleKeydown(event) {
        switch (event.key) {
            case 'Escape':
                this.closeAllDropdowns();
                if (this.isMobile() && !this.isCollapsed) {
                    this.collapse();
                }
                break;
                
            case 'ArrowDown':
            case 'ArrowUp':
                this.handleArrowNavigation(event);
                break;
        }
    }
    
    /**
     * 处理箭头键导航
     */
    handleArrowNavigation(event) {
        const focusableItems = this.container.querySelectorAll('.nav-link:not(.nav-item-disabled .nav-link)');
        const currentIndex = Array.from(focusableItems).indexOf(document.activeElement);
        
        if (currentIndex === -1) return;
        
        event.preventDefault();
        
        let nextIndex;
        if (event.key === 'ArrowDown') {
            nextIndex = currentIndex < focusableItems.length - 1 ? currentIndex + 1 : 0;
        } else {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : focusableItems.length - 1;
        }
        
        focusableItems[nextIndex].focus();
    }
    
    /**
     * 更新标签滚动状态
     */
    updateTabsScroll() {
        if (this.config.type !== 'tabs') return;
        
        const container = this.elements.navContainer;
        const nav = this.elements.nav;
        
        if (nav.scrollWidth > container.clientWidth) {
            this.elements.scrollLeft.style.display = 'block';
            this.elements.scrollRight.style.display = 'block';
            container.classList.add('scrollable');
        } else {
            this.elements.scrollLeft.style.display = 'none';
            this.elements.scrollRight.style.display = 'none';
            container.classList.remove('scrollable');
        }
    }
    
    /**
     * 滚动标签页
     */
    scrollTabs(direction) {
        const container = this.elements.navContainer;
        const scrollAmount = 200;
        
        if (direction === 'left') {
            container.scrollLeft -= scrollAmount;
        } else {
            container.scrollLeft += scrollAmount;
        }
    }
    
    /**
     * 响应式处理
     */
    initResponsive() {
        this.updateResponsive();
    }
    
    /**
     * 更新响应式状态
     */
    updateResponsive() {
        const isMobile = this.isMobile();
        
        if (isMobile) {
            this.container.classList.add('navigation-mobile');
            if (this.config.type === 'navbar' || this.config.type === 'sidebar') {
                this.collapse();
            }
        } else {
            this.container.classList.remove('navigation-mobile');
            if (this.config.type === 'navbar' || this.config.type === 'sidebar') {
                this.expand();
            }
        }
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        this.updateResponsive();
        
        if (this.config.type === 'tabs') {
            this.updateTabsScroll();
        }
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 移除事件监听器
        document.removeEventListener('click', this.boundHandlers.click);
        window.removeEventListener('resize', this.boundHandlers.resize);
        
        // 清理数据
        this.openDropdowns.clear();
        this.tabs.clear();
        
        super.destroy();
    }
}

// 注册组件
if (typeof JSComponentManager !== 'undefined') {
    JSComponentManager.register('navigation', Navigation);
}

// 导出组件（如果在模块环境中）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Navigation;
}