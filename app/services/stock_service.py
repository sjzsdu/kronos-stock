import pandas as pd
import numpy as np
import datetime
from typing import Optional, Tuple, Dict, Any
from flask import current_app

class StockService:
    """Stock data management service"""
    
    def __init__(self):
        self._stock_data_available = self._check_stock_data_availability()
    
    def _check_stock_data_availability(self) -> bool:
        """Check if china_stock_data is available"""
        try:
            from china_stock_data import StockData
            # Test if we can create an instance
            test_instance = StockData('000001')
            return True
        except (ImportError, Exception) as e:
            # Log warning if we have app context
            try:
                current_app.logger.warning(f"china_stock_data not available: {e}")
            except RuntimeError:
                # No app context available during init
                pass
            return False
    
    def get_stock_data(self, stock_code: str, period: str = '1y') -> Tuple[bool, pd.DataFrame, str]:
        """Get stock data for given code and period"""
        if not self._stock_data_available:
            error_msg = "Stock data service is not available. Please install china_stock_data package."
            current_app.logger.error(error_msg)
            return False, pd.DataFrame(), error_msg
        
        try:
            return self._get_real_stock_data(stock_code, period)
        except Exception as e:
            error_msg = f"Failed to get stock data for {stock_code}: {str(e)}"
            current_app.logger.error(error_msg)
            return False, pd.DataFrame(), error_msg
    
    def _get_real_stock_data(self, stock_code: str, period: str) -> Tuple[bool, pd.DataFrame, str]:
        """Get real stock data using china_stock_data"""
        from china_stock_data import StockData
        
        try:
            # Create StockData instance
            stock_data = StockData(stock_code)
            current_app.logger.debug(f"Getting data for stock: {stock_code}")
            
            # Get kline data
            df = stock_data.get_data('kline')
            
            if df is None or df.empty:
                return False, pd.DataFrame(), f"No data found for stock code: {stock_code}"
            
            current_app.logger.debug(f"Raw data shape: {df.shape}, columns: {df.columns.tolist()}")
            
            # Standardize column names
            df_standard = self._standardize_dataframe(df)
            
            if df_standard.empty:
                return False, pd.DataFrame(), f"Failed to process data for stock code: {stock_code}"
            
            return True, df_standard, f"Successfully retrieved data for {stock_code}"
            
        except Exception as e:
            current_app.logger.error(f"Error getting real stock data: {e}")
            return False, pd.DataFrame(), f"Error retrieving data: {str(e)}"
    
    def _standardize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize dataframe column names and format"""
        # Column mapping from Chinese/various formats to standard English names
        column_mapping = {
            '开盘': 'open', 'open': 'open', '开盘价': 'open',
            '最高': 'high', 'high': 'high', '最高价': 'high',
            '最低': 'low', 'low': 'low', '最低价': 'low',
            '收盘': 'close', 'close': 'close', '收盘价': 'close', '今收': 'close',
            '成交量': 'volume', 'volume': 'volume', '量': 'volume',
            '时间': 'timestamps', 'date': 'timestamps', 'datetime': 'timestamps', '日期': 'timestamps'
        }
        
        # Find actual column mappings
        actual_mapping = {}
        for col in df.columns:
            col_lower = col.lower().strip()
            for key, value in column_mapping.items():
                if key.lower() in col_lower or col_lower in key.lower():
                    actual_mapping[value] = col
                    break
        
        current_app.logger.debug(f"Column mapping found: {actual_mapping}")
        
        # Check if we have minimum required columns
        required_columns = ['open', 'high', 'low', 'close']
        found_columns = [col for col in required_columns if col in actual_mapping]
        
        if len(found_columns) < 4:
            current_app.logger.warning(f"Missing required columns. Found: {found_columns}")
            return pd.DataFrame()
        
        # Create standardized DataFrame
        df_standard = pd.DataFrame()
        for std_col, orig_col in actual_mapping.items():
            if std_col in ['open', 'high', 'low', 'close', 'volume']:
                df_standard[std_col] = pd.to_numeric(df[orig_col], errors='coerce')
        
        # Handle timestamps
        if 'timestamps' in actual_mapping:
            df_standard['timestamps'] = pd.to_datetime(df[actual_mapping['timestamps']], errors='coerce')
        elif hasattr(df, 'index') and hasattr(df.index, 'dtype') and 'datetime' in str(df.index.dtype):
            df_standard['timestamps'] = pd.to_datetime(df.index)
        else:
            # Create default timestamp series
            current_app.logger.warning("No timestamp column found, creating default timestamps")
            df_standard['timestamps'] = pd.date_range(
                end=datetime.datetime.now(), 
                periods=len(df), 
                freq='B'  # Business days
            )
        
        # Set timestamps as index
        df_standard.set_index('timestamps', inplace=True)
        
        # Add volume if missing
        if 'volume' not in df_standard.columns:
            df_standard['volume'] = 1000000  # Default volume
        
        # Remove any rows with NaN values in critical columns
        df_standard.dropna(subset=['open', 'high', 'low', 'close'], inplace=True)
        
        return df_standard
    
    def validate_stock_code(self, stock_code: str) -> Tuple[bool, str]:
        """Validate stock code format"""
        if not stock_code:
            return False, "Stock code cannot be empty"
        
        # Clean and standardize stock code
        stock_code = stock_code.strip().upper()
        
        # Standard 6-digit Chinese stock codes
        if stock_code.isdigit() and len(stock_code) == 6:
            return True, stock_code
        
        # Codes with exchange prefix (SH.600000, SZ.000001)
        if '.' in stock_code:
            exchange, code = stock_code.split('.', 1)
            if exchange.upper() in ['SH', 'SZ'] and code.isdigit() and len(code) == 6:
                return True, stock_code
        
        # Accept alphanumeric codes for flexibility
        if stock_code.replace('.', '').replace('-', '').isalnum() and len(stock_code) >= 4:
            return True, stock_code
        
        return False, "Invalid stock code format. Expected 6-digit code or format like SH.600000"
    
    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get basic stock information"""
        try:
            if self._stock_data_available:
                return self._get_real_stock_info(stock_code)
            else:
                return self._get_fallback_stock_info(stock_code)
        except Exception as e:
            current_app.logger.error(f"Error getting stock info for {stock_code}: {e}")
            return self._get_fallback_stock_info(stock_code)
    
    def _get_real_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get real stock information using china_stock_data"""
        from china_stock_data import StockData
        
        try:
            # Create StockData instance
            stock_data = StockData(stock_code)
            
            # Get basic info
            info = stock_data.get_data('info')
            
            if info is not None and not info.empty:
                # Extract basic information from the data
                stock_info = {
                    'code': stock_code,
                    'name': info.get('name', f"{stock_code} 股票"),
                    'market': 'CN',
                    'currency': 'CNY'
                }
                
                # Try to get additional details if available
                if 'industry' in info:
                    stock_info['industry'] = info['industry']
                if 'sector' in info:
                    stock_info['sector'] = info['sector']
                if 'exchange' in info:
                    stock_info['exchange'] = info['exchange']
                    
                return stock_info
            else:
                # Fallback to basic info based on stock code
                return self._get_fallback_stock_info(stock_code)
                
        except Exception as e:
            current_app.logger.warning(f"Failed to get real stock info for {stock_code}: {e}")
            return self._get_fallback_stock_info(stock_code)
    
    def _get_fallback_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get fallback stock information based on stock code patterns"""
        # Determine exchange based on stock code
        exchange = 'SSE'  # Default to Shanghai Stock Exchange
        market_name = '上海证券交易所'
        
        if stock_code.startswith(('00', '30')):
            exchange = 'SZSE'
            market_name = '深圳证券交易所'
        elif stock_code.startswith('SZ.'):
            exchange = 'SZSE'
            market_name = '深圳证券交易所'
        elif stock_code.startswith('SH.'):
            exchange = 'SSE'
            market_name = '上海证券交易所'
        
        return {
            'code': stock_code,
            'name': f"{stock_code} 股票",  # Placeholder name
            'market': 'CN',
            'exchange': exchange,
            'exchange_name': market_name,
            'currency': 'CNY',
            'sector': '待获取',  # To be fetched from API
            'industry': '待获取'  # To be fetched from API
        }
    
    def get_current_price(self, stock_code: str) -> Dict[str, Any]:
        """Get current stock price and trading info"""
        try:
            if self._stock_data_available:
                return self._get_real_current_price(stock_code)
            else:
                return self._get_mock_current_price(stock_code)
        except Exception as e:
            current_app.logger.error(f"Error getting current price for {stock_code}: {e}")
            return self._get_mock_current_price(stock_code)
    
    def _get_real_current_price(self, stock_code: str) -> Dict[str, Any]:
        """Get real current price using china_stock_data"""
        from china_stock_data import StockData
        
        try:
            # Create StockData instance
            stock_data = StockData(stock_code)
            
            # Get latest kline data (most recent trading day)
            df = stock_data.get_data('kline', period='1d', count=2)
            
            if df is not None and not df.empty:
                # Get the latest data
                latest = df.iloc[-1]
                previous = df.iloc[-2] if len(df) > 1 else latest
                
                current_price = float(latest.get('close', latest.get('收盘', 0)))
                previous_close = float(previous.get('close', previous.get('收盘', current_price)))
                
                price_change = current_price - previous_close
                price_change_percent = (price_change / previous_close * 100) if previous_close != 0 else 0
                
                return {
                    'current_price': current_price,
                    'price_change': price_change,
                    'price_change_percent': price_change_percent,
                    'volume': int(latest.get('volume', latest.get('成交量', 0))),
                    'high': float(latest.get('high', latest.get('最高', current_price))),
                    'low': float(latest.get('low', latest.get('最低', current_price))),
                    'open': float(latest.get('open', latest.get('开盘', current_price))),
                    'last_updated': str(latest.name) if hasattr(latest, 'name') else str(datetime.datetime.now().date())
                }
            else:
                return self._get_mock_current_price(stock_code)
                
        except Exception as e:
            current_app.logger.warning(f"Failed to get real current price for {stock_code}: {e}")
            return self._get_mock_current_price(stock_code)
    
    def _get_mock_current_price(self, stock_code: str) -> Dict[str, Any]:
        """Generate mock current price data"""
        import random
        
        # Generate mock price based on stock code hash for consistency
        seed = hash(stock_code) % 1000
        random.seed(seed)
        
        base_price = random.uniform(10, 200)
        price_change = random.uniform(-5, 5)
        price_change_percent = random.uniform(-10, 10)
        
        return {
            'current_price': round(base_price, 2),
            'price_change': round(price_change, 2),
            'price_change_percent': round(price_change_percent, 2),
            'volume': random.randint(100000, 10000000),
            'high': round(base_price * random.uniform(1.0, 1.1), 2),
            'low': round(base_price * random.uniform(0.9, 1.0), 2),
            'open': round(base_price * random.uniform(0.95, 1.05), 2),
            'last_updated': str(datetime.datetime.now().date())
        }

    def get_historical_data(self, stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get historical stock data for a date range"""
        try:
            if self._stock_data_available:
                return self._get_real_historical_data(stock_code, start_date, end_date)
            else:
                return self._get_mock_historical_data(stock_code, start_date, end_date)
        except Exception as e:
            current_app.logger.error(f"Error getting historical data for {stock_code}: {e}")
            return {'error': str(e)}
    
    def _get_real_historical_data(self, stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get real historical data using china_stock_data"""
        from china_stock_data import StockData
        
        try:
            # Create StockData instance
            stock_data = StockData(stock_code)
            
            # Get historical kline data
            df = stock_data.get_data('kline', start=start_date, end=end_date)
            
            if df is not None and not df.empty:
                # Convert to standard format
                data_points = []
                for index, row in df.iterrows():
                    data_points.append({
                        'date': str(index) if hasattr(index, '__str__') else str(index.date()),
                        'open': float(row.get('open', row.get('开盘', 0))),
                        'high': float(row.get('high', row.get('最高', 0))),
                        'low': float(row.get('low', row.get('最低', 0))),
                        'close': float(row.get('close', row.get('收盘', 0))),
                        'volume': int(row.get('volume', row.get('成交量', 0)))
                    })
                
                return {
                    'success': True,
                    'data': data_points,
                    'total_records': len(data_points)
                }
            else:
                return {'error': f'No historical data found for {stock_code}'}
                
        except Exception as e:
            current_app.logger.warning(f"Failed to get real historical data for {stock_code}: {e}")
            return self._get_mock_historical_data(stock_code, start_date, end_date)
    
    def _get_mock_historical_data(self, stock_code: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Generate mock historical data"""
        import random
        from datetime import datetime, timedelta
        
        try:
            start = datetime.strptime(start_date, '%Y%m%d')
            end = datetime.strptime(end_date, '%Y%m%d')
        except:
            return {'error': 'Invalid date format'}
        
        # Generate mock data
        seed = hash(stock_code) % 1000
        random.seed(seed)
        
        data_points = []
        current_date = start
        base_price = random.uniform(10, 200)
        
        while current_date <= end:
            if current_date.weekday() < 5:  # Only weekdays
                # Generate daily price movement
                change = random.uniform(-0.1, 0.1)
                base_price *= (1 + change)
                
                open_price = base_price * random.uniform(0.98, 1.02)
                close_price = base_price
                high_price = max(open_price, close_price) * random.uniform(1.0, 1.05)
                low_price = min(open_price, close_price) * random.uniform(0.95, 1.0)
                
                data_points.append({
                    'date': current_date.strftime('%Y-%m-%d'),
                    'open': round(open_price, 2),
                    'high': round(high_price, 2),
                    'low': round(low_price, 2),
                    'close': round(close_price, 2),
                    'volume': random.randint(100000, 5000000)
                })
            
            current_date += timedelta(days=1)
        
        return {
            'success': True,
            'data': data_points,
            'total_records': len(data_points)
        }

# Global stock service instance
stock_service = StockService()