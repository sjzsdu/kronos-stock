import pandas as pd
import datetime
import json
import os
from typing import Dict, Any, List, Tuple, Optional
from flask import current_app

from .model_service import model_service
from .stock_service import stock_service

class PredictionService:
    """Stock prediction service"""
    
    def predict_stock(self, stock_code: str, lookback: int = 30, 
                     pred_len: int = 5, temperature: float = 0.7) -> Tuple[bool, Dict[str, Any]]:
        """Predict stock prices"""
        try:
            # Validate inputs
            if not model_service.is_model_loaded():
                return False, {'error': 'No model is loaded. Please load a model first.'}
            
            # Validate stock code
            valid, validated_code = stock_service.validate_stock_code(stock_code)
            if not valid:
                return False, {'error': f'Invalid stock code: {validated_code}'}
            
            # Get stock data
            success, df, message = stock_service.get_stock_data(validated_code)
            if not success:
                return False, {'error': message}
            
            if len(df) < lookback:
                return False, {'error': f'Insufficient data. Need at least {lookback} days, got {len(df)} days.'}
            
            # Prepare data for prediction
            x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume']].copy()
            x_timestamp = df.iloc[-lookback:]['timestamps']
            
            # Generate future timestamps (trading days only)
            future_dates = self._generate_future_trading_dates(
                df['timestamps'].iloc[-1].date(), pred_len
            )
            y_timestamp = pd.Series(future_dates)
            
            # Make prediction
            pred_df = model_service.predictor.predict(
                df=x_df,
                x_timestamp=x_timestamp, 
                y_timestamp=y_timestamp,
                pred_len=pred_len,
                T=temperature,
                top_p=0.9,
                sample_count=1,
                verbose=False
            )
            
            # Format prediction results
            results = self._format_prediction_results(pred_df, df['close'].iloc[-1])
            
            # Generate summary
            summary = self._generate_prediction_summary(df, pred_df, lookback, pred_len)
            
            # Save prediction results
            filename = self._save_prediction_results(validated_code, results, df, {
                'lookback': lookback,
                'pred_len': pred_len, 
                'temperature': temperature
            })
            
            return True, {
                'stock_code': validated_code,
                'prediction_results': results,
                'prediction_summary': summary,
                'saved_file': filename,
                'historical_data': self._format_historical_data(df.tail(30))  # Last 30 days for chart
            }
            
        except Exception as e:
            error_msg = f'Prediction failed: {str(e)}'
            current_app.logger.error(error_msg)
            return False, {'error': error_msg}
    
    def _generate_future_trading_dates(self, last_date: datetime.date, pred_len: int) -> List[pd.Timestamp]:
        """Generate future trading dates (weekdays only)"""
        future_dates = []
        current_date = last_date
        
        while len(future_dates) < pred_len:
            current_date += datetime.timedelta(days=1)
            if current_date.weekday() < 5:  # Monday to Friday
                future_dates.append(pd.Timestamp(current_date))
        
        return future_dates
    
    def _format_prediction_results(self, pred_df: pd.DataFrame, last_close: float) -> List[Dict[str, Any]]:
        """Format prediction results for API response"""
        results = []
        prev_close = last_close
        
        for i, (dt, row) in enumerate(pred_df.iterrows()):
            current_close = row['close']
            change_pct = (current_close - prev_close) / prev_close * 100
            
            results.append({
                'date': dt.strftime('%Y-%m-%d'),
                'weekday': dt.strftime('%A'),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(current_close),
                'volume': float(row.get('volume', 0)),
                'change_pct': float(change_pct)
            })
            
            prev_close = current_close
        
        return results
    
    def _format_historical_data(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Format historical data for charts"""
        historical = []
        
        for i, (dt, row) in enumerate(df.iterrows()):
            if i == 0:
                change_pct = 0
                prev_close = row['close']
            else:
                prev_close = df.iloc[i-1]['close']
                change_pct = (row['close'] - prev_close) / prev_close * 100
            
            historical.append({
                'date': dt.strftime('%Y-%m-%d') if hasattr(dt, 'strftime') else str(dt),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row.get('volume', 0)),
                'change_pct': float(change_pct)
            })
        
        return historical
    
    def _generate_prediction_summary(self, df: pd.DataFrame, pred_df: pd.DataFrame,
                                   lookback: int, pred_len: int) -> Dict[str, Any]:
        """Generate prediction summary statistics"""
        current_price = float(df['close'].iloc[-1])
        target_price = float(pred_df['close'].iloc[-1])
        total_change_pct = (target_price - current_price) / current_price * 100
        
        return {
            'current_price': current_price,
            'target_price': target_price,
            'total_change_pct': float(total_change_pct),
            'prediction_period': f'{pred_len} days',
            'actual_lookback': lookback,
            'trend': 'bullish' if total_change_pct > 1 else 'bearish' if total_change_pct < -1 else 'neutral'
        }
    
    def _save_prediction_results(self, stock_code: str, results: List[Dict[str, Any]], 
                               df: pd.DataFrame, params: Dict[str, Any]) -> str:
        """Save prediction results to file"""
        try:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'prediction_{stock_code}_{timestamp}.json'
            
            # Create results directory if it doesn't exist
            results_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'results')
            os.makedirs(results_dir, exist_ok=True)
            
            filepath = os.path.join(results_dir, filename)
            
            # Prepare data to save
            save_data = {
                'stock_code': stock_code,
                'timestamp': timestamp,
                'parameters': params,
                'prediction_results': results,
                'historical_context': {
                    'last_30_days': self._format_historical_data(df.tail(30)),
                    'data_range': {
                        'start': df.index[0].strftime('%Y-%m-%d') if hasattr(df.index[0], 'strftime') else str(df.index[0]),
                        'end': df.index[-1].strftime('%Y-%m-%d') if hasattr(df.index[-1], 'strftime') else str(df.index[-1]),
                        'total_days': len(df)
                    }
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            current_app.logger.info(f"Prediction results saved to: {filename}")
            return filename
            
        except Exception as e:
            current_app.logger.error(f"Failed to save prediction results: {str(e)}")
            return ""

# Global prediction service instance  
prediction_service = PredictionService()