from flask import render_template, request
from . import views_bp
from app.services import model_service, prediction_service, stock_service

@views_bp.route('/components/model-status')
def model_status_component():
    """HTMX component for model status"""
    model_status = model_service.get_model_status()
    return render_template('components/model_status.html', status=model_status)

@views_bp.route('/components/prediction-form')
def prediction_form_component():
    """HTMX component for prediction form"""
    return render_template('components/stock_form.html')

@views_bp.route('/components/prediction-result', methods=['POST'])
def prediction_result_component():
    """HTMX component for prediction results"""
    try:
        # Get form data
        stock_code = request.form.get('stock_code')
        lookback = int(request.form.get('lookback', 30))
        pred_len = int(request.form.get('pred_len', 5))
        temperature = float(request.form.get('temperature', 0.7))
        
        # Make prediction
        success, result = prediction_service.predict_stock(
            stock_code, lookback, pred_len, temperature
        )
        
        if success:
            return render_template('components/prediction_result.html', 
                                 success=True, data=result)
        else:
            return render_template('components/prediction_result.html',
                                 success=False, error=result.get('error'))
    
    except Exception as e:
        return render_template('components/prediction_result.html',
                             success=False, error=str(e))

@views_bp.route('/components/load-model', methods=['POST'])
def load_model_component():
    """HTMX component for loading models"""
    try:
        model_name = request.form.get('model_name')
        
        if not model_name:
            return render_template('components/model_status.html',
                                 status=model_service.get_model_status(),
                                 error="Please select a model")
        
        success, message = model_service.load_model(model_name)
        model_status = model_service.get_model_status()
        
        if success:
            return render_template('components/model_status.html',
                                 status=model_status, 
                                 success_message=message)
        else:
            return render_template('components/model_status.html',
                                 status=model_status,
                                 error=message)
    
    except Exception as e:
        return render_template('components/model_status.html',
                             status=model_service.get_model_status(),
                             error=str(e))

@views_bp.route('/components/chart-container')
def chart_container_component():
    """HTMX component for chart display"""
    stock_code = request.args.get('stock_code')
    
    if stock_code:
        # Get stock data for chart
        success, df, message = stock_service.get_stock_data(stock_code)
        if success:
            # Format data for chart
            chart_data = []
            for dt, row in df.tail(60).iterrows():  # Last 60 days
                chart_data.append({
                    'date': dt.strftime('%Y-%m-%d') if hasattr(dt, 'strftime') else str(dt),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': float(row.get('volume', 0))
                })
            
            # Convert to JSON string for template
            import json
            chart_data_json = json.dumps(chart_data)
            
            return render_template('components/chart_container.html',
                                 stock_code=stock_code,
                                 chart_data=chart_data,
                                 chart_data_json=chart_data_json)
    
    return render_template('components/chart_container.html')
