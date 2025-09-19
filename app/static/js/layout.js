// Layout and interaction management
class LayoutManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.mainContent = document.querySelector('.app-main');
        this.isMobile = window.innerWidth <= 768;
        this.sidebarCollapsed = this.isMobile;
        this.sidebarLabelSelector = '.sidebar-label';
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupMobileLayout();
        this.initializeComponents();
    }
    
    setupEventListeners() {
        // Sidebar toggle
        document.addEventListener('click', (e) => {
            if (e.target.closest('.sidebar-toggle')) {
                this.toggleSidebar();
            }
        });
        
        // Window resize handler
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        // User menu dropdown
        const userMenu = document.querySelector('.user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleUserDropdown();
            });
        }
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', () => {
            this.closeAllDropdowns();
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }
    
    toggleSidebar() {
        this.sidebarCollapsed = !this.sidebarCollapsed;
        this.applySidebarState();
    }

    updateSidebarToggleUI() {
        const btn = document.getElementById('sidebarToggle');
        if (!btn) return;
        btn.setAttribute('aria-expanded', String(!this.sidebarCollapsed));
        // Tooltip aria-label sync
        btn.setAttribute('aria-label', this.sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏');
    }
    
    setupMobileLayout() {
        this.isMobile = window.innerWidth <= 768;
        if (this.isMobile) {
            this.sidebarCollapsed = true;
        } else {
            const savedState = localStorage.getItem('sidebarCollapsed');
            if (savedState !== null) this.sidebarCollapsed = savedState === 'true';
        }
        this.applySidebarState(true);
    }

    applySidebarState(skipSave=false) {
        if (!this.sidebar) return;
        // Width control
        if (this.sidebarCollapsed) {
            this.sidebar.classList.remove('w-64');
            this.sidebar.classList.add('w-16');
        } else {
            this.sidebar.classList.remove('w-16');
            this.sidebar.classList.add('w-64');
        }
        // Labels show/hide
        const labels = this.sidebar.querySelectorAll(this.sidebarLabelSelector);
        labels.forEach(l => {
            if (this.sidebarCollapsed) {
                l.classList.add('hidden');
            } else {
                l.classList.remove('hidden');
            }
        });
        // Section title spacing adjust (optional, using utility classes)
        const sectionTitles = this.sidebar.querySelectorAll('.sidebar-section-title');
        sectionTitles.forEach(t => {
            if (this.sidebarCollapsed) {
                t.classList.add('justify-center');
            } else {
                t.classList.remove('justify-center');
            }
        });
        // Menu items center alignment when collapsed
        const menuItems = this.sidebar.querySelectorAll('.sidebar-menu-item');
        menuItems.forEach(mi => {
            if (this.sidebarCollapsed) {
                mi.classList.add('justify-center');
                mi.classList.add('px-0');
            } else {
                mi.classList.remove('justify-center');
                mi.classList.remove('px-0');
            }
        });
        // Toggle wrapper shift outward
        const toggleWrapper = this.sidebar.querySelector('.sidebar-toggle-wrapper');
        if (toggleWrapper) {
            // Keep slight outward shift when collapsed
            if (this.sidebarCollapsed) {
                toggleWrapper.classList.remove('-right-3');
                toggleWrapper.classList.add('-right-4');
            } else {
                toggleWrapper.classList.remove('-right-4');
                toggleWrapper.classList.add('-right-3');
            }
        }
        this.updateSidebarToggleUI();
        if (!skipSave) localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
        // Dispatch resize after transition
        setTimeout(() => window.dispatchEvent(new Event('resize')), 300);
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            this.setupMobileLayout();
        }
    }
    
    toggleUserDropdown() {
        const dropdown = document.getElementById('userDropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    }
    
    toggleNotifications() {
        const dropdown = document.getElementById('notificationDropdown');
        if (dropdown) {
            dropdown.classList.toggle('hidden');
        }
    }
    
    toggleMobileMenu() {
        const mobileMenu = document.querySelector('.mobile-nav');
        if (mobileMenu) {
            mobileMenu.classList.toggle('hidden');
        }
    }
    
    closeAllDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown.active');
        dropdowns.forEach(dropdown => {
            dropdown.classList.remove('active');
        });
    }
    
    handleKeyboardShortcuts(e) {
        // Sidebar toggle: Ctrl/Cmd + B
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            this.toggleSidebar();
        }
        
        // Search: Ctrl/Cmd + K
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.focusSearch();
        }
        
        // Escape: Close all dropdowns
        if (e.key === 'Escape') {
            this.closeAllDropdowns();
        }
    }
    
    focusSearch() {
        const searchInput = document.querySelector('.search-input');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    initializeComponents() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize loading states
        this.initLoadingStates();
        
        // Initialize notifications
        this.initNotifications();
    }
    
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target);
            });
            
            element.addEventListener('mouseleave', (e) => {
                this.hideTooltip(e.target);
            });
        });
    }
    
    showTooltip(element) {
        const text = element.getAttribute('data-tooltip');
        if (!text) return;
        
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
        
        element._tooltip = tooltip;
    }
    
    hideTooltip(element) {
        if (element._tooltip) {
            element._tooltip.remove();
            delete element._tooltip;
        }
    }
    
    initLoadingStates() {
        // Handle HTMX loading states
        document.addEventListener('htmx:beforeRequest', (e) => {
            this.showLoading(e.target);
        });
        
        document.addEventListener('htmx:afterRequest', (e) => {
            this.hideLoading(e.target);
        });
    }
    
    showLoading(element) {
        element.classList.add('loading');
        
        // Add spinner if needed
        if (element.classList.contains('btn')) {
            const spinner = document.createElement('i');
            spinner.className = 'fas fa-spinner fa-spin loading-spinner';
            element.prepend(spinner);
        }
    }
    
    hideLoading(element) {
        element.classList.remove('loading');
        
        // Remove spinner
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
    
    initNotifications() {
        // Check for new notifications periodically
        setInterval(() => {
            this.checkNotifications();
        }, 30000); // Check every 30 seconds
    }
    
    checkNotifications() {
        console.log('Checking notifications...');
        // Check for new notifications
        fetch('/api/notifications/check')
            .then(response => {
                console.log('Notification check response status:', response.status);
                return response.json();
            })
            .then(data => {
                console.log('Notification check data:', data);
                if (data.success) {
                    this.updateNotificationIcon(data.data.unread_count);
                    
                    // Show new notifications if any
                    if (data.data.unread_count > 0) {
                        const highPriorityNotifications = data.data.notifications.filter(
                            n => !n.read && n.priority === 'high'
                        );
                        
                        // Show toast for high priority notifications
                        highPriorityNotifications.forEach(notification => {
                            this.showNotification(notification.message, 'warning', 8000);
                        });
                    }
                } else {
                    console.error('Notification check failed:', data.error);
                }
            })
            .catch(error => {
                console.warn('Failed to check notifications:', error);
            });
    }
    
    updateNotificationIcon(unreadCount) {
        const notificationIcon = document.querySelector('.notification-icon');
        const notificationBadge = document.querySelector('.notification-badge');
        
        if (notificationIcon && notificationBadge) {
            if (unreadCount > 0) {
                notificationBadge.style.display = 'flex';
                notificationBadge.textContent = unreadCount > 99 ? '99+' : unreadCount;
                notificationIcon.classList.add('has-notifications');
            } else {
                notificationBadge.style.display = 'none';
                notificationIcon.classList.remove('has-notifications');
            }
        }
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-message">${message}</span>
                <button class="notification-close" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        // Add to container
        let container = document.querySelector('.notifications-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'notifications-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, duration);
        }
        
        return notification;
    }
}

// Stock data management
class StockManager {
    constructor() {
        this.watchlist = this.loadWatchlist();
        this.predictions = [];
        this.realTimeData = new Map();
        
        this.init();
    }
    
    init() {
        this.setupRealTimeUpdates();
        this.setupWatchlistHandlers();
    }
    
    setupRealTimeUpdates() {
        // Simulate real-time price updates
        setInterval(() => {
            this.updatePrices();
        }, 5000);
    }
    
    updatePrices() {
        const watchedStocks = this.watchlist;
        
        watchedStocks.forEach(stock => {
            // Simulate price changes
            const change = (Math.random() - 0.5) * 0.1; // ±5% max change
            const currentPrice = this.realTimeData.get(stock.symbol) || stock.price;
            const newPrice = currentPrice * (1 + change);
            
            this.realTimeData.set(stock.symbol, newPrice);
            
            // Update UI elements
            this.updateStockPriceInUI(stock.symbol, newPrice, change);
        });
    }
    
    updateStockPriceInUI(symbol, price, change) {
        const elements = document.querySelectorAll(`[data-stock="${symbol}"]`);
        elements.forEach(element => {
            const priceElement = element.querySelector('.stock-price');
            const changeElement = element.querySelector('.stock-change');
            
            if (priceElement) {
                priceElement.textContent = price.toFixed(2);
                priceElement.className = `stock-price ${change >= 0 ? 'text-success' : 'text-danger'}`;
            }
            
            if (changeElement) {
                const changePercent = (change * 100).toFixed(2);
                changeElement.textContent = `${change >= 0 ? '+' : ''}${changePercent}%`;
                changeElement.className = `stock-change ${change >= 0 ? 'text-success' : 'text-danger'}`;
            }
        });
    }
    
    setupWatchlistHandlers() {
        document.addEventListener('click', (e) => {
            if (e.target.closest('.add-to-watchlist')) {
                const symbol = e.target.closest('[data-stock]')?.getAttribute('data-stock');
                if (symbol) {
                    this.addToWatchlist(symbol);
                }
            }
            
            if (e.target.closest('.remove-from-watchlist')) {
                const symbol = e.target.closest('[data-stock]')?.getAttribute('data-stock');
                if (symbol) {
                    this.removeFromWatchlist(symbol);
                }
            }
        });
    }
    
    addToWatchlist(symbol) {
        if (!this.watchlist.find(stock => stock.symbol === symbol)) {
            // This would typically fetch stock data from API
            const stock = {
                symbol: symbol,
                name: symbol, // Would be fetched from API
                price: 100 + Math.random() * 200 // Simulated price
            };
            
            this.watchlist.push(stock);
            this.saveWatchlist();
            
            layoutManager.showNotification(`${symbol} 已添加到关注列表`, 'success');
        }
    }
    
    removeFromWatchlist(symbol) {
        this.watchlist = this.watchlist.filter(stock => stock.symbol !== symbol);
        this.saveWatchlist();
        
        layoutManager.showNotification(`${symbol} 已从关注列表移除`, 'info');
    }
    
    loadWatchlist() {
        const saved = localStorage.getItem('stockWatchlist');
        return saved ? JSON.parse(saved) : [
            { symbol: '000001', name: '平安银行', price: 12.50 },
            { symbol: '000002', name: '万科A', price: 18.75 },
            { symbol: '600519', name: '贵州茅台', price: 1680.00 }
        ];
    }
    
    saveWatchlist() {
        localStorage.setItem('stockWatchlist', JSON.stringify(this.watchlist));
    }
}

// Chart management
class ChartManager {
    constructor() {
        this.charts = new Map();
        this.defaultConfig = {
            responsive: true,
            displayModeBar: false,
            layout: {
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { family: 'Inter, sans-serif' }
            }
        };
    }
    
    createChart(containerId, data, layout = {}, config = {}) {
        const mergedLayout = { ...this.defaultConfig.layout, ...layout };
        const mergedConfig = { ...this.defaultConfig, ...config };
        
        const chart = Plotly.newPlot(containerId, data, mergedLayout, mergedConfig);
        this.charts.set(containerId, chart);
        
        return chart;
    }
    
    updateChart(containerId, update) {
        if (this.charts.has(containerId)) {
            Plotly.redraw(containerId);
        }
    }
    
    resizeCharts() {
        this.charts.forEach((chart, containerId) => {
            Plotly.Plots.resize(containerId);
        });
    }
}

// HTMX enhancements
class HTMXEnhancements {
    constructor() {
        this.init();
    }
    
    init() {
        // Add loading indicators
        document.addEventListener('htmx:beforeRequest', (e) => {
            this.addLoadingState(e.target);
        });
        
        document.addEventListener('htmx:afterRequest', (e) => {
            this.removeLoadingState(e.target);
        });
        
        // Handle errors
        document.addEventListener('htmx:responseError', (e) => {
            this.handleError(e);
        });
        
        // Auto-refresh elements
        this.setupAutoRefresh();
    }
    
    addLoadingState(element) {
        element.classList.add('htmx-loading');
        
        // Add spinner overlay for forms
        if (element.tagName === 'FORM') {
            const overlay = document.createElement('div');
            overlay.className = 'htmx-overlay';
            overlay.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            element.appendChild(overlay);
        }
    }
    
    removeLoadingState(element) {
        element.classList.remove('htmx-loading');
        
        // Remove spinner overlay
        const overlay = element.querySelector('.htmx-overlay');
        if (overlay) {
            overlay.remove();
        }
    }
    
    handleError(e) {
        console.error('HTMX Error:', e.detail);
        layoutManager.showNotification('请求失败，请稍后重试', 'danger');
    }
    
    setupAutoRefresh() {
        // Auto-refresh market data every 30 seconds
        const marketElements = document.querySelectorAll('[data-auto-refresh]');
        marketElements.forEach(element => {
            const interval = parseInt(element.getAttribute('data-auto-refresh')) || 30000;
            const url = element.getAttribute('hx-get') || element.getAttribute('hx-post');
            
            if (url) {
                setInterval(() => {
                    htmx.ajax('GET', url, { target: element });
                }, interval);
            }
        });
    }
}

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize managers
    window.layoutManager = new LayoutManager();
    window.stockManager = new StockManager();
    window.chartManager = new ChartManager();
    window.htmxEnhancements = new HTMXEnhancements();
    
    // Handle window resize for charts
    window.addEventListener('resize', () => {
        chartManager.resizeCharts();
    });
    
    // Initialize any existing charts
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart');
        // Initialize chart based on type
        // This would be expanded based on specific chart needs
    });
});

// Utility functions
window.utils = {
    formatCurrency: (value, currency = 'CNY') => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency
        }).format(value);
    },
    
    formatPercent: (value) => {
        return new Intl.NumberFormat('zh-CN', {
            style: 'percent',
            minimumFractionDigits: 2
        }).format(value);
    },
    
    formatNumber: (value) => {
        return new Intl.NumberFormat('zh-CN').format(value);
    },
    
    debounce: (func, wait) => {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    throttle: (func, limit) => {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// Toast notification system
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Toast content
    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-icon">
                ${getToastIcon(type)}
            </div>
            <div class="toast-message">${message}</div>
            <button class="toast-close" onclick="closeToast(this.parentElement.parentElement)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Show with animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        closeToast(toast);
    }, duration);
    
    return toast;
}

function closeToast(toast) {
    if (toast && toast.parentElement) {
        toast.classList.remove('show');
        setTimeout(() => {
            if (toast.parentElement) {
                toast.parentElement.removeChild(toast);
            }
        }, 300);
    }
}

function getToastIcon(type) {
    const icons = {
        success: '<i class="fas fa-check-circle"></i>',
        error: '<i class="fas fa-exclamation-circle"></i>',
        warning: '<i class="fas fa-exclamation-triangle"></i>',
        info: '<i class="fas fa-info-circle"></i>'
    };
    return icons[type] || icons.info;
}

// 登出功能
function logout() {
    console.log('用户登出');
    // 实际项目中可以发送登出请求到服务器
    window.location.href = '/';
}

// Initialize layout manager when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    window.layoutManager = new LayoutManager();
    console.log('LayoutManager initialized');
});

(function initSidebarToggle(){
  const sidebar = document.getElementById('sidebar');
  const btn = document.getElementById('sidebarToggle');
  if(!sidebar || !btn) return;
  const STORAGE_KEY = 'sidebar:collapsed';
  const labelSelector = '.sidebar-label';

  function apply(collapsed){
    sidebar.classList.toggle('w-64', !collapsed);
    sidebar.classList.toggle('w-16', collapsed);
    sidebar.querySelectorAll(labelSelector).forEach(el=>el.classList.toggle('hidden', collapsed));
    btn.setAttribute('aria-expanded', (!collapsed).toString());
    btn.setAttribute('aria-label', collapsed ? '展开侧边栏' : '折叠侧边栏');
    btn.querySelector('.icon-expanded').classList.toggle('hidden', collapsed);
    btn.querySelector('.icon-collapsed').classList.toggle('hidden', !collapsed);
  }

  let collapsed = localStorage.getItem(STORAGE_KEY)==='1';
  apply(collapsed);

  btn.addEventListener('click', (e)=>{
    e.stopPropagation();
    collapsed = !collapsed;
    localStorage.setItem(STORAGE_KEY, collapsed ? '1':'0');
    apply(collapsed);
    window.dispatchEvent(new Event('resize'));
  });
})();