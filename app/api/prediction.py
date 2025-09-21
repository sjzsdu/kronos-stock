from flask import Blueprint, request, jsonify, render_template
import time
import traceback
from app.services import model_service
from app.services.prediction_service import prediction_service
from app.models import db, PredictionRecord

prediction_api = Blueprint('prediction_api', __name__)

@prediction_api.route('/predict', methods=['POST'])
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

@prediction_api.route('/history', methods=['GET'])
@prediction_api.route('/predictions', methods=['GET'])  # Alias for frontend compatibility
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
    """Get specific prediction record"""
    try:
        record = PredictionRecord.query.get_or_404(record_id)
        return jsonify({
            'success': True,
            'data': record.to_dict()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500