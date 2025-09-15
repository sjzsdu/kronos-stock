// Layout and interaction management
class LayoutManager {
    constructor() {
        this.sidebar = document.getElementById('sidebar');
        this.mainContent = document.querySelector('.app-main');
        this.isMobile = window.innerWidth <= 768;
        this.sidebarCollapsed = this.isMobile;
        
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
        
        if (this.sidebar) {
            this.sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
        }
        
        // Save preference
        localStorage.setItem('sidebarCollapsed', this.sidebarCollapsed);
        
        // Trigger resize event for charts
        setTimeout(() => {
            window.dispatchEvent(new Event('resize'));
        }, 300);
    }
    
    setupMobileLayout() {
        this.isMobile = window.innerWidth <= 768;
        
        if (this.isMobile) {
            this.sidebarCollapsed = true;
            if (this.sidebar) {
                this.sidebar.classList.add('collapsed');
            }
        } else {
            // Restore saved preference on desktop
            const savedState = localStorage.getItem('sidebarCollapsed');
            if (savedState !== null) {
                this.sidebarCollapsed = savedState === 'true';
                if (this.sidebar) {
                    this.sidebar.classList.toggle('collapsed', this.sidebarCollapsed);
                }
            }
        }
    }
    
    handleResize() {
        const wasMobile = this.isMobile;
        this.isMobile = window.innerWidth <= 768;
        
        if (wasMobile !== this.isMobile) {
            this.setupMobileLayout();
        }
    }
    
    toggleUserDropdown() {
        const dropdown = document.querySelector('.user-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
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
        // Implementation for checking notifications
        // This would typically make an HTMX request to get new notifications
        htmx.ajax('GET', '/api/notifications/check', {
            target: '.notification-icon',
            swap: 'none'
        });
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