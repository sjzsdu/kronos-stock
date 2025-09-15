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
            return True
        except ImportError:
            current_app.logger.warning("china_stock_data not available, using simulated data")
            return False
    
    def get_stock_data(self, stock_code: str, period: str = '1y') -> Tuple[bool, pd.DataFrame, str]:
        """Get stock data for given code and period"""
        try:
            if self._stock_data_available:
                return self._get_real_stock_data(stock_code, period)
            else:
                return self._get_simulated_stock_data(stock_code, period)
        except Exception as e:
            error_msg = f"Failed to get stock data: {str(e)}"
            current_app.logger.error(error_msg)
            return False, pd.DataFrame(), error_msg
    
    def _get_real_stock_data(self, stock_code: str, period: str) -> Tuple[bool, pd.DataFrame, str]:
        """Get real stock data using china_stock_data"""
        from china_stock_data import StockData
        
        stock_data = StockData()
        df = stock_data.get_stock_data(stock_code, period)
        
        if df.empty:
            return False, df, f"No data found for stock code: {stock_code}"
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, df, f"Missing columns: {missing_columns}"
        
        # Add timestamps if not present
        if 'timestamps' not in df.columns:
            df['timestamps'] = pd.to_datetime(df.index)
        
        return True, df, "Real stock data retrieved successfully"
    
    def _get_simulated_stock_data(self, stock_code: str, period: str) -> Tuple[bool, pd.DataFrame, str]:
        """Generate simulated stock data for demo purposes"""
        # Parse period to determine number of days
        days_map = {'1y': 252, '6m': 126, '3m': 63, '1m': 21}
        days = days_map.get(period, 252)
        
        # Generate date range (trading days only)
        end_date = datetime.datetime.now().date()
        dates = []
        current_date = end_date - datetime.timedelta(days=days * 2)  # Start earlier to account for weekends
        
        while len(dates) < days:
            if current_date.weekday() < 5:  # Monday to Friday
                dates.append(current_date)
            current_date += datetime.timedelta(days=1)
        
        # Generate realistic stock price data
        np.random.seed(hash(stock_code) % 2**32)  # Consistent random data for same stock
        
        base_price = 50 + (hash(stock_code) % 100)  # Base price between 50-150
        returns = np.random.normal(0.001, 0.02, days)  # Daily returns with slight upward bias
        
        prices = [base_price]
        for ret in returns[1:]:
            new_price = prices[-1] * (1 + ret)
            prices.append(max(new_price, 1.0))  # Ensure price doesn't go below 1
        
        # Generate OHLCV data
        data = []
        for i, (date, close) in enumerate(zip(dates, prices)):
            # Generate realistic OHLC based on close price
            volatility = 0.02
            high = close * (1 + np.random.uniform(0, volatility))
            low = close * (1 - np.random.uniform(0, volatility))
            
            if i == 0:
                open_price = close
            else:
                # Open near previous close with some gap
                gap = np.random.normal(0, 0.005)
                open_price = prices[i-1] * (1 + gap)
            
            # Ensure OHLC relationships are valid
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            volume = np.random.randint(1000000, 10000000)  # Random volume
            
            data.append({
                'timestamps': pd.Timestamp(date),
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('timestamps', inplace=True)
        df['timestamps'] = df.index  # Keep timestamps as column too
        
        return True, df, f"Simulated stock data generated for {stock_code}"
    
    def validate_stock_code(self, stock_code: str) -> Tuple[bool, str]:
        """Validate stock code format"""
        if not stock_code:
            return False, "Stock code cannot be empty"
        
        # Basic validation for Chinese stock codes
        stock_code = stock_code.strip().upper()
        
        # Check for common patterns: 6-digit codes, codes with exchange prefix
        if stock_code.isdigit() and len(stock_code) == 6:
            return True, stock_code
        
        # Allow codes with exchange prefix (SH.600000, SZ.000001, etc.)
        if '.' in stock_code:
            exchange, code = stock_code.split('.', 1)
            if exchange.upper() in ['SH', 'SZ'] and code.isdigit() and len(code) == 6:
                return True, stock_code
        
        # For demo purposes, accept any alphanumeric code
        if stock_code.replace('.', '').replace('-', '').isalnum():
            return True, stock_code
        
        return False, "Invalid stock code format"
    
    def get_stock_info(self, stock_code: str) -> Dict[str, Any]:
        """Get basic stock information"""
        # In a real implementation, this would fetch from a stock info API
        return {
            'code': stock_code,
            'name': f"Stock {stock_code}",  # Placeholder name
            'market': 'CN',  # Assume Chinese market
            'currency': 'CNY',
            'exchange': 'SSE' if stock_code.startswith('6') else 'SZSE'
        }

# Global stock service instance
stock_service = StockService()