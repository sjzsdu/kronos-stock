// Prediction detail modal functionality
let currentPredictionModal = null;

// Open prediction detail modal
function openPredictionDetail(recordId) {
    showNotification('正在加载预测详情...', 'info');
    
    htmx.ajax('GET', `/api/predictions/${recordId}`, {
        target: 'body',
        swap: 'beforeend',
        headers: {
            'Accept': 'text/html'
        }
    }).then(() => {
        setTimeout(() => initializePredictionChart(recordId), 100);
    }).catch(error => {
        showNotification('加载预测详情失败', 'error');
    });
}

// Close prediction detail modal
function closePredictionModal() {
    const modal = document.querySelector('.fixed.inset-0.bg-black.bg-opacity-50');
    if (modal) {
        modal.remove();
        currentPredictionModal = null;
    }
}

// Initialize prediction chart
function initializePredictionChart(recordId) {
    fetch(`/api/predictions/${recordId}/chart-data`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showChartError(data.error);
                return;
            }
            
            renderPredictionChart(data);
        })
        .catch(error => {
            showChartError('获取图表数据失败');
        });
}

// Render prediction chart using Plotly.js
function renderPredictionChart(chartData) {
    const chartContainer = document.getElementById('prediction-chart');
    if (!chartContainer) {
        return;
    }

    const traces = [];

    // Historical price trace
    if (chartData.historical_data && chartData.historical_data.length > 0) {
        traces.push({
            x: chartData.historical_data.map(d => d.date),
            y: chartData.historical_data.map(d => d.price),
            type: 'scatter',
            mode: 'lines',
            name: '历史价格',
            line: { color: '#3B82F6', width: 2 },
            hovertemplate: '日期: %{x}<br>价格: ¥%{y:.2f}<extra></extra>'
        });
    }

    // Prediction trace
    if (chartData.prediction_data && chartData.prediction_data.length > 0) {
        traces.push({
            x: chartData.prediction_data.map(d => d.date),
            y: chartData.prediction_data.map(d => d.predicted_price),
            type: 'scatter',
            mode: 'lines+markers',
            name: '预测价格',
            line: { color: '#EF4444', width: 2, dash: 'dash' },
            marker: { size: 6, color: '#EF4444' },
            hovertemplate: '日期: %{x}<br>预测价格: ¥%{y:.2f}<extra></extra>'
        });
    }

    // Actual price trace (for comparison if available)
    if (chartData.actual_data && chartData.actual_data.length > 0) {
        traces.push({
            x: chartData.actual_data.map(d => d.date),
            y: chartData.actual_data.map(d => d.actual_price),
            type: 'scatter',
            mode: 'lines+markers',
            name: '实际价格',
            line: { color: '#10B981', width: 2 },
            marker: { size: 6, color: '#10B981' },
            hovertemplate: '日期: %{x}<br>实际价格: ¥%{y:.2f}<extra></extra>'
        });
    }

    // Confidence interval (if available)
    if (chartData.confidence_interval) {
        const upperBound = {
            x: chartData.prediction_data.map(d => d.date),
            y: chartData.confidence_interval.upper,
            type: 'scatter',
            mode: 'lines',
            name: '置信区间上限',
            line: { color: 'rgba(239, 68, 68, 0.3)', width: 1 },
            showlegend: false,
            hoverinfo: 'skip'
        };
        
        const lowerBound = {
            x: chartData.prediction_data.map(d => d.date),
            y: chartData.confidence_interval.lower,
            type: 'scatter',
            mode: 'lines',
            name: '置信区间',
            line: { color: 'rgba(239, 68, 68, 0.3)', width: 1 },
            fill: 'tonexty',
            fillcolor: 'rgba(239, 68, 68, 0.1)',
            hoverinfo: 'skip'
        };
        
        traces.unshift(upperBound);
        traces.push(lowerBound);
    }

    const layout = {
        title: {
            text: `${chartData.stock_code} 股价预测分析`,
            font: { size: 18, color: '#374151' }
        },
        xaxis: {
            title: '日期',
            type: 'date',
            gridcolor: '#E5E7EB',
            showgrid: true
        },
        yaxis: {
            title: '价格 (¥)',
            gridcolor: '#E5E7EB',
            showgrid: true,
            tickformat: '.2f'
        },
        legend: {
            x: 0,
            y: 1,
            bgcolor: 'rgba(255, 255, 255, 0.8)',
            bordercolor: '#E5E7EB',
            borderwidth: 1
        },
        hovermode: 'x unified',
        margin: { l: 60, r: 20, t: 60, b: 60 },
        plot_bgcolor: '#FAFAFA',
        paper_bgcolor: '#FFFFFF'
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
        displaylogo: false,
        toImageButtonOptions: {
            format: 'png',
            filename: `prediction_${chartData.stock_code}_${new Date().getTime()}`,
            height: 500,
            width: 800,
            scale: 1
        }
    };

    Plotly.newPlot(chartContainer, traces, layout, config);
}

