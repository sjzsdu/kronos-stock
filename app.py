import os
import pandas as pd
import numpy as np
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import warnings
import datetime
warnings.filterwarnings('ignore')

## Path adjustments: ensure local embedded model (csweb/model) is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)
EMBEDDED_MODEL_DIR = os.path.join(CURRENT_DIR, 'model')
if os.path.isdir(EMBEDDED_MODEL_DIR) and EMBEDDED_MODEL_DIR not in sys.path:
    sys.path.insert(0, EMBEDDED_MODEL_DIR)
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

try:
    from model import Kronos, KronosTokenizer, KronosPredictor
    MODEL_CODE_AVAILABLE = True
except Exception as e:
    MODEL_CODE_AVAILABLE = False
    MODEL_IMPORT_ERROR = str(e)

try:
    from china_stock_data import StockData
    STOCK_DATA_AVAILABLE = True
except ImportError:
    STOCK_DATA_AVAILABLE = False
    print("Warning: china_stock_data not available, will use simulated data")

app = Flask(__name__)
CORS(app)

# Global model objects
tokenizer = None
model = None
predictor = None

# Local model directories (already downloaded under csweb/)
MODEL_DIRS_ROOT = CURRENT_DIR
AVAILABLE_MODELS = {
    'kronos-mini': {
        'name': 'kronos-mini',
        'path': 'kronos-mini',
        'context_length': 2048,
        'params': '4.1M'
    },
    'kronos-small': {
        'name': 'kronos-small',
        'path': 'kronos-small',
        'context_length': 512,
        'params': '24.7M'
    },
    'kronos-base': {
        'name': 'kronos-base',
        'path': 'kronos-base',
        'context_length': 2048,
        'params': '500M'
    }
}

# Popular Chinese stock codes
POPULAR_STOCKS = {
    '000001': '平安银行',
    '000002': '万科A',
    '600000': '浦发银行',
    '600036': '招商银行',
    '600519': '贵州茅台',
    '000858': '五粮液',
    '002415': '海康威视',
    '000725': '京东方A',
    '601318': '中国平安',
    '601288': '农业银行'
}

def get_stock_data(stock_code, days=500):
    """获取股票数据"""
    try:
        if STOCK_DATA_AVAILABLE:
            stock = StockData(stock_code, days=days)
            kline_data = stock.get_data("kline")
            
            # Convert Chinese column names to English
            column_mapping = {
                '开盘': 'open',
                '收盘': 'close', 
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume'
            }
            
            df = kline_data.rename(columns=column_mapping)
            
            # Add timestamps and amount columns
            df = df.reset_index()
            df['timestamps'] = pd.to_datetime(df['日期'])
            if 'amount' not in df.columns:
                df['amount'] = df['volume'] * df['close']
            
            # Remove NaN values
            df = df.dropna()
            
            return df, None
        else:
            # Generate simulated data if china_stock_data is not available
            return generate_simulated_stock_data(stock_code, days), None
            
    except Exception as e:
        return None, f"Failed to get stock data: {str(e)}"

# Simple health endpoint
@app.route('/api/health')
def health():
    return jsonify({
        'ok': True,
        'model_code': MODEL_CODE_AVAILABLE,
        'model_loaded': predictor is not None,
        'available_models': list(AVAILABLE_MODELS.keys())
    }), (200 if predictor is not None else 200)

def generate_simulated_stock_data(stock_code, days=500):
    """Generate simulated stock data for demonstration"""
    # Ensure we have at least 500 days for better testing
    days = max(days, 500)
    
    # Start from a base price
    base_price = 10.0 + hash(stock_code) % 100
    
    dates = pd.date_range(end=datetime.date.today(), periods=days, freq='D')
    
    # Generate price data with random walk
    np.random.seed(hash(stock_code) % 1000)
    returns = np.random.normal(0.001, 0.02, days)
    prices = [base_price]
    
    for i in range(1, days):
        new_price = prices[-1] * (1 + returns[i])
        prices.append(max(new_price, 0.1))  # Ensure positive prices
    
    # Generate OHLC data
    df = pd.DataFrame({
        'timestamps': dates,
        'open': prices,
        'close': prices,
        'high': [p * (1 + np.random.uniform(0, 0.03)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.03)) for p in prices],
        'volume': np.random.randint(1000000, 10000000, days)
    })
    
    # Ensure high >= close >= low and high >= open >= low
    df['high'] = df[['open', 'close', 'high']].max(axis=1)
    df['low'] = df[['open', 'close', 'low']].min(axis=1)
    
    df['amount'] = df['volume'] * df['close']
    
    return df

def save_prediction_results(stock_code, prediction_results, actual_data, input_data, prediction_params):
    """Save prediction results to file"""
    try:
        # Create prediction results directory
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prediction_results')
        os.makedirs(results_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'prediction_{stock_code}_{timestamp}.json'
        filepath = os.path.join(results_dir, filename)
        
        # Prepare data for saving
        save_data = {
            'timestamp': datetime.datetime.now().isoformat(),
            'stock_code': stock_code,
            'stock_name': POPULAR_STOCKS.get(stock_code, 'Unknown'),
            'prediction_params': prediction_params,
            'input_data_summary': {
                'rows': len(input_data),
                'columns': list(input_data.columns),
                'time_range': {
                    'start': input_data['timestamps'].min().isoformat(),
                    'end': input_data['timestamps'].max().isoformat()
                },
                'price_range': {
                    'open': {'min': float(input_data['open'].min()), 'max': float(input_data['open'].max())},
                    'high': {'min': float(input_data['high'].min()), 'max': float(input_data['high'].max())},
                    'low': {'min': float(input_data['low'].min()), 'max': float(input_data['low'].max())},
                    'close': {'min': float(input_data['close'].min()), 'max': float(input_data['close'].max())}
                }
            },
            'prediction_results': prediction_results,
            'actual_data': actual_data
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        return filename, None
        
    except Exception as e:
        return None, f"Failed to save prediction results: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/models')
def get_models():
    return jsonify({
        'success': True,
        'models': AVAILABLE_MODELS,
        'model_code': MODEL_CODE_AVAILABLE
    })

@app.route('/api/popular_stocks')
def get_popular_stocks():
    """Get popular stock codes"""
    return jsonify({
        'success': True,
        'stocks': POPULAR_STOCKS
    })

@app.route('/api/load_model', methods=['POST'])
def load_model():
    global tokenizer, model, predictor
    if not MODEL_CODE_AVAILABLE:
        return jsonify({'success': False, 'error': f'model code import failed: {MODEL_IMPORT_ERROR}'}), 500
    data = request.get_json(force=True) if request.data else {}
    key = data.get('model', 'kronos-small')
    device = data.get('device', 'cpu')
    conf = AVAILABLE_MODELS.get(key)
    if not conf:
        return jsonify({'success': False, 'error': f'unknown model: {key}'}), 400
    model_dir = os.path.join(MODEL_DIRS_ROOT, conf['path'])
    if not os.path.isdir(model_dir):
        return jsonify({'success': False, 'error': f'model directory missing: {model_dir}'}), 500
    try:
        tokenizer = KronosTokenizer.from_pretrained(model_dir)
        model = Kronos.from_pretrained(model_dir)
        predictor = KronosPredictor(
            model,
            tokenizer,
            device=device,
            max_context=conf['context_length']
        )
        return jsonify({'success': True, 'message': f'loaded {key} on {device}', 'model': key})
    except Exception as e:
        tokenizer = model = predictor = None
        return jsonify({'success': False, 'error': f'load failure: {e}'}), 500

@app.route('/api/stock_data', methods=['POST'])
def get_stock_data_api():
    """Get stock data"""
    try:
        data = request.get_json()
        stock_code = data.get('stock_code', '000001')
        days = data.get('days', 500)
        
        # Get stock data
        df, error = get_stock_data(stock_code, days)
        
        if error:
            return jsonify({
                'success': False,
                'error': error
            })
        
        # Prepare data info
        data_info = {
            'stock_code': stock_code,
            'stock_name': POPULAR_STOCKS.get(stock_code, 'Unknown'),
            'rows': len(df),
            'columns': list(df.columns),
            'time_range': {
                'start': df['timestamps'].min().strftime('%Y-%m-%d'),
                'end': df['timestamps'].max().strftime('%Y-%m-%d')
            },
            'price_range': {
                'min': float(df['close'].min()),
                'max': float(df['close'].max()),
                'latest': float(df['close'].iloc[-1])
            },
            'volume_range': {
                'min': float(df['volume'].min()) if 'volume' in df.columns else 0,
                'max': float(df['volume'].max()) if 'volume' in df.columns else 0,
                'latest': float(df['volume'].iloc[-1]) if 'volume' in df.columns else 0
            }
        }
        
        # Prepare chart data
        chart_data = {
            'timestamps': df['timestamps'].dt.strftime('%Y-%m-%d').tolist(),
            'open': df['open'].tolist(),
            'high': df['high'].tolist(),
            'low': df['low'].tolist(),
            'close': df['close'].tolist(),
            'volume': df['volume'].tolist() if 'volume' in df.columns else [0] * len(df)
        }
        
        return jsonify({
            'success': True,
            'data_info': data_info,
            'chart_data': chart_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to get stock data: {str(e)}'
        })

@app.route('/api/predict', methods=['POST'])
def predict():
    if predictor is None:
        return jsonify({'success': False, 'error': 'model not loaded'}), 400
    try:
        data = request.get_json(force=True)
        stock_code = data.get('stock_code', '000001')
        lookback = int(data.get('lookback', 400))
        pred_len = int(data.get('pred_len', 5))
        temperature = float(data.get('temperature', 1.0))
        days = int(data.get('days', 500))
        df, error = get_stock_data(stock_code, days)
        if error:
            return jsonify({'success': False, 'error': error})
        if len(df) < lookback + pred_len + 5:
            return jsonify({'success': False, 'error': 'insufficient historical length'})
        x_df = df.iloc[-lookback:][['open', 'high', 'low', 'close', 'volume', 'amount']]
        x_timestamp = df.iloc[-lookback:]['timestamps']
        # Build future timestamps (trading days)
        future_dates = []
        d = df['timestamps'].iloc[-1].date()
        while len(future_dates) < pred_len:
            d += datetime.timedelta(days=1)
            if d.weekday() < 5:
                future_dates.append(pd.Timestamp(d))
        y_timestamp = pd.Series(future_dates)
        pred_df = predictor.predict(
            df=x_df,
            x_timestamp=x_timestamp,
            y_timestamp=y_timestamp,
            pred_len=pred_len,
            T=temperature,
            top_p=0.9,
            sample_count=1,
            verbose=False
        )
        results = []
        prev_close = df['close'].iloc[-1]
        for i, (dt, row) in enumerate(pred_df.iterrows()):
            change_pct = (row['close'] - (prev_close if i == 0 else pred_df.iloc[i-1]['close'])) / (prev_close if i == 0 else pred_df.iloc[i-1]['close']) * 100
            results.append({
                'date': dt.strftime('%Y-%m-%d'),
                'weekday': dt.strftime('%A'),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row.get('volume', 0)),
                'change_pct': float(change_pct)
            })
        summary = {
            'current_price': float(df['close'].iloc[-1]),
            'target_price': float(pred_df['close'].iloc[-1]),
            'total_change_pct': float((pred_df['close'].iloc[-1] - df['close'].iloc[-1]) / df['close'].iloc[-1] * 100),
            'prediction_period': f'{pred_len} days',
            'actual_lookback': lookback
        }
        filename, _ = save_prediction_results(
            stock_code, results, None, df,
            {'lookback': lookback, 'pred_len': pred_len, 'temperature': temperature, 'model_loaded': True}
        )
        return jsonify({
            'success': True,
            'stock_code': stock_code,
            'prediction_results': results,
            'prediction_summary': summary,
            'saved_file': filename
        })
    except Exception as e:
        return jsonify({'success': False, 'error': f'prediction failed: {e}'})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
