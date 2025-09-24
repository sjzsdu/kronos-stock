#!/usr/bin/env python3
"""
Test script for prediction record deletion functionality
"""

import sys
import os
# Add the parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from app import create_app
from app.models import db, PredictionRecord
import json

def test_prediction_deletion():
    """Test the deletion functionality"""
    app = create_app('development')
    
    with app.app_context():
        # Check if we have any records
        records = PredictionRecord.query.all()
        print(f'Found {len(records)} existing prediction records')
            
        # Create a test record for deletion
        test_record = PredictionRecord(
            stock_code='TEST001',
            prediction_days=7,
            model_type='kronos-mini',
            status='completed',
            lookback=30,
            temperature=0.7,
            prediction_data=json.dumps({
                'stock_code': 'TEST001',
                'prediction_results': [
                    {'date': '2025-09-25', 'close': 100.0}
                ],
                'prediction_summary': {
                    'current_price': 100.0,
                    'target_price': 105.0,
                    'total_change_pct': 5.0
                }
            })
        )
        
        db.session.add(test_record)
        db.session.commit()
        
        print(f'Created test record with ID: {test_record.id}')
        
        # Test the deletion API
        with app.test_client() as client:
            response = client.delete(f'/api/predictions/{test_record.id}')
            print(f'Delete API response status: {response.status_code}')
            print(f'Delete API response data: {response.get_json()}')
            
            # Verify the record was deleted
            deleted_record = PredictionRecord.query.get(test_record.id)
            if deleted_record is None:
                print('✅ Record successfully deleted')
            else:
                print('❌ Record still exists after deletion')

if __name__ == '__main__':
    test_prediction_deletion()