// Show chart error
function showChartError(errorMessage) {
    const chartContainer = document.getElementById('prediction-chart');
    if (chartContainer) {
        chartContainer.innerHTML = `
            <div class="flex items-center justify-center h-full">
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle text-red-500 text-4xl mb-4"></i>
                    <p class="text-gray-600">${errorMessage}</p>
                </div>
            </div>
        `;
    }
}

// Share prediction functionality
function sharePrediction(recordId) {
    // Generate shareable link
    const shareUrl = `${window.location.origin}/prediction/shared/${recordId}`;
    
    if (navigator.share) {
        // Use native sharing if available
        navigator.share({
            title: '股价预测分析',
            text: '查看这个股价预测分析结果',
            url: shareUrl
        }).catch(console.error);
    } else {
        // Fallback to clipboard
        navigator.clipboard.writeText(shareUrl).then(() => {
            showNotification('分享链接已复制到剪贴板', 'success');
        }).catch(() => {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = shareUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            showNotification('分享链接已复制到剪贴板', 'success');
        });
    }
}

// Export prediction functionality
function exportPrediction(recordId) {
    showNotification('正在准备导出...', 'info');
    
    // Create export options modal
    const exportModal = document.createElement('div');
    exportModal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60';
    exportModal.innerHTML = `
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div class="p-6">
                <h3 class="text-lg font-semibold mb-4">选择导出格式</h3>
                <div class="space-y-3">
                    <button onclick="performExport(${recordId}, 'json')" 
                            class="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <i class="fas fa-code text-blue-500 mr-3"></i>
                        JSON 数据格式
                    </button>
                    <button onclick="performExport(${recordId}, 'csv')" 
                            class="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <i class="fas fa-table text-green-500 mr-3"></i>
                        CSV 表格格式
                    </button>
                    <button onclick="performExport(${recordId}, 'pdf')" 
                            class="w-full p-3 text-left border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                        <i class="fas fa-file-pdf text-red-500 mr-3"></i>
                        PDF 报告格式
                    </button>
                </div>
                <div class="mt-6 text-right">
                    <button onclick="this.closest('.fixed').remove()" 
                            class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                        取消
                    </button>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(exportModal);
}

// Perform actual export
function performExport(recordId, format) {
    // Close export modal
    document.querySelector('.z-60').remove();
    
    showNotification('正在导出数据...', 'info');
    
    // Download export file
    const downloadUrl = `/api/predictions/${recordId}/export?format=${format}`;
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `prediction_${recordId}_${new Date().getTime()}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showNotification(`${format.toUpperCase()} 文件导出成功`, 'success');
}

// Create similar prediction
function createSimilarPrediction(stockCode, modelType, predictionDays) {
    closePredictionModal();
    
    // Navigate to prediction page with pre-filled parameters
    const predictionUrl = `/prediction?stock_code=${stockCode}&model=${modelType}&days=${predictionDays}`;
    
    if (window.location.pathname === '/prediction') {
        // If already on prediction page, just update form
        const stockInput = document.querySelector('input[name="stock_code"]');
        const modelSelect = document.querySelector('select[name="model_type"]');
        const daysInput = document.querySelector('input[name="prediction_days"]');
        
        if (stockInput) stockInput.value = stockCode;
        if (modelSelect) modelSelect.value = modelType;
        if (daysInput) daysInput.value = predictionDays;
        
        showNotification('已为您填写相同的预测参数', 'success');
    } else {
        // Navigate to prediction page
        window.location.href = predictionUrl;
    }
}

// Global event listeners for prediction modal
window.addEventListener('initPredictionChart', function(event) {
    if (event.detail && event.detail.recordId) {
        initializePredictionChart(event.detail.recordId);
    }
});

// Close modal on escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' && currentPredictionModal) {
        closePredictionModal();
    }
});

// Export global functions for HTMX integration
window.openPredictionDetail = openPredictionDetail;
window.closePredictionModal = closePredictionModal;
window.sharePrediction = sharePrediction;
window.exportPrediction = exportPrediction;
window.createSimilarPrediction = createSimilarPrediction;