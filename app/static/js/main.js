// Main Application JavaScript

// Chart utilities
const ChartUtils = {
    // Format data for candlestick charts
    formatCandlestickData(data) {
        return {
            x: data.map(d => d.date),
            open: data.map(d => d.open),
            high: data.map(d => d.high),
            low: data.map(d => d.low),
            close: data.map(d => d.close),
            type: 'candlestick',
            increasing: {line: {color: '#E74C3C'}},
            decreasing: {line: {color: '#26C281'}}
        };
    },
    
    // Format data for volume charts
    formatVolumeData(data) {
        return {
            x: data.map(d => d.date),
            y: data.map(d => d.volume),
            type: 'bar',
            name: '成交量',
            marker: {
                color: 'rgba(158,158,158,0.5)'
            }
        };
    },
    
    // Create prediction vs historical chart
    createPredictionChart(containerId, historicalData, predictionData, stockCode) {
        const historical = this.formatCandlestickData(historicalData);
        historical.name = '历史数据';
        
        const prediction = this.formatCandlestickData(predictionData);
        prediction.name = '预测数据';
        prediction.increasing.line.color = '#3498DB';
        prediction.decreasing.line.color = '#9B59B6';
        prediction.line = {width: 2, dash: 'dash'};
        
        const layout = {
            title: {
                text: `${stockCode} 股价预测`,
                font: {size: 16}
            },
            xaxis: {
                title: '日期',
                rangeslider: {visible: false}
            },
            yaxis: {
                title: '价格 (CNY)'
            },
            showlegend: true,
            legend: {
                x: 0,
                y: 1
            },
            margin: {l: 50, r: 50, t: 50, b: 50}
        };
        
        const config = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToRemove: ['pan2d', 'select2d', 'lasso2d'],
            displaylogo: false
        };
        
        Plotly.newPlot(containerId, [historical, prediction], layout, config);
    }
};

// Form utilities
const FormUtils = {
    // Validate stock code format
    validateStockCode(code) {
        if (!code || code.trim() === '') {
            return { valid: false, message: '股票代码不能为空' };
        }
        
        code = code.trim().toUpperCase();
        
        // Basic validation patterns
        const patterns = [
            /^\d{6}$/,  // 6-digit codes
            /^(SH|SZ)\.\d{6}$/,  // Exchange prefix codes
            /^[A-Z0-9.-]+$/  // General alphanumeric codes for demo
        ];
        
        const isValid = patterns.some(pattern => pattern.test(code));
        
        if (!isValid) {
            return { valid: false, message: '股票代码格式无效' };
        }
        
        return { valid: true, code: code };
    },
    
    // Format form data for API submission
    formatPredictionData(formData) {
        return {
            stock_code: formData.get('stock_code')?.trim().toUpperCase(),
            lookback: parseInt(formData.get('lookback')) || 30,
            pred_len: parseInt(formData.get('pred_len')) || 5,
            temperature: parseFloat(formData.get('temperature')) || 0.7
        };
    }
};

// Data formatting utilities
const DataUtils = {
    // Format number with Chinese locale
    formatNumber(num, decimals = 2) {
        return new Intl.NumberFormat('zh-CN', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(num);
    },
    
    // Format percentage
    formatPercentage(num, decimals = 2) {
        const formatted = this.formatNumber(num, decimals);
        return num > 0 ? `+${formatted}%` : `${formatted}%`;
    },
    
    // Format currency
    formatCurrency(num, currency = 'CNY') {
        return new Intl.NumberFormat('zh-CN', {
            style: 'currency',
            currency: currency,
            minimumFractionDigits: 2
        }).format(num);
    },
    
    // Format date
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        }).format(date);
    }
};

// UI enhancement utilities
const UIUtils = {
    // Add loading state to element
    addLoadingState(element, text = '加载中...') {
        if (!element) return;
        
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = `<div class="loading">${text}</div>`;
        element.classList.add('loading-state');
    },
    
    // Remove loading state from element
    removeLoadingState(element) {
        if (!element || !element.dataset.originalContent) return;
        
        element.innerHTML = element.dataset.originalContent;
        element.classList.remove('loading-state');
        delete element.dataset.originalContent;
    },
    
    // Animate number counting
    animateNumber(element, startVal, endVal, duration = 1000) {
        if (!element) return;
        
        const startTime = Date.now();
        const startValue = parseFloat(startVal) || 0;
        const endValue = parseFloat(endVal) || 0;
        const difference = endValue - startValue;
        
        const updateNumber = () => {
            const currentTime = Date.now();
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function (easeOutCubic)
            const eased = 1 - Math.pow(1 - progress, 3);
            const currentValue = startValue + (difference * eased);
            
            element.textContent = DataUtils.formatNumber(currentValue);
            
            if (progress < 1) {
                requestAnimationFrame(updateNumber);
            }
        };
        
        requestAnimationFrame(updateNumber);
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Kronos Stock Prediction System initialized');
    
    // Enhance number inputs with validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            const min = parseFloat(this.min);
            const max = parseFloat(this.max);
            const value = parseFloat(this.value);
            
            if (!isNaN(min) && value < min) {
                this.setCustomValidity(`值不能小于 ${min}`);
            } else if (!isNaN(max) && value > max) {
                this.setCustomValidity(`值不能大于 ${max}`);
            } else {
                this.setCustomValidity('');
            }
        });
    });
    
    // Enhance range inputs with real-time display
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const output = input.nextElementSibling;
        if (output && output.tagName === 'OUTPUT') {
            input.addEventListener('input', function() {
                output.value = this.value;
            });
        }
    });
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + Enter to submit prediction form
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const predictionForm = document.querySelector('.prediction-form');
            if (predictionForm) {
                predictionForm.requestSubmit();
            }
        }
    });
});

// Export utilities for use in other scripts
window.ChartUtils = ChartUtils;
window.FormUtils = FormUtils;
window.DataUtils = DataUtils;
window.UIUtils = UIUtils;