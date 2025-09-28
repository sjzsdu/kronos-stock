"""
Market data service for handling various market data operations
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

class MarketDataService:
    """Service for market data operations"""
    
    def __init__(self):
        """Initialize market data service"""
        self.data_cache = {}
        self.cache_timeout = 300  # 5 minutes cache
        self.market_instance = None
        self._initialize_market_data()
    
    def _initialize_market_data(self):
        """Initialize china_stock_data MarketData instance"""
        try:
            from china_stock_data import MarketData
            # Use current month data by default
            current_month = datetime.now().strftime('%Y%m')
            self.market_instance = MarketData(date=current_month, symbol='当月')
            logger.info(f"MarketData initialized with date: {current_month}")
        except ImportError:
            logger.warning("china_stock_data not available, using mock data")
            self.market_instance = None
        except Exception as e:
            logger.error(f"Error initializing MarketData: {str(e)}")
            self.market_instance = None
    
    def _get_real_data(self, fetcher_name: str) -> Optional[pd.DataFrame]:
        """Get real data from china_stock_data"""
        if self.market_instance is None:
            return None
            
        try:
            # Check if data is cached
            cache_key = f"{fetcher_name}_{datetime.now().strftime('%Y%m%d_%H')}"  # Cache for 1 hour
            if cache_key in self.data_cache:
                return self.data_cache[cache_key]
            
            # Get data from MarketData
            data = self.market_instance.get_data(fetcher_name)
            
            if data is not None and not data.empty:
                self.data_cache[cache_key] = data
                logger.info(f"Successfully retrieved {fetcher_name} data: {data.shape}")
                return data
            else:
                logger.warning(f"No data returned for {fetcher_name}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting real data for {fetcher_name}: {str(e)}")
            return None
        
    def get_top_list_data(self, date: Optional[str] = None, exchange: Optional[str] = None) -> Dict[str, Any]:
        """
        Get dragon tiger list data (龙虎榜数据)
        
        Args:
            date: Query date (YYYY-MM-DD)
            exchange: Exchange filter ('sh' for SSE, 'sz' for SZSE)
            
        Returns:
            Dictionary containing top list data
        """
        try:
            # Try to get real data first
            real_data = self._get_real_data('lhb')  # 龙虎榜数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real data
                records = []
                for _, row in real_data.head(20).iterrows():  # Limit to 20 records for display
                    record = {}
                    # Map columns to standard format
                    for col in real_data.columns:
                        if '代码' in col or 'code' in col.lower():
                            record['stock_code'] = str(row[col]).zfill(6)
                        elif '名称' in col or 'name' in col.lower():
                            record['stock_name'] = str(row[col])
                        elif '成交金额' in col or 'turnover' in col.lower():
                            record['turnover'] = float(row[col]) if pd.notna(row[col]) else 0
                        elif '涨跌幅' in col or '变动' in col:
                            record['change_pct'] = float(row[col]) if pd.notna(row[col]) else 0
                        elif '上榜原因' in col or '原因' in col:
                            record['reason'] = str(row[col])
                        elif '买入金额' in col:
                            record['buy_amount'] = float(row[col]) if pd.notna(row[col]) else 0
                        elif '卖出金额' in col:
                            record['sell_amount'] = float(row[col]) if pd.notna(row[col]) else 0
                    
                    # Fill missing fields with defaults
                    record.setdefault('stock_code', '000000')
                    record.setdefault('stock_name', '未知股票')
                    record.setdefault('turnover', 0)
                    record.setdefault('change_pct', 0)
                    record.setdefault('reason', '其他')
                    record.setdefault('buy_amount', 0)
                    record.setdefault('sell_amount', 0)
                    
                    records.append(record)
                
                return {
                    'success': True,
                    'data': {
                        'date': date or datetime.now().strftime('%Y-%m-%d'),
                        'exchange': exchange or 'all',
                        'records': records,
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real data retrieved successfully ({len(records)} records)'
                }
            
            # No real data available
            logger.warning("No real data available for dragon tiger list")
            return {
                'success': False,
                'data': None,
                'error': 'No data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting top list data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'message': f'Error retrieving data: {str(e)}'
            }
    
    def get_margin_data(self, date: Optional[str] = None, exchange: Optional[str] = None) -> Dict[str, Any]:
        """
        Get margin trading data
        
        Args:
            date: Query date (YYYY-MM-DD)  
            exchange: Exchange filter
            
        Returns:
            Dictionary containing margin trading data
        """
        try:
            # Try to get real data
            real_data = self._get_real_data('margin')  # 融资融券数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real margin data
                logger.info(f"Successfully retrieved margin data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date': date or datetime.now().strftime('%Y-%m-%d'),
                        'records': real_data.to_dict('records'),
                        'source': 'real_data'
                    },
                    'message': f'Real margin data retrieved successfully'
                }
            
            # No real data available
            logger.warning("No real margin data available")
            return {
                'success': False,
                'data': None,
                'error': 'No margin data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting margin data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving margin data: {str(e)}'
            }
    
    def get_northbound_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get northbound funds data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary containing northbound funds data
        """
        try:
            # Try to get real data
            real_data = self._get_real_data('northbound')  # 北向资金数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real northbound data
                logger.info(f"Successfully retrieved northbound data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'records': real_data.to_dict('records'),
                        'source': 'real_data'
                    },
                    'message': f'Real northbound data retrieved successfully'
                }
            
            # No real data available
            logger.warning("No real northbound data available")
            return {
                'success': False,
                'data': None,
                'error': 'No northbound data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting northbound data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving northbound data: {str(e)}'
            }
    
    def get_exchange_data(self, exchange: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get exchange market data (SSE or SZSE)
        
        Args:
            exchange: 'sse' for Shanghai or 'szse' for Shenzhen
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Dictionary containing exchange market data
        """
        try:
            exchange_names = {
                'sse': '上海证券交易所',
                'szse': '深圳证券交易所'
            }
            
            # Try to get real data
            fetcher_name = f'{exchange}_data'  # 交易所数据的fetcher名称
            real_data = self._get_real_data(fetcher_name)
            
            if real_data is not None and not real_data.empty:
                # Process real exchange data
                logger.info(f"Successfully retrieved {exchange} data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'exchange': exchange_names.get(exchange, '未知交易所'),
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'records': real_data.to_dict('records'),
                        'source': 'real_data'
                    },
                    'message': f'Real {exchange_names.get(exchange)} data retrieved successfully'
                }
            
            # No real data available
            logger.warning(f"No real {exchange} data available")
            return {
                'success': False,
                'data': None,
                'error': f'No {exchange} data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting {exchange} data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving {exchange} data: {str(e)}'
            }
    
    def get_regional_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, region: Optional[str] = None) -> Dict[str, Any]:
        """
        Get regional trading data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: Region filter
            
        Returns:
            Dictionary containing regional trading data
        """
        try:
            # Try to get real data
            real_data = self._get_real_data('regional')  # 地区数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real regional data
                logger.info(f"Successfully retrieved regional data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'records': real_data.to_dict('records'),
                        'source': 'real_data'
                    },
                    'message': f'Real regional data retrieved successfully'
                }
            
            # No real data available
            logger.warning("No real regional data available")
            return {
                'success': False,
                'data': None,
                'error': 'No regional data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting regional data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving regional data: {str(e)}'
            }
    
    def get_industry_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Get industry trading data
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            industry: Industry filter
            
        Returns:
            Dictionary containing industry trading data
        """
        try:
            # Try to get real data
            real_data = self._get_real_data('industry')  # 行业数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real industry data
                logger.info(f"Successfully retrieved industry data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'records': real_data.to_dict('records'),
                        'source': 'real_data'
                    },
                    'message': f'Real industry data retrieved successfully'
                }
            
            # No real data available
            logger.warning("No real industry data available")
            return {
                'success': False,
                'data': None,
                'error': 'No industry data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting industry data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving industry data: {str(e)}'
            }

# Create a singleton instance
market_data_service = MarketDataService()