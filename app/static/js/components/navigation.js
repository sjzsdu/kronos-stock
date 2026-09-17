/**
 * 导航组件
 * 支持动态菜单、面包屑、标签页、侧边栏等导航功能
 */

class Navigation extends BaseComponent {
    constructor(container, options = {}) {
        super(container, options);
        
        this.name = 'Navigation';
        this.version = '1.0.0';
        
        // 默认配置
        this.defaultOptions = {
            type: 'navbar', // navbar, sidebar, tabs, breadcrumb
            theme: 'light', // light, dark
            position: 'top', // top, bottom, left, right, fixed
            collapsible: true, // 是否可折叠
            responsive: true, // 响应式设计
            
            // 导航项配置
            items: [],
            activeItem: null,
            
            // 样式配置
            showBrand: true,
            showSearch: false,
            showProfile: true,
            
            // 行为配置
            autoClose: true, // 移动端自动关闭
            smooth: true, // 平滑滚动
            highlight: true, // 高亮当前项
            
            // 事件回调
            onItemClick: null,
            onToggle: null,
            onChange: null
        };
        
        this.config = { ...this.defaultOptions, ...options };
        
        // 状态管理
        this.isCollapsed = false;
        this.isMobile = false;
        this.activeItemId = this.config.activeItem;
        this.history = [];
        
        // 导航数据
        this.navigationItems = this.processNavigationItems(this.config.items);
        
        // 事件绑定
        this.boundHandlers = {
            resize: this.handleResize.bind(this),
            scroll: this.handleScroll.bind(this),
            hashchange: this.handleHashChange.bind(this),
            click: this.handleDocumentClick.bind(this)
        };
    }
    
    /**
     * 初始化组件
     */
    async init() {
        try {
            this.detectMobile();
            this.createNavigation();
            this.setupEventListeners();
            this.updateActiveItem();
            
            this.setState('ready');
            this.emit('initialized', { component: this });
            
            return this;
        } catch (error) {
            this.handleError(error, '初始化导航组件失败');
            throw error;
        }
    }
    
    /**
     * 检测移动设备
     */
    detectMobile() {
        this.isMobile = window.innerWidth < 768;
        if (this.isMobile && this.config.collapsible) {
            this.isCollapsed = true;
        }
    }
    
    /**
     * 处理导航项数据
     */
    processNavigationItems(items) {
        return items.map(item => ({
            id: item.id || this.generateId(),
            text: item.text || item.label,
            href: item.href || '#',
            icon: item.icon,
            badge: item.badge,
            children: item.children ? this.processNavigationItems(item.children) : null,
            active: item.active || false,
            disabled: item.disabled || false,
            target: item.target || '_self',
            className: item.className || '',
            data: item.data || {}
        }));
    }
    
    /**
     * 创建导航
     */
    createNavigation() {
        this.container.className = `navigation navigation-${this.config.type} navigation-${this.config.theme} navigation-${this.config.position}`;
        
        if (this.isCollapsed) {
            this.container.classList.add('collapsed');
        }
        
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
        }
    }
    
    /**
     * 创建导航栏
     */
    createNavbar() {
        this.container.innerHTML = `
            <nav class="navbar">
                ${this.config.showBrand ? `
                    <div class="navbar-brand">
                        <a href="/" class="brand-link">
                            <i class="fas fa-chart-line brand-icon"></i>
                            <span class="brand-text">Kronos Stock</span>
                        </a>
                    </div>
                ` : ''}
                
                ${this.config.collapsible ? `
                    <button class="navbar-toggle" aria-label="切换导航">
                        <span class="toggle-icon">
                            <span></span>
                            <span></span>
                            <span></span>
                        </span>
                    </button>
                ` : ''}
                
                <div class="navbar-content">
                    <ul class="navbar-nav">
                        ${this.renderNavItems(this.navigationItems)}
                    </ul>
                    
                    ${this.config.showSearch ? `
                        <div class="navbar-search">
                            <input type="text" class="search-input" placeholder="搜索...">
                            <button class="search-btn">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                    ` : ''}
                    
                    ${this.config.showProfile ? `
                        <div class="navbar-profile">
                            <div class="profile-dropdown">
                                <button class="profile-btn">
                                    <img src="/static/images/avatar.png" alt="用户头像" class="profile-avatar">
                                    <span class="profile-name">用户</span>
                                    <i class="fas fa-chevron-down profile-arrow"></i>
                                </button>
                                <div class="profile-menu">
                                    <a href="/profile" class="profile-item">
                                        <i class="fas fa-user"></i>
                                        <span>个人资料</span>
                                    </a>
                                    <a href="/settings" class="profile-item">
                                        <i class="fas fa-cog"></i>
                                        <span>设置</span>
                                    </a>
                                    <div class="profile-divider"></div>
                                    <a href="/logout" class="profile-item">
                                        <i class="fas fa-sign-out-alt"></i>
                                        <span>退出</span>
                                    </a>
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </nav>
        `;
        
        this.elements = {
            navbar: this.container.querySelector('.navbar'),
            toggle: this.container.querySelector('.navbar-toggle'),
            content: this.container.querySelector('.navbar-content'),
            nav: this.container.querySelector('.navbar-nav'),
            search: this.container.querySelector('.navbar-search'),
            profile: this.container.querySelector('.navbar-profile')
        };
    }
    
    /**
     * 创建侧边栏
     */
    createSidebar() {
        this.container.innerHTML = `
            <aside class="sidebar">
                ${this.config.showBrand ? `
                    <div class="sidebar-header">
                        <a href="/" class="sidebar-brand">
                            <i class="fas fa-chart-line brand-icon"></i>
                            <span class="brand-text">Kronos Stock</span>
                        </a>
                        ${this.config.collapsible ? `
                            <button class="sidebar-toggle" aria-label="折叠侧边栏">
                                <i class="fas fa-bars"></i>
                            </button>
                        ` : ''}
                    </div>
                ` : ''}
                
                <nav class="sidebar-nav">
                    <ul class="nav-menu">
                        ${this.renderSidebarItems(this.navigationItems)}
                    </ul>
                </nav>
                
                <div class="sidebar-footer">
                    <div class="sidebar-user">
                        <img src="/static/images/avatar.png" alt="用户头像" class="user-avatar">
                        <div class="user-info">
                            <span class="user-name">用户名</span>
                            <span class="user-role">管理员</span>
                        </div>
                    </div>
                </div>
            </aside>
        `;
        
        this.elements = {
            sidebar: this.container.querySelector('.sidebar'),
            header: this.container.querySelector('.sidebar-header'),
            toggle: this.container.querySelector('.sidebar-toggle'),
            nav: this.container.querySelector('.sidebar-nav'),
            menu: this.container.querySelector('.nav-menu'),
            footer: this.container.querySelector('.sidebar-footer')
        };
    }
    
    /**
     * 创建标签页
     */
    createTabs() {
        this.container.innerHTML = `
            <div class="tabs">
                <div class="tab-header">
                    <ul class="tab-nav" role="tablist">
                        ${this.renderTabItems(this.navigationItems)}
                    </ul>
                    <div class="tab-actions">
                        <button class="tab-action-btn" data-action="scroll-left" title="向左滚动">
                            <i class="fas fa-chevron-left"></i>
                        </button>
                        <button class="tab-action-btn" data-action="scroll-right" title="向右滚动">
                            <i class="fas fa-chevron-right"></i>
                        </button>
                    </div>
                </div>
                <div class="tab-content">
                    ${this.renderTabPanels(this.navigationItems)}
                </div>
            </div>
        `;
        
        this.elements = {
            tabs: this.container.querySelector('.tabs'),
            header: this.container.querySelector('.tab-header'),
            nav: this.container.querySelector('.tab-nav'),
            content: this.container.querySelector('.tab-content'),
            actions: this.container.querySelector('.tab-actions')
        };
    }
    
    /**
     * 创建面包屑
     */
    createBreadcrumb() {
        this.container.innerHTML = `
            <nav class="breadcrumb" aria-label="面包屑导航">
                <ol class="breadcrumb-list">
                    ${this.renderBreadcrumbItems(this.navigationItems)}
                </ol>
            </nav>
        `;
        
        this.elements = {
            breadcrumb: this.container.querySelector('.breadcrumb'),
            list: this.container.querySelector('.breadcrumb-list')
        };
    }
    
    /**
     * 渲染导航项
     */
    renderNavItems(items) {
        return items.map(item => `
            <li class="nav-item ${item.children ? 'has-dropdown' : ''} ${item.active ? 'active' : ''} ${item.disabled ? 'disabled' : ''}">
                <a href="${item.href}" 
                   class="nav-link ${item.className}" 
                   data-id="${item.id}"
                   target="${item.target}"
                   ${item.disabled ? 'aria-disabled="true"' : ''}>
                    ${item.icon ? `<i class="${item.icon}"></i>` : ''}
                    <span class="nav-text">${item.text}</span>
                    ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
                    ${item.children ? '<i class="fas fa-chevron-down dropdown-arrow"></i>' : ''}
                </a>
                ${item.children ? `
                    <ul class="nav-dropdown">
                        ${this.renderNavItems(item.children)}
                    </ul>
                ` : ''}
            </li>
        `).join('');
    }
    
    /**
     * 渲染侧边栏项
     */
    renderSidebarItems(items, level = 0) {
        return items.map(item => `
            <li class="nav-item ${item.children ? 'has-submenu' : ''} ${item.active ? 'active' : ''} ${item.disabled ? 'disabled' : ''}" 
                data-level="${level}">
                <a href="${item.href}" 
                   class="nav-link ${item.className}" 
                   data-id="${item.id}"
                   target="${item.target}"
                   ${item.disabled ? 'aria-disabled="true"' : ''}>
                    ${item.icon ? `<i class="${item.icon} nav-icon"></i>` : ''}
                    <span class="nav-text">${item.text}</span>
                    ${item.badge ? `<span class="nav-badge">${item.badge}</span>` : ''}
                    ${item.children ? '<i class="fas fa-chevron-right submenu-arrow"></i>' : ''}
                </a>
                ${item.children ? `
                    <ul class="nav-submenu">
                        ${this.renderSidebarItems(item.children, level + 1)}
                    </ul>
                ` : ''}
            </li>
        `).join('');
    }
    
    /**
     * 渲染标签项
     */
    renderTabItems(items) {
        return items.map((item, index) => `
            <li class="tab-item ${item.active ? 'active' : ''}" role="presentation">
                <button class="tab-link" 
                        role="tab" 
                        data-id="${item.id}"
                        data-target="#tab-panel-${item.id}"
                        aria-controls="tab-panel-${item.id}"
                        aria-selected="${item.active ? 'true' : 'false'}"
                        tabindex="${item.active ? '0' : '-1'}">
                    ${item.icon ? `<i class="${item.icon}"></i>` : ''}
                    <span class="tab-text">${item.text}</span>
                    ${item.badge ? `<span class="tab-badge">${item.badge}</span>` : ''}
                    <button class="tab-close" aria-label="关闭标签页">
                        <i class="fas fa-times"></i>
                    </button>
                </button>
            </li>
        `).join('');
    }
    
    /**
     * 渲染标签面板
     */
    renderTabPanels(items) {
        return items.map(item => `
            <div class="tab-panel ${item.active ? 'active' : ''}" 
                 id="tab-panel-${item.id}"
                 role="tabpanel"
                 aria-labelledby="tab-${item.id}">
                ${item.content || `<p>标签页 ${item.text} 的内容</p>`}
            </div>
        `).join('');
    }
    
    /**
     * 渲染面包屑项
     */
    renderBreadcrumbItems(items) {
        return items.map((item, index) => `
            <li class="breadcrumb-item ${index === items.length - 1 ? 'active' : ''}">
                ${index === items.length - 1 ? `
                    <span class="breadcrumb-text" aria-current="page">${item.text}</span>
                ` : `
                    <a href="${item.href}" class="breadcrumb-link" data-id="${item.id}">
                        ${item.icon ? `<i class="${item.icon}"></i>` : ''}
                        <span class="breadcrumb-text">${item.text}</span>
                    </a>
                `}
            </li>
        `).join('');
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
        
        // 导航项点击
        this.container.addEventListener('click', (e) => {
            this.handleNavClick(e);
        });
        
        // 下拉菜单处理
        this.container.addEventListener('mouseenter', (e) => {
            if (e.target.closest('.has-dropdown')) {
                this.showDropdown(e.target.closest('.has-dropdown'));
            }
        });
        
        this.container.addEventListener('mouseleave', (e) => {
            if (e.target.closest('.has-dropdown')) {
                this.hideDropdown(e.target.closest('.has-dropdown'));
            }
        });
        
        // 全局事件
        window.addEventListener('resize', this.boundHandlers.resize);
        window.addEventListener('scroll', this.boundHandlers.scroll);
        window.addEventListener('hashchange', this.boundHandlers.hashchange);
        document.addEventListener('click', this.boundHandlers.click);
    }
    
    /**
     * 处理导航点击
     */
    handleNavClick(event) {
        const navLink = event.target.closest('.nav-link, .tab-link, .breadcrumb-link');
        if (!navLink) return;
        
        event.preventDefault();
        
        const itemId = navLink.dataset.id;
        const item = this.findItemById(itemId);
        
        if (!item || item.disabled) return;
        
        // 处理不同类型的导航
        switch (this.config.type) {
            case 'tabs':
                this.switchTab(itemId);
                break;
            default:
                this.setActiveItem(itemId);
                if (item.href && item.href !== '#') {
                    if (item.target === '_blank') {
                        window.open(item.href);
                    } else {
                        window.location.href = item.href;
                    }
                }
        }
        
        // 移动端自动关闭
        if (this.isMobile && this.config.autoClose && this.isCollapsed === false) {
            this.collapse();
        }
        
        // 触发事件
        if (this.config.onItemClick) {
            this.config.onItemClick(item, event);
        }
        
        this.emit('itemClick', { item, event });
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
        this.isCollapsed = false;
        this.container.classList.remove('collapsed');
        
        if (this.config.onToggle) {
            this.config.onToggle(false);
        }
        
        this.emit('expand');
    }
    
    /**
     * 折叠导航
     */
    collapse() {
        this.isCollapsed = true;
        this.container.classList.add('collapsed');
        
        if (this.config.onToggle) {
            this.config.onToggle(true);
        }
        
        this.emit('collapse');
    }
    
    /**
     * 设置活跃项
     */
    setActiveItem(itemId) {
        // 移除旧的活跃状态
        if (this.activeItemId) {
            const oldItem = this.container.querySelector(`[data-id="${this.activeItemId}"]`);
            if (oldItem) {
                oldItem.closest('.nav-item, .tab-item, .breadcrumb-item')
                    ?.classList.remove('active');
            }
        }
        
        // 设置新的活跃状态
        this.activeItemId = itemId;
        const newItem = this.container.querySelector(`[data-id="${itemId}"]`);
        if (newItem) {
            newItem.closest('.nav-item, .tab-item, .breadcrumb-item')
                ?.classList.add('active');
        }
        
        // 更新数据
        this.updateItemActiveState(itemId);
        
        if (this.config.onChange) {
            this.config.onChange(itemId, this.findItemById(itemId));
        }
        
        this.emit('activeItemChanged', { itemId, item: this.findItemById(itemId) });
    }
    
    /**
     * 切换标签页
     */
    switchTab(tabId) {
        // 隐藏所有标签页
        this.container.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.remove('active');
        });
        
        // 显示目标标签页
        const targetPanel = this.container.querySelector(`#tab-panel-${tabId}`);
        if (targetPanel) {
            targetPanel.classList.add('active');
        }
        
        // 更新标签状态
        this.setActiveItem(tabId);
    }
    
    /**
     * 添加导航项
     */
    addItem(item, parentId = null) {
        const processedItem = this.processNavigationItems([item])[0];
        
        if (parentId) {
            const parent = this.findItemById(parentId);
            if (parent) {
                if (!parent.children) parent.children = [];
                parent.children.push(processedItem);
            }
        } else {
            this.navigationItems.push(processedItem);
        }
        
        this.refresh();
        this.emit('itemAdded', { item: processedItem, parentId });
    }
    
    /**
     * 移除导航项
     */
    removeItem(itemId) {
        const item = this.findItemById(itemId);
        if (!item) return;
        
        this.removeItemFromArray(this.navigationItems, itemId);
        this.refresh();
        this.emit('itemRemoved', { itemId, item });
    }
    
    /**
     * 更新导航项
     */
    updateItem(itemId, updates) {
        const item = this.findItemById(itemId);
        if (!item) return;
        
        Object.assign(item, updates);
        this.refresh();
        this.emit('itemUpdated', { itemId, item, updates });
    }
    
    /**
     * 查找导航项
     */
    findItemById(itemId, items = null) {
        items = items || this.navigationItems;
        
        for (const item of items) {
            if (item.id === itemId) {
                return item;
            }
            if (item.children) {
                const found = this.findItemById(itemId, item.children);
                if (found) return found;
            }
        }
        
        return null;
    }
    
    /**
     * 从数组中移除项目
     */
    removeItemFromArray(items, itemId) {
        for (let i = 0; i < items.length; i++) {
            if (items[i].id === itemId) {
                items.splice(i, 1);
                return true;
            }
            if (items[i].children) {
                if (this.removeItemFromArray(items[i].children, itemId)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    /**
     * 更新项目活跃状态
     */
    updateItemActiveState(activeId, items = null) {
        items = items || this.navigationItems;
        
        for (const item of items) {
            item.active = item.id === activeId;
            if (item.children) {
                this.updateItemActiveState(activeId, item.children);
            }
        }
    }
    
    /**
     * 显示下拉菜单
     */
    showDropdown(navItem) {
        const dropdown = navItem.querySelector('.nav-dropdown');
        if (dropdown) {
            dropdown.classList.add('show');
        }
    }
    
    /**
     * 隐藏下拉菜单
     */
    hideDropdown(navItem) {
        const dropdown = navItem.querySelector('.nav-dropdown');
        if (dropdown) {
            dropdown.classList.remove('show');
        }
    }
    
    /**
     * 更新活跃项
     */
    updateActiveItem() {
        // 基于当前URL更新活跃项
        const currentPath = window.location.pathname + window.location.hash;
        const matchingItem = this.findItemByHref(currentPath);
        
        if (matchingItem) {
            this.setActiveItem(matchingItem.id);
        }
    }
    
    /**
     * 根据链接查找项目
     */
    findItemByHref(href, items = null) {
        items = items || this.navigationItems;
        
        for (const item of items) {
            if (item.href === href) {
                return item;
            }
            if (item.children) {
                const found = this.findItemByHref(href, item.children);
                if (found) return found;
            }
        }
        
        return null;
    }
    
    /**
     * 刷新导航
     */
    refresh() {
        this.createNavigation();
        this.setupEventListeners();
        this.updateActiveItem();
    }
    
    /**
     * 处理窗口大小变化
     */
    handleResize() {
        const wasMobile = this.isMobile;
        this.detectMobile();
        
        if (wasMobile !== this.isMobile) {
            if (this.config.responsive) {
                this.refresh();
            }
        }
    }
    
    /**
     * 处理滚动事件
     */
    handleScroll() {
        // 可以在这里实现滚动时的特殊行为，如固定导航栏
        if (this.config.position === 'fixed') {
            const scrolled = window.scrollY > 50;
            this.container.classList.toggle('scrolled', scrolled);
        }
    }
    
    /**
     * 处理Hash变化
     */
    handleHashChange() {
        this.updateActiveItem();
    }
    
    /**
     * 处理文档点击（关闭下拉菜单）
     */
    handleDocumentClick(event) {
        if (!this.container.contains(event.target)) {
            // 关闭所有下拉菜单
            this.container.querySelectorAll('.nav-dropdown.show').forEach(dropdown => {
                dropdown.classList.remove('show');
            });
        }
    }
    
    /**
     * 销毁组件
     */
    destroy() {
        // 移除事件监听器
        window.removeEventListener('resize', this.boundHandlers.resize);
        window.removeEventListener('scroll', this.boundHandlers.scroll);
        window.removeEventListener('hashchange', this.boundHandlers.hashchange);
        document.removeEventListener('click', this.boundHandlers.click);
        
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