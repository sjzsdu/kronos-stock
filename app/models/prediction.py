from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class PredictionRecord(db.Model):
    """Model for storing prediction records"""
    
    __tablename__ = 'prediction_records'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic prediction parameters
    stock_code = db.Column(db.String(20), nullable=False, index=True)
    prediction_days = db.Column(db.Integer, nullable=False)
    model_type = db.Column(db.String(50), nullable=False)
    
    # Technical parameters
    lookback = db.Column(db.Integer, nullable=False, default=30)
    temperature = db.Column(db.Float, nullable=False, default=0.7)
    
    # Prediction results (stored as JSON)
    prediction_data = db.Column(db.Text)  # JSON string of prediction results
    
    # Status tracking
    status = db.Column(db.String(20), nullable=False, default='completed')  # completed, failed, processing
    error_message = db.Column(db.Text)
    
    # Metadata
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    execution_time = db.Column(db.Float)  # seconds
    
    # Optional user tracking (for future extension)
    user_id = db.Column(db.String(100), index=True)  # Can be IP or user ID
    session_id = db.Column(db.String(100), index=True)
    
    def __repr__(self):
        return f'<PredictionRecord {self.id}: {self.stock_code} - {self.model_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'stock_code': self.stock_code,
            'prediction_days': self.prediction_days,
            'model_type': self.model_type,
            'lookback': self.lookback,
            'temperature': self.temperature,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'execution_time': self.execution_time,
            'user_id': self.user_id,
            'session_id': self.session_id
        }
        
        # Parse prediction data if exists
        if self.prediction_data:
            try:
                result['prediction_data'] = json.loads(self.prediction_data)
            except json.JSONDecodeError:
                result['prediction_data'] = None
        
        if self.error_message:
            result['error_message'] = self.error_message
            
        return result
    
    def set_prediction_data(self, data):
        """Set prediction data (will be JSON serialized)"""
        if data is not None:
            self.prediction_data = json.dumps(data, ensure_ascii=False)
        else:
            self.prediction_data = None
    
    def get_prediction_data(self):
        """Get prediction data (will be JSON deserialized)"""
        if self.prediction_data:
            try:
                return json.loads(self.prediction_data)
            except json.JSONDecodeError:
                return None
        return None

# Index for common queries
db.Index('idx_stock_created', PredictionRecord.stock_code, PredictionRecord.created_at)
db.Index('idx_model_created', PredictionRecord.model_type, PredictionRecord.created_at)
db.Index('idx_status_created', PredictionRecord.status, PredictionRecord.created_at)