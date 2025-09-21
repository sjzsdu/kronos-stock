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
        # TODO: Integrate with real stock info API (e.g., tushare, baostock)
        # For now, return basic info based on stock code pattern
        
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

# Global stock service instance
stock_service = StockService()