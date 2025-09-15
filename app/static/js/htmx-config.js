// HTMX Configuration and Event Handlers

// Configure HTMX
document.addEventListener('DOMContentLoaded', function() {
    // Global HTMX configuration
    htmx.config.globalViewTransitions = true;
    htmx.config.refreshOnHistoryMiss = true;
    
    // Configure request timeout
    htmx.config.timeout = 30000; // 30 seconds for predictions
});

// Global error handler
document.body.addEventListener('htmx:responseError', function(event) {
    console.error('HTMX Request Error:', event.detail);
    
    // Show user-friendly error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-error';
    errorDiv.innerHTML = '<strong>请求失败</strong><br>请检查网络连接或稍后重试';
    
    // Insert error message at the top of the page
    const container = document.querySelector('.dashboard-container') || document.querySelector('.main-content');
    if (container) {
        container.insertBefore(errorDiv, container.firstChild);
        
        // Remove error message after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
});

// Loading state management
document.body.addEventListener('htmx:beforeRequest', function(event) {
    // Add loading class to target element
    const target = event.detail.target;
    if (target) {
        target.classList.add('htmx-loading');
    }
});

document.body.addEventListener('htmx:afterRequest', function(event) {
    // Remove loading class from target element
    const target = event.detail.target;
    if (target) {
        target.classList.remove('htmx-loading');
    }
});

// Form validation handlers
document.body.addEventListener('htmx:configRequest', function(event) {
    // Prediction form validation
    if (event.detail.path.includes('/components/prediction-result')) {
        const form = event.detail.elt;
        const stockCode = form.querySelector('input[name="stock_code"]')?.value;
        const lookback = form.querySelector('input[name="lookback"]')?.value;
        const predLen = form.querySelector('input[name="pred_len"]')?.value;
        
        // Validate stock code
        if (!stockCode || stockCode.trim() === '') {
            event.preventDefault();
            showNotification('请输入股票代码', 'error');
            return false;
        }
        
        // Validate numeric parameters
        if (lookback && (parseInt(lookback) < 7 || parseInt(lookback) > 252)) {
            event.preventDefault();
            showNotification('历史数据天数必须在7-252之间', 'error');
            return false;
        }
        
        if (predLen && (parseInt(predLen) < 1 || parseInt(predLen) > 30)) {
            event.preventDefault();
            showNotification('预测天数必须在1-30之间', 'error');
            return false;
        }
    }
});

// Model loading validation
document.body.addEventListener('htmx:configRequest', function(event) {
    if (event.detail.path.includes('/components/load-model')) {
        const form = event.detail.elt;
        const modelName = form.querySelector('input[name="model_name"]:checked')?.value;
        
        if (!modelName) {
            event.preventDefault();
            showNotification('请选择一个模型', 'error');
            return false;
        }
    }
});

// Success message handler
document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.successful && event.detail.target.id === 'prediction-results') {
        // Check if prediction was successful
        const resultElement = event.detail.target.querySelector('.prediction-results');
        if (resultElement) {
            showNotification('预测完成！', 'success');
        }
    }
    
    if (event.detail.successful && event.detail.target.id === 'model-status') {
        // Check for model loading success
        const successMessage = event.detail.target.querySelector('.alert-success');
        if (successMessage) {
            showNotification('模型加载成功！', 'success');
        }
    }
});

// Utility function to show notifications
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.innerHTML = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        max-width: 400px;
        opacity: 0;
        transition: opacity 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Fade out and remove
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// Custom event for model loaded
document.body.addEventListener('model-loaded', function(event) {
    console.log('Model loaded event triggered');
    // Could trigger additional UI updates here
});

// Progressive enhancement for users without JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add no-js class removal and js class addition
    document.documentElement.classList.remove('no-js');
    document.documentElement.classList.add('js');
    
    // Enhance forms for better UX
    const forms = document.querySelectorAll('form[hx-post]');
    forms.forEach(form => {
        const submitButton = form.querySelector('button[type="submit"]');
        if (submitButton) {
            const originalText = submitButton.textContent;
            
            form.addEventListener('htmx:beforeRequest', () => {
                submitButton.disabled = true;
                submitButton.textContent = '处理中...';
            });
            
            form.addEventListener('htmx:afterRequest', () => {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            });
        }
    });
});