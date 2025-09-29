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
            real_data = self._get_real_data('margin_financing')  # 融资融券数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real margin data
                records = []
                for _, row in real_data.head(50).iterrows():  # Limit to 50 records for display
                    record = {}
                    # Convert date format
                    if pd.notna(row['信用交易日期']):
                        date_str = str(int(row['信用交易日期']))
                        if len(date_str) == 8:
                            formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                            record['trade_date'] = formatted_date
                        else:
                            record['trade_date'] = '未知日期'
                    else:
                        record['trade_date'] = '未知日期'
                    
                    # Map columns to standard format
                    record['margin_balance'] = float(row['融资余额']) if pd.notna(row['融资余额']) else 0
                    record['margin_buy'] = float(row['融资买入额']) if pd.notna(row['融资买入额']) else 0
                    record['short_volume'] = float(row['融券余量']) if pd.notna(row['融券余量']) else 0
                    record['short_amount'] = float(row['融券余量金额']) if pd.notna(row['融券余量金额']) else 0
                    record['short_sell'] = float(row['融券卖出量']) if pd.notna(row['融券卖出量']) else 0
                    record['total_balance'] = float(row['融资融券余额']) if pd.notna(row['融资融券余额']) else 0
                    
                    records.append(record)
                
                logger.info(f"Successfully retrieved margin data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date': date or datetime.now().strftime('%Y-%m-%d'),
                        'records': records,
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real margin data retrieved successfully ({len(records)} records)'
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
            real_data = self._get_real_data('northbound_holdings')  # 北向资金持股数据的fetcher名称
            
            if real_data is not None and not real_data.empty:
                # Process real northbound holdings data
                records = []
                for _, row in real_data.head(50).iterrows():  # Limit to 50 records for display
                    record = {}
                    
                    # Map columns to standard format
                    record['rank'] = int(row['序号']) if pd.notna(row['序号']) else 0
                    record['stock_code'] = str(int(row['代码'])).zfill(6) if pd.notna(row['代码']) else '000000'
                    record['stock_name'] = str(row['名称']) if pd.notna(row['名称']) else '未知股票'
                    record['close_price'] = float(row['今日收盘价']) if pd.notna(row['今日收盘价']) else 0
                    record['change_pct'] = float(row['今日涨跌幅']) if pd.notna(row['今日涨跌幅']) else 0
                    
                    # Holdings data
                    record['holding_shares'] = float(row['今日持股-股数']) if pd.notna(row['今日持股-股数']) else 0
                    record['holding_value'] = float(row['今日持股-市值']) if pd.notna(row['今日持股-市值']) else 0
                    record['holding_pct_float'] = float(row['今日持股-占流通股比']) if pd.notna(row['今日持股-占流通股比']) else 0
                    record['holding_pct_total'] = float(row['今日持股-占总股本比']) if pd.notna(row['今日持股-占总股本比']) else 0
                    
                    # 5-day changes
                    record['change_5d_shares'] = float(row['5日增持估计-股数']) if pd.notna(row['5日增持估计-股数']) else 0
                    record['change_5d_value'] = float(row['5日增持估计-市值']) if pd.notna(row['5日增持估计-市值']) else 0
                    record['change_5d_pct'] = float(row['5日增持估计-市值增幅']) if pd.notna(row['5日增持估计-市值增幅']) else 0
                    
                    record['sector'] = str(row['所属板块']) if pd.notna(row['所属板块']) else '其他'
                    record['date'] = str(row['日期']) if pd.notna(row['日期']) else ''
                    
                    records.append(record)
                
                # Calculate summary statistics
                total_holding_value = sum(record['holding_value'] for record in records)
                avg_holding_pct = sum(record['holding_pct_float'] for record in records) / len(records) if records else 0
                top_holdings = records[:10] if len(records) >= 10 else records
                
                logger.info(f"Successfully retrieved northbound holdings data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'records': records,
                        'summary': {
                            'total_holdings': len(records),
                            'total_value': total_holding_value,
                            'avg_holding_pct': avg_holding_pct,
                            'top_holdings': top_holdings
                        },
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real northbound holdings data retrieved successfully ({len(records)} records)'
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