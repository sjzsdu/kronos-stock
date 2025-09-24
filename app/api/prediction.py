from flask import Blueprint, request, jsonify, render_template, make_response
import time
import traceback
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from app.services import model_service
from app.services.prediction_service import prediction_service
from app.models import db, PredictionRecord

# Set up logger
logger = logging.getLogger(__name__)

prediction_api = Blueprint('prediction_api', __name__)

@prediction_api.route('/predictions', methods=['POST'])
def predict():
    """Predict stock prices"""
    start_time = time.time()
    prediction_record = None
    
    try:
        data = request.get_json()
        
        # Extract parameters from frontend form
        stock_code = data.get('stock_code')
        prediction_days = data.get('prediction_days', 7)
        model_type = data.get('model_type', 'kronos-mini')
        
        # Map to backend parameters
        lookback = 30  # Default lookback period
        pred_len = int(prediction_days)  # Map prediction_days to pred_len
        temperature = 0.7  # Default temperature
        
        if not stock_code:
            return jsonify({
                'success': False,
                'error': 'stock_code is required'
            }), 400
        
        # Validate parameters
        try:
            pred_len = int(pred_len)
            temperature = float(temperature)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid parameter types'
            }), 400
        
        if not (1 <= pred_len <= 30):
            return jsonify({
                'success': False,
                'error': 'prediction_days must be between 1 and 30 days'
            }), 400
        
        if not (0.1 <= temperature <= 2.0):
            return jsonify({
                'success': False,
                'error': 'temperature must be between 0.1 and 2.0'
            }), 400
        
        # Create prediction record
        prediction_record = PredictionRecord(
            stock_code=stock_code,
            prediction_days=pred_len,
            model_type=model_type,
            lookback=lookback,
            temperature=temperature,
            status='processing',
            user_id=request.remote_addr,  # Use IP as user identifier for now
            session_id=request.headers.get('X-Session-ID', 'unknown')
        )
        
        try:
            db.session.add(prediction_record)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'error': f'Database error: {str(e)}'
            }), 500
        
        # Make prediction
        success, result = prediction_service.predict_stock(stock_code, lookback, pred_len, temperature)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Update prediction record
        try:
            prediction_record.execution_time = execution_time
            
            if success:
                prediction_record.status = 'completed'
                prediction_record.set_prediction_data(result)
                
                # Add record ID to result
                result['record_id'] = prediction_record.id
                
                db.session.commit()
                
                # Render the result as HTML for HTMX
                html_content = render_template('components/prediction_result.html', 
                                             success=True, 
                                             data=result)
                return html_content
            else:
                prediction_record.status = 'failed'
                prediction_record.error_message = result.get('error', 'Prediction failed')
                db.session.commit()
                
                error_html = render_template('components/prediction_result.html', 
                                           success=False, 
                                           error=result.get('error', 'Prediction failed'))
                return error_html
                
        except Exception as e:
            db.session.rollback()
            # Still try to return the prediction result even if DB update fails
            if success:
                result['warning'] = 'Prediction succeeded but failed to save to database'
                html_content = render_template('components/prediction_result.html', 
                                             success=True, 
                                             data=result)
                return html_content
            else:
                return jsonify({
                    'success': False,
                    'error': f'Prediction failed and database error: {str(e)}'
                }), 500
                
    except Exception as e:
        # Log the full traceback for debugging
        error_msg = str(e)
        full_traceback = traceback.format_exc()
        
        # Update prediction record if it exists
        if prediction_record:
            try:
                prediction_record.status = 'failed'
                prediction_record.error_message = error_msg
                prediction_record.execution_time = time.time() - start_time
                db.session.commit()
            except:
                db.session.rollback()
        
        return jsonify({
            'success': False,
            'error': error_msg,
            'traceback': full_traceback if request.args.get('debug') == 'true' else None
        }), 500

@prediction_api.route('/notifications/check', methods=['GET'])
def check_notifications():
    return jsonify({
        'success': True,
        'notifications': []
    })

@prediction_api.route('/model/load', methods=['POST'])
def load_model():
    """Load a specific model"""
    try:
        data = request.get_json()
        model_name = data.get('model_name', 'kronos-mini')
        
        success, message = model_service.load_model(model_name)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prediction_api.route('/model/status', methods=['GET'])
def model_status():
    """Get current model status"""
    try:
        status = model_service.get_model_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prediction_api.route('/predictions', methods=['GET'])
def get_prediction_history():
    """Get prediction history"""
    try:
        # Query parameters for filtering
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        stock_code = request.args.get('stock_code') or request.args.get('stock')
        model_type = request.args.get('model_type') or request.args.get('model')
        status = request.args.get('status')
        days = request.args.get('days', type=int)  # Time filter
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Build query
        query = PredictionRecord.query
        
        if stock_code:
            query = query.filter(PredictionRecord.stock_code == stock_code)
        if model_type:
            query = query.filter(PredictionRecord.model_type == model_type)
        if status:
            query = query.filter(PredictionRecord.status == status)
        
        # Time filter
        if days:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            query = query.filter(PredictionRecord.created_at >= cutoff_date)
        
        # Order by creation time descending
        query = query.order_by(PredictionRecord.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Convert to dictionary
        records = [record.to_dict() for record in pagination.items]
        
        # Check if this is an HTMX request
        if request.headers.get('HX-Request'):
            # Return HTML for HTMX
            return render_template('components/prediction_history.html', 
                                 records=records,
                                 pagination=pagination)
        else:
            # Return JSON for API calls
            return jsonify({
                'success': True,
                'data': {
                    'records': records,
                    'pagination': {
                        'page': page,
                        'per_page': per_page,
                        'total': pagination.total,
                        'pages': pagination.pages,
                        'has_next': pagination.has_next,
                        'has_prev': pagination.has_prev
                    }
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@prediction_api.route('/history/<int:record_id>', methods=['GET'])
def get_prediction_record(record_id):
    """Get specific prediction record with enhanced details"""
    try:
        record = PredictionRecord.query.get_or_404(record_id)
        
        # Get basic record data
        record_data = record.to_dict()
        
        # Get current stock price info using new service method
        from app.services.stock_service import stock_service
        try:
            current_price_info = stock_service.get_current_price(record.stock_code)
            record_data['current_stock_info'] = current_price_info
        except Exception as e:
            record_data['current_stock_info'] = {'error': f'获取当前价格失败: {str(e)}'}
        
        # Get stock basic info using new service method
        try:
            stock_info = stock_service.get_stock_info(record.stock_code)
            record_data['stock_basic_info'] = stock_info
        except Exception as e:
            record_data['stock_basic_info'] = {'error': f'获取股票基本信息失败: {str(e)}'}
        
        # Calculate prediction accuracy if possible
        if record.status == 'completed' and record.prediction_data:
            try:
                accuracy_analysis = calculate_prediction_accuracy_with_service(record, stock_service)
                record_data['accuracy_analysis'] = accuracy_analysis
            except Exception as e:
                logger.warning(f"Failed to calculate accuracy for record {record_id}: {e}")
                record_data['accuracy_analysis'] = {'error': f'准确率计算失败: {str(e)}'}
        
        return jsonify({
            'success': True,
            'data': record_data
        })
    except Exception as e:
        logger.error(f"Error getting prediction record {record_id}: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def calculate_prediction_accuracy_with_service(record, stock_service):
    """Calculate prediction accuracy using stock service"""
    try:
        prediction_data = record.get_prediction_data()
        if not prediction_data or 'prediction_results' not in prediction_data:
            return {'error': '无预测数据可供分析'}
        
        # Get historical data from prediction date to now
        from datetime import datetime, timedelta
        
        prediction_start = record.created_at.date()
        prediction_end = prediction_start + timedelta(days=record.prediction_days)
        current_date = datetime.now().date()
        
        # Check if enough time has passed for accuracy calculation
        if current_date < prediction_end:
            days_passed = (current_date - prediction_start).days
            return {
                'status': 'insufficient_data',
                'message': f'预测期为{record.prediction_days}天，目前已过{days_passed}天，需要更多时间验证准确性',
                'days_passed': days_passed,
                'total_days': record.prediction_days
            }
        
        # Get actual historical data for the prediction period
        start_date_str = prediction_start.strftime('%Y%m%d')
        end_date_str = min(prediction_end, current_date).strftime('%Y%m%d')
        
        historical_result = stock_service.get_historical_data(
            record.stock_code, 
            start_date_str, 
            end_date_str
        )
        
        if 'error' in historical_result:
            return {'error': f'获取历史数据失败: {historical_result["error"]}'}
        
        if not historical_result.get('data'):
            return {'error': '没有可用的历史数据进行准确率计算'}
        
        # Extract actual prices
        actual_data = historical_result['data']
        if len(actual_data) < record.prediction_days:
            return {
                'status': 'insufficient_data',
                'message': f'预测期为{record.prediction_days}天，但只获取到{len(actual_data)}天的实际数据',
                'available_days': len(actual_data)
            }
        
        # Calculate accuracy metrics
        prediction_results = prediction_data['prediction_results'][:len(actual_data)]
        predictions = [float(result['close']) for result in prediction_results]
        actual_prices = [float(day['close']) for day in actual_data[:len(predictions)]]
        
        if len(predictions) != len(actual_prices):
            return {'error': '预测数据与实际数据长度不匹配'}
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        import numpy as np
        mape = np.mean([abs((actual - pred) / actual) for actual, pred in zip(actual_prices, predictions) if actual != 0]) * 100
        
        # Calculate directional accuracy
        predicted_directions = [1 if i == 0 or predictions[i] > predictions[i-1] else 0 for i in range(len(predictions))]
        actual_directions = [1 if i == 0 or actual_prices[i] > actual_prices[i-1] else 0 for i in range(len(actual_prices))]
        directional_accuracy = sum([1 for p, a in zip(predicted_directions, actual_directions) if p == a]) / len(predicted_directions) * 100
        
        # Calculate additional metrics
        rmse = np.sqrt(np.mean([(actual - pred) ** 2 for actual, pred in zip(actual_prices, predictions)]))
        
        return {
            'status': 'completed',
            'mape': mape,
            'directional_accuracy': directional_accuracy,
            'rmse': rmse,
            'prediction_period': record.prediction_days,
            'data_points_used': len(actual_prices),
            'message': f'基于{len(actual_prices)}天数据的准确率分析'
        }
        
    except Exception as e:
        logger.error(f"Error calculating prediction accuracy: {e}")
        return {'error': f'准确率计算过程中出错: {str(e)}'}

def calculate_prediction_accuracy(record, current_df):
    """Legacy function for backward compatibility"""
    try:
        prediction_data = record.get_prediction_data()
        if not prediction_data or 'prediction_results' not in prediction_data:
            return {'error': '无预测数据可供分析'}
        
        # Get prediction start date
        prediction_start = record.created_at
        
        # Get actual prices after prediction date
        actual_data = current_df[current_df.index >= prediction_start]
        
        if len(actual_data) < record.prediction_days:
            return {
                'status': 'insufficient_data',
                'message': f'预测期为{record.prediction_days}天，但目前只有{len(actual_data)}天的实际数据',
                'available_days': len(actual_data)
            }
        
        # Calculate accuracy metrics
        prediction_results = prediction_data['prediction_results'][:len(actual_data)]
        predictions = np.array([float(result['close']) for result in prediction_results])
        actual_prices = actual_data['close'].values[:len(predictions)]
        
        # Calculate MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((actual_prices - predictions) / actual_prices)) * 100
        
        # Calculate directional accuracy
        if len(predictions) > 1:
            pred_direction = np.diff(predictions) > 0
            actual_direction = np.diff(actual_prices) > 0
            directional_accuracy = np.mean(pred_direction == actual_direction) * 100
        else:
            directional_accuracy = None
        
        return {
            'status': 'completed',
            'mape': float(mape),
            'directional_accuracy': float(directional_accuracy) if directional_accuracy is not None else None,
            'predictions': predictions.tolist() if hasattr(predictions, 'tolist') else predictions,
            'actual_prices': actual_prices.tolist(),
            'dates': [date.strftime('%Y-%m-%d') for date in actual_data.index[:len(predictions)]]
        }
        
    except Exception as e:
        return {'error': f'准确率计算失败: {str(e)}'}

@prediction_api.route('/predictions/<int:record_id>')
def get_prediction_detailed_analysis(record_id):
    """Get detailed analysis view for a prediction record"""
    try:
        record = PredictionRecord.query.get_or_404(record_id)
        
        # Get basic record data
        record_data = record.to_dict()
        
        # Get current stock data for comparison
        from app.services import stock_service
        try:
            success, current_df, message = stock_service.get_stock_data(record.stock_code, '1y')
            if success and not current_df.empty:
                # Get latest price
                latest_data = current_df.iloc[-1]
                record_data['current_stock_info'] = {
                    'current_price': float(latest_data['close']),
                    'price_change': float(latest_data['close'] - current_df.iloc[-2]['close']) if len(current_df) > 1 else 0,
                    'price_change_percent': float((latest_data['close'] - current_df.iloc[-2]['close']) / current_df.iloc[-2]['close'] * 100) if len(current_df) > 1 else 0,
                    'volume': int(latest_data['volume']) if 'volume' in latest_data else 0,
                    'high': float(latest_data['high']),
                    'low': float(latest_data['low']),
                    'last_updated': latest_data.name.strftime('%Y-%m-%d %H:%M:%S') if hasattr(latest_data.name, 'strftime') else str(latest_data.name)
                }
                
                # Calculate prediction accuracy if prediction is completed and time has passed
                if record.status == 'completed' and record.prediction_data:
                    record_data['accuracy_analysis'] = calculate_prediction_accuracy(record, current_df)
                    
            else:
                record_data['current_stock_info'] = {'error': message}
                
        except Exception as e:
            record_data['current_stock_info'] = {'error': f'获取股票数据失败: {str(e)}'}
        
        # Get stock basic info
        try:
            stock_info = stock_service.get_stock_info(record.stock_code)
            record_data['stock_basic_info'] = stock_info
        except Exception as e:
            record_data['stock_basic_info'] = {'error': f'获取股票基本信息失败: {str(e)}'}
        
        if request.headers.get('Accept') == 'application/json':
            return jsonify({
                'success': True,
                'data': record_data
            })
        else:
            # Render modal template
            return render_template('components/prediction_detail_modal.html', 
                                 record=type('obj', (object,), record_data)())
    
    except Exception as e:
        logger.error(f"Error getting detailed analysis for record {record_id}: {str(e)}")
        if request.headers.get('Accept') == 'application/json':
            return jsonify({'error': str(e)}), 500
        else:
            return render_template('components/error_modal.html', 
                                 error_message=str(e)), 500


@prediction_api.route('/predictions/<int:record_id>/chart-data')
def get_prediction_chart_data(record_id):
    """Get chart data for prediction visualization"""
    try:
        record = PredictionRecord.query.get_or_404(record_id)
        
        if record.status != 'completed' or not record.prediction_data:
            return jsonify({'error': 'Prediction not completed or no data available'}), 400
        
        prediction_data = record.get_prediction_data()
        
        # Prepare chart data structure
        chart_data = {
            'stock_code': record.stock_code,
            'prediction_data': [],
            'historical_data': [],
            'actual_data': [],
            'confidence_interval': None
        }
        
        # Get base date from record creation
        base_date = record.created_at.date()
        
        # Add prediction data points
        if 'prediction_results' in prediction_data:
            for result in prediction_data['prediction_results']:
                chart_data['prediction_data'].append({
                    'date': result['date'],
                    'predicted_price': float(result['close'])
                })
        
        # Get historical data for context (last 30 days before prediction)
        try:
            from app.services.stock_service import StockService
            stock_service = StockService()
            
            # Calculate date range for historical data
            end_date = base_date
            start_date = end_date - timedelta(days=30)
            
            historical_data = stock_service.get_historical_data(
                record.stock_code, 
                start_date.strftime('%Y%m%d'),
                end_date.strftime('%Y%m%d')
            )
            
            if historical_data and not historical_data.get('error'):
                for data_point in historical_data.get('data', []):
                    chart_data['historical_data'].append({
                        'date': data_point['date'],
                        'price': float(data_point['close'])
                    })
        except Exception as e:
            logger.warning(f"Could not fetch historical data for chart: {str(e)}")
        
        # Get actual data for comparison (if prediction period has passed)
        try:
            current_date = datetime.now().date()
            prediction_end_date = base_date + timedelta(days=record.prediction_days)
            
            if current_date > base_date:
                # Get actual data for the prediction period
                actual_end_date = min(current_date, prediction_end_date)
                actual_data = stock_service.get_historical_data(
                    record.stock_code,
                    base_date.strftime('%Y%m%d'),
                    actual_end_date.strftime('%Y%m%d')
                )
                
                if actual_data and not actual_data.get('error'):
                    for data_point in actual_data.get('data', []):
                        chart_data['actual_data'].append({
                            'date': data_point['date'],
                            'actual_price': float(data_point['close'])
                        })
        except Exception as e:
            logger.warning(f"Could not fetch actual data for comparison: {str(e)}")
        
        # Add confidence intervals if available
        if 'confidence_intervals' in prediction_data:
            intervals = prediction_data['confidence_intervals']
            chart_data['confidence_interval'] = {
                'upper': [float(x) for x in intervals.get('upper', [])],
                'lower': [float(x) for x in intervals.get('lower', [])]
            }
        
        return jsonify(chart_data)
    
    except Exception as e:
        logger.error(f"Error getting chart data for record {record_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


@prediction_api.route('/predictions/<int:record_id>/export')
def export_prediction(record_id):
    """Export prediction data in various formats"""
    try:
        record = PredictionRecord.query.get_or_404(record_id)
        format_type = request.args.get('format', 'json').lower()
        
        if record.status != 'completed' or not record.prediction_data:
            return jsonify({'error': 'Prediction not completed or no data available'}), 400
        
        # Get comprehensive record data
        record_data = get_prediction_record(record_id)
        
        if format_type == 'json':
            return export_as_json(record_data)
        elif format_type == 'csv':
            return export_as_csv(record_data)
        elif format_type == 'pdf':
            return export_as_pdf(record_data)
        else:
            return jsonify({'error': 'Unsupported format'}), 400
    
    except Exception as e:
        logger.error(f"Error exporting prediction {record_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500


def export_as_json(record_data):
    """Export prediction data as JSON"""
    response = make_response(json.dumps(record_data, indent=2, ensure_ascii=False))
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=prediction_{record_data["id"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    return response


def export_as_csv(record_data):
    """Export prediction data as CSV"""
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header information
    writer.writerow(['Prediction Export Report'])
    writer.writerow(['Generated at:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    writer.writerow([])
    
    # Basic information
    writer.writerow(['Basic Information'])
    writer.writerow(['Record ID', record_data['id']])
    writer.writerow(['Stock Code', record_data['stock_code']])
    writer.writerow(['Model Type', record_data['model_type']])
    writer.writerow(['Prediction Days', record_data['prediction_days']])
    writer.writerow(['Status', record_data['status']])
    writer.writerow(['Created At', record_data['created_at']])
    writer.writerow(['Execution Time (s)', record_data['execution_time']])
    writer.writerow([])
    
    # Prediction data
    if record_data.get('prediction_data') and record_data['prediction_data'].get('predictions'):
        writer.writerow(['Prediction Results'])
        writer.writerow(['Day', 'Predicted Price'])
        
        for i, price in enumerate(record_data['prediction_data']['predictions']):
            writer.writerow([i + 1, f'{price:.2f}'])
        writer.writerow([])
    
    # Accuracy analysis
    if record_data.get('accuracy_analysis') and record_data['accuracy_analysis'].get('status') == 'completed':
        writer.writerow(['Accuracy Analysis'])
        accuracy = record_data['accuracy_analysis']
        writer.writerow(['MAPE (%)', f'{accuracy.get("mape", 0):.2f}'])
        if 'directional_accuracy' in accuracy:
            writer.writerow(['Directional Accuracy (%)', f'{accuracy["directional_accuracy"]:.1f}'])
        writer.writerow([])
    
    # Current stock info
    if record_data.get('current_stock_info') and not record_data['current_stock_info'].get('error'):
        writer.writerow(['Current Stock Information'])
        stock_info = record_data['current_stock_info']
        writer.writerow(['Current Price', f'{stock_info.get("current_price", 0):.2f}'])
        writer.writerow(['Price Change', f'{stock_info.get("price_change", 0):.2f}'])
        writer.writerow(['Price Change (%)', f'{stock_info.get("price_change_percent", 0):.2f}'])
        writer.writerow(['Volume', stock_info.get('volume', 0)])
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    response.headers['Content-Disposition'] = f'attachment; filename=prediction_{record_data["id"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    return response


def export_as_pdf(record_data):
    """Export prediction data as PDF report"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        import io
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        story = []
        
        # Title
        title = Paragraph("股价预测分析报告", title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Basic information table
        basic_info = [
            ['记录ID', str(record_data['id'])],
            ['股票代码', record_data['stock_code']],
            ['模型类型', record_data['model_type']],
            ['预测天数', str(record_data['prediction_days'])],
            ['状态', record_data['status']],
            ['创建时间', record_data['created_at']],
            ['执行时间', f"{record_data['execution_time']:.2f}秒"]
        ]
        
        story.append(Paragraph("基本信息", subtitle_style))
        basic_table = Table(basic_info, colWidths=[2*inch, 3*inch])
        basic_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(basic_table)
        story.append(Spacer(1, 20))
        
        # Prediction results
        if record_data.get('prediction_data') and record_data['prediction_data'].get('predictions'):
            story.append(Paragraph("预测结果", subtitle_style))
            predictions = record_data['prediction_data']['predictions']
            
            pred_data = [['天数', '预测价格']]
            for i, price in enumerate(predictions[:10]):  # Show first 10 days
                pred_data.append([f'第{i+1}天', f'¥{price:.2f}'])
            
            if len(predictions) > 10:
                pred_data.append(['...', '...'])
                pred_data.append([f'第{len(predictions)}天', f'¥{predictions[-1]:.2f}'])
            
            pred_table = Table(pred_data, colWidths=[1.5*inch, 2*inch])
            pred_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(pred_table)
            story.append(Spacer(1, 20))
        
        # Accuracy analysis
        if record_data.get('accuracy_analysis') and record_data['accuracy_analysis'].get('status') == 'completed':
            story.append(Paragraph("准确率分析", subtitle_style))
            accuracy = record_data['accuracy_analysis']
            
            accuracy_data = [
                ['指标', '数值'],
                ['平均绝对百分比误差 (MAPE)', f"{accuracy.get('mape', 0):.2f}%"]
            ]
            
            if 'directional_accuracy' in accuracy:
                accuracy_data.append(['方向准确率', f"{accuracy['directional_accuracy']:.1f}%"])
            
            accuracy_table = Table(accuracy_data, colWidths=[3*inch, 2*inch])
            accuracy_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(accuracy_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=prediction_{record_data["id"]}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        buffer.close()
        return response
        
    except ImportError:
        # Fallback if reportlab is not available
        return jsonify({'error': 'PDF export not available. Please install reportlab.'}), 500
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500

@prediction_api.route('/predictions/<int:record_id>', methods=['DELETE'])
def delete_prediction_record(record_id):
    """Delete a prediction record"""
    try:
        # Get the record to delete
        record = PredictionRecord.query.get_or_404(record_id)
        
        # Log the deletion attempt
        logger.info(f"Attempting to delete prediction record {record_id} for stock {record.stock_code}")
        
        # Store record info for logging
        stock_code = record.stock_code
        model_type = record.model_type
        created_at = record.created_at
        
        # Delete the record
        db.session.delete(record)
        db.session.commit()
        
        # Log successful deletion
        logger.info(f"Successfully deleted prediction record {record_id} (stock: {stock_code}, model: {model_type}, created: {created_at})")
        
        return jsonify({
            'success': True,
            'message': f'预测记录已删除 (股票: {stock_code})',
            'deleted_record': {
                'id': record_id,
                'stock_code': stock_code,
                'model_type': model_type,
                'created_at': created_at.isoformat() if created_at else None
            }
        })
        
    except Exception as e:
        # Rollback in case of error
        db.session.rollback()
        logger.error(f"Error deleting prediction record {record_id}: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'success': False,
            'error': f'删除失败: {str(e)}',
            'message': '删除预测记录时发生错误'
        }), 500