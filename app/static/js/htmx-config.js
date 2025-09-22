/**
 * HTMX Configuration for Kronos Stock Prediction System
 * This file configures global HTMX behavior, event handlers, and UI interactions
 */

// HTMX Global Configuration
document.addEventListener('DOMContentLoaded', function() {
    // Configure HTMX defaults
    htmx.config.globalViewTransitions = true;
    htmx.config.defaultSwapStyle = 'innerHTML';
    htmx.config.defaultSwapDelay = 100;
    htmx.config.defaultSettleDelay = 100;
    
    // Set up global request indicators
    htmx.config.indicatorClass = 'htmx-indicator';
    
    // Configure timeout
    htmx.config.timeout = 30000; // 30 seconds
});

// Global HTMX Event Handlers
document.body.addEventListener('htmx:beforeRequest', function(event) {
    showGlobalLoading();
    
    const xhr = event.detail.xhr;
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    hideGlobalLoading();
    
    const xhr = event.detail.xhr;
    
    if (xhr.status >= 400) {
        handleHTMXError(event);
    }
});

document.body.addEventListener('htmx:responseError', function(event) {
    handleHTMXError(event);
});

document.body.addEventListener('htmx:sendError', function(event) {
    console.error('HTMX Send Error:', event.detail);
    showNotification('网络连接失败，请检查您的网络连接', 'error');
    hideGlobalLoading();
});

document.body.addEventListener('htmx:timeout', function(event) {
    console.error('HTMX Timeout:', event.detail);
    showNotification('请求超时，请稍后重试', 'error');
    hideGlobalLoading();
});

// Handle successful HTMX swaps
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Reinitialize any JavaScript components after content swap
    initializeSwappedContent(event.detail.target);
});

// Handle before content swap
document.body.addEventListener('htmx:beforeSwap', function(event) {
    // You can modify the response before it's swapped in
    const xhr = event.detail.xhr;
    
    // Handle JSON responses that might need special treatment
    if (xhr.getResponseHeader('Content-Type')?.includes('application/json')) {
        try {
            const data = JSON.parse(xhr.responseText);
            if (data.success === false) {
                event.detail.shouldSwap = false; // Prevent swap
                showNotification(data.error || '操作失败', 'error');
                return;
            }
        } catch (e) {
            // Not JSON, continue normally
        }
    }
});

// Global Loading Indicator Functions
function showGlobalLoading() {
    let indicator = document.querySelector('#global-loading-indicator');
    if (!indicator) {
        indicator = document.createElement('div');
        indicator.id = 'global-loading-indicator';
        indicator.className = 'fixed top-4 right-4 bg-primary text-white px-4 py-2 rounded-lg shadow-lg z-50 flex items-center gap-2';
        indicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 加载中...';
        document.body.appendChild(indicator);
    }
    indicator.classList.remove('hidden');
}

function hideGlobalLoading() {
    const indicator = document.querySelector('#global-loading-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
}

// Error Handling
function handleHTMXError(event) {
    const xhr = event.detail.xhr;
    let errorMessage = '请求失败';
    
    try {
        const response = JSON.parse(xhr.responseText);
        errorMessage = response.error || response.message || errorMessage;
    } catch (e) {
        // Not JSON, use status text or default message
        errorMessage = xhr.statusText || errorMessage;
    }
    
    showNotification(errorMessage, 'error');
}

// Notification System
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 left-1/2 transform -translate-x-1/2 px-6 py-3 rounded-lg shadow-lg z-50 transition-all duration-300 max-w-md text-center ${getNotificationClasses(type)}`;
    notification.innerHTML = `
        <div class="flex items-center gap-2">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 opacity-70 hover:opacity-100">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    if (duration > 0) {
        setTimeout(() => {
            if (notification.parentElement) {
                notification.style.opacity = '0';
                notification.style.transform = 'translate(-50%, -100%)';
                setTimeout(() => notification.remove(), 300);
            }
        }, duration);
    }
}

function getNotificationClasses(type) {
    switch (type) {
        case 'success':
            return 'bg-green-500 text-white';
        case 'error':
            return 'bg-red-500 text-white';
        case 'warning':
            return 'bg-yellow-500 text-white';
        default:
            return 'bg-blue-500 text-white';
    }
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success':
            return 'fa-check-circle';
        case 'error':
            return 'fa-exclamation-circle';
        case 'warning':
            return 'fa-exclamation-triangle';
        default:
            return 'fa-info-circle';
    }
}

// Initialize content after HTMX swaps
function initializeSwappedContent(target) {
    // Reinitialize charts if any
    const charts = target.querySelectorAll('[data-chart]');
    charts.forEach(chart => {
        // Reinitialize chart if needed
        if (window.Plotly && chart.dataset.chart) {
            // Chart reinitialization logic here
        }
    });
    
    // Reinitialize form elements
    const forms = target.querySelectorAll('form');
    forms.forEach(form => {
        // Add any form-specific initialization
    });
    
    // Reinitialize tooltips or other UI components
    const tooltips = target.querySelectorAll('[title]');
    tooltips.forEach(element => {
        // Tooltip initialization if you have a tooltip library
    });
}

// Form Submission Helpers
function handleFormSubmit(form, endpoint, options = {}) {
    const formData = new FormData(form);
    
    // Show loading state
    const submitButton = form.querySelector('[type="submit"]');
    const originalText = submitButton.innerHTML;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>提交中...';
    submitButton.disabled = true;
    
    // Use HTMX for form submission
    htmx.ajax('POST', endpoint, {
        values: Object.fromEntries(formData),
        target: options.target || form.parentElement,
        swap: options.swap || 'innerHTML'
    }).finally(() => {
        // Restore button state
        submitButton.innerHTML = originalText;
        submitButton.disabled = false;
    });
}

// Utility function to refresh specific components
function refreshComponent(selector, endpoint) {
    const element = document.querySelector(selector);
    if (element) {
        htmx.ajax('GET', endpoint, {
            target: element,
            swap: 'innerHTML'
        });
    }
}

// Auto-refresh functionality
function setupAutoRefresh(selector, endpoint, interval = 30000) {
    const element = document.querySelector(selector);
    if (element) {
        setInterval(() => {
            refreshComponent(selector, endpoint);
        }, interval);
    }
}

// Global utility functions for the application
window.htmxUtils = {
    showNotification,
    refreshComponent,
    setupAutoRefresh,
    handleFormSubmit
};
