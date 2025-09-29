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
    
    def _safe_float(self, value):
        """Safely convert value to float"""
        if pd.isna(value):
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
        
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
    
    def get_sse_data(self) -> Dict[str, Any]:
        """
        Get Shanghai Stock Exchange (SSE) market overview data
        
        Returns:
            Dictionary containing SSE market overview data
        """
        try:
            # Get real SSE summary data
            real_data = self._get_real_data('sse_summary')
            
            if real_data is not None and not real_data.empty:
                # Process SSE summary data
                records = []
                for _, row in real_data.iterrows():
                    record = {
                        'item': str(row['项目']),
                        'total': self._safe_float(row['股票']),
                        'main_board': self._safe_float(row['主板']),
                        'star_board': self._safe_float(row['科创板'])
                    }
                    records.append(record)
                
                # Calculate summary statistics
                total_companies = next((r['total'] for r in records if r['item'] == '上市公司'), 0)
                total_market_value = next((r['total'] for r in records if r['item'] == '总市值'), 0)
                avg_pe_ratio = next((r['total'] for r in records if r['item'] == '平均市盈率'), 0)
                circulating_shares = next((r['total'] for r in records if r['item'] == '流通股本'), 0)
                
                logger.info(f"Successfully retrieved SSE summary data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'records': records,
                        'summary': {
                            'total_companies': int(total_companies),
                            'total_market_value': total_market_value,
                            'avg_pe_ratio': avg_pe_ratio,
                            'circulating_shares': circulating_shares,
                            'main_board_companies': next((r['main_board'] for r in records if r['item'] == '上市公司'), 0),
                            'star_board_companies': next((r['star_board'] for r in records if r['item'] == '上市公司'), 0)
                        },
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real SSE summary data retrieved successfully ({len(records)} items)'
                }
            
            # No real data available
            logger.warning("No real SSE summary data available")
            return {
                'success': False,
                'data': None,
                'error': 'No SSE summary data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting SSE summary data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving SSE summary data: {str(e)}'
            }
    
    def get_szse_data(self) -> Dict[str, Any]:
        """
        Get Shenzhen Stock Exchange (SZSE) market overview data
        
        Returns:
            Dictionary containing SZSE market overview data
        """
        try:
            # Try SZSE daily deal data first, fallback to SSE data if not available
            real_data = self._get_real_data('szse_deal_daily')
            
            # If SZSE data not available, try SSE data as fallback
            if real_data is None or real_data.empty:
                real_data = self._get_real_data('sse_deal_daily')
            
            if real_data is not None and not real_data.empty:
                # Process SZSE/SSE daily deal data
                records = []
                for _, row in real_data.iterrows():
                    record = {
                        'item': str(row['单日情况']),
                        'total': self._safe_float(row['股票']),
                        'main_board_a': self._safe_float(row.get('主板A', row.get('主板', 0))),
                        'main_board_b': self._safe_float(row.get('主板B', 0)),
                        'growth_board': self._safe_float(row.get('科创板', row.get('创业板', 0))),
                        'stock_repurchase': self._safe_float(row.get('股票回购', 0))
                    }
                    records.append(record)
                
                # Calculate summary statistics
                market_value = next((r['total'] for r in records if r['item'] == '市价总值'), 0)
                avg_pe_ratio = next((r['total'] for r in records if r['item'] == '平均市盈率'), 0)
                turnover_volume = next((r['total'] for r in records if r['item'] == '成交量'), 0)
                turnover_amount = next((r['total'] for r in records if r['item'] == '成交金额'), 0)
                
                logger.info(f"Successfully retrieved SZSE daily data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'records': records,
                        'summary': {
                            'market_value': market_value,
                            'avg_pe_ratio': avg_pe_ratio,
                            'turnover_volume': turnover_volume,
                            'turnover_amount': turnover_amount,
                            'main_board_a_value': next((r['main_board_a'] for r in records if r['item'] == '市价总值'), 0),
                            'growth_board_value': next((r['growth_board'] for r in records if r['item'] == '市价总值'), 0),
                            'total_companies': len([r for r in records if '数量' in r['item'] or '家数' in r['item']])
                        },
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real SZSE daily data retrieved successfully ({len(records)} items)'
                }
            
            # No real data available
            logger.warning("No real SZSE daily data available")
            return {
                'success': False,
                'data': None,
                'error': 'No SZSE daily data available - real-time data service not accessible'
            }
            
        except Exception as e:
            logger.error(f"Error getting SZSE daily data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving SZSE daily data: {str(e)}'
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
        Get regional trading data from SZSE area summary
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            region: Region filter
            
        Returns:
            Dictionary containing regional trading data with summary statistics
        """
        try:
            # Get SZSE area summary data  
            real_data = self._get_real_data('szse_area_summary')
            
            # If no data, try reinitializing MarketData instance with fresh date
            if (real_data is None or real_data.empty) and self.market_instance is not None:
                try:
                    from china_stock_data import MarketData
                    current_month = datetime.now().strftime('%Y%m')
                    self.market_instance = MarketData(date=current_month, symbol='当月')
                    real_data = self._get_real_data('szse_area_summary')
                except Exception as e:
                    logger.warning(f"Failed to reinitialize MarketData: {str(e)}")
            
            if real_data is not None and not real_data.empty:
                # Process regional trading data
                records = []
                total_trading_amount = 0
                
                for _, row in real_data.iterrows():
                    record = {
                        'rank': int(row['序号']),
                        'region': str(row['地区']),
                        'total_amount': self._safe_float(row['总交易额']),
                        'market_share': self._safe_float(row['占市场']),
                        'stock_amount': self._safe_float(row['股票交易额']),
                        'fund_amount': self._safe_float(row['基金交易额']),
                        'bond_amount': self._safe_float(row['债券交易额'])
                    }
                    
                    # Apply region filter if specified
                    if region and region.lower() not in record['region'].lower():
                        continue
                        
                    records.append(record)
                    total_trading_amount += record['total_amount']
                
                # Calculate summary statistics
                top_regions = sorted(records[:10], key=lambda x: x['total_amount'], reverse=True)
                avg_market_share = sum(r['market_share'] for r in records) / len(records) if records else 0
                
                logger.info(f"Successfully retrieved SZSE area data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'records': records,
                        'summary': {
                            'total_regions': len(records),
                            'total_trading_amount': total_trading_amount,
                            'avg_market_share': avg_market_share,
                            'top_regions': [r['region'] for r in top_regions[:5]],
                            'top_trading_amounts': [r['total_amount'] for r in top_regions[:5]]
                        },
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real SZSE area data retrieved successfully ({len(records)} regions)'
                }
            
            # No real data available, provide sample data for demonstration
            logger.warning("No real SZSE area data available, using sample data")
            
            # Sample data based on typical regional trading patterns
            sample_records = [
                {'rank': 1, 'region': '上海', 'total_amount': 4800766000000, 'market_share': 17.98, 'stock_amount': 2223904000000, 'fund_amount': 189403700000, 'bond_amount': 2386916000000},
                {'rank': 2, 'region': '深圳', 'total_amount': 3461262000000, 'market_share': 12.96, 'stock_amount': 1602554000000, 'fund_amount': 162348600000, 'bond_amount': 1696359000000},
                {'rank': 3, 'region': '北京', 'total_amount': 2758256000000, 'market_share': 10.33, 'stock_amount': 1265754000000, 'fund_amount': 133778200000, 'bond_amount': 1358182000000},
                {'rank': 4, 'region': '浙江', 'total_amount': 2125194000000, 'market_share': 7.96, 'stock_amount': 1437788000000, 'fund_amount': 54978760000, 'bond_amount': 632426800000},
                {'rank': 5, 'region': '江苏', 'total_amount': 1988666000000, 'market_share': 7.45, 'stock_amount': 1096425000000, 'fund_amount': 77053870000, 'bond_amount': 815187400000},
                {'rank': 6, 'region': '广东', 'total_amount': 1645123000000, 'market_share': 6.16, 'stock_amount': 945321000000, 'fund_amount': 65432100000, 'bond_amount': 634370000000},
                {'rank': 7, 'region': '山东', 'total_amount': 987654000000, 'market_share': 3.70, 'stock_amount': 567890000000, 'fund_amount': 43210000000, 'bond_amount': 376554000000},
                {'rank': 8, 'region': '福建', 'total_amount': 765432000000, 'market_share': 2.87, 'stock_amount': 432100000000, 'fund_amount': 32109800000, 'bond_amount': 301222200000},
                {'rank': 9, 'region': '河南', 'total_amount': 654321000000, 'market_share': 2.45, 'stock_amount': 376543000000, 'fund_amount': 27654300000, 'bond_amount': 250123700000},
                {'rank': 10, 'region': '湖北', 'total_amount': 543210000000, 'market_share': 2.03, 'stock_amount': 312345000000, 'fund_amount': 23456700000, 'bond_amount': 207408300000}
            ]
            
            # Calculate summary statistics from sample data
            total_trading_amount = sum(r['total_amount'] for r in sample_records)
            avg_market_share = sum(r['market_share'] for r in sample_records) / len(sample_records)
            top_regions = [r['region'] for r in sample_records[:5]]
            top_trading_amounts = [r['total_amount'] for r in sample_records[:5]]
            
            return {
                'success': True,
                'data': {
                    'records': sample_records,
                    'summary': {
                        'total_regions': len(sample_records),
                        'total_trading_amount': total_trading_amount,
                        'avg_market_share': avg_market_share,
                        'top_regions': top_regions,
                        'top_trading_amounts': top_trading_amounts
                    },
                    'date_range': {
                        'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                        'end': end_date or datetime.now().strftime('%Y-%m-%d')
                    },
                    'source': 'sample_data',
                    'total_count': len(sample_records)
                },
                'message': f'Sample SZSE area data provided for demonstration ({len(sample_records)} regions)'
            }
            
        except Exception as e:
            logger.error(f"Error getting SZSE area data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving SZSE area data: {str(e)}'
            }
    
    def get_industry_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None, industry: Optional[str] = None) -> Dict[str, Any]:
        """
        Get industry trading data from SZSE sector summary
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            industry: Industry filter
            
        Returns:
            Dictionary containing industry trading data with summary statistics
        """
        try:
            # Get SZSE sector summary data
            real_data = self._get_real_data('szse_sector_summary')
            
            # If no data, try reinitializing MarketData instance with fresh date
            if (real_data is None or real_data.empty) and self.market_instance is not None:
                try:
                    from china_stock_data import MarketData
                    current_month = datetime.now().strftime('%Y%m')
                    self.market_instance = MarketData(date=current_month, symbol='当月')
                    real_data = self._get_real_data('szse_sector_summary')
                except Exception as e:
                    logger.warning(f"Failed to reinitialize MarketData for industry: {str(e)}")
            
            if real_data is not None and not real_data.empty:
                # Process industry trading data
                records = []
                total_trading_amount = 0
                total_trading_volume = 0
                
                for _, row in real_data.iterrows():
                    record = {
                        'name_cn': str(row['项目名称']),
                        'name_en': str(row['项目名称-英文']),
                        'trading_days': int(row['交易天数']),
                        'trading_amount': self._safe_float(row['成交金额-人民币元']),
                        'amount_percentage': self._safe_float(row['成交金额-占总计']),
                        'trading_volume': self._safe_float(row['成交股数-股数']),
                        'volume_percentage': self._safe_float(row['成交股数-占总计']),
                        'transaction_count': int(row['成交笔数-笔']),
                        'transaction_percentage': self._safe_float(row['成交笔数-占总计'])
                    }
                    
                    # Apply industry filter if specified
                    if industry and industry.lower() not in record['name_cn'].lower():
                        continue
                        
                    records.append(record)
                    total_trading_amount += record['trading_amount']
                    total_trading_volume += record['trading_volume']
                
                # Calculate summary statistics
                top_industries = sorted(records[:10], key=lambda x: x['trading_amount'], reverse=True)
                avg_amount_percentage = sum(r['amount_percentage'] for r in records) / len(records) if records else 0
                avg_trading_days = sum(r['trading_days'] for r in records) / len(records) if records else 0
                
                logger.info(f"Successfully retrieved SZSE sector data: {real_data.shape}")
                return {
                    'success': True,
                    'data': {
                        'records': records,
                        'summary': {
                            'total_industries': len(records),
                            'total_trading_amount': total_trading_amount,
                            'total_trading_volume': total_trading_volume,
                            'avg_amount_percentage': avg_amount_percentage,
                            'avg_trading_days': avg_trading_days,
                            'top_industries': [r['name_cn'] for r in top_industries[:5]],
                            'top_trading_amounts': [r['trading_amount'] for r in top_industries[:5]]
                        },
                        'date_range': {
                            'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                            'end': end_date or datetime.now().strftime('%Y-%m-%d')
                        },
                        'source': 'real_data',
                        'total_count': len(real_data)
                    },
                    'message': f'Real SZSE sector data retrieved successfully ({len(records)} industries)'
                }
            
            # No real data available, provide sample data for demonstration
            logger.warning("No real SZSE sector data available, using sample data")
            
            # Sample data based on typical industry trading patterns
            sample_records = [
                {'name_cn': '电子', 'name_en': 'Electronics', 'trading_days': 20, 'trading_amount': 2850000000000, 'amount_percentage': 18.50, 'trading_volume': 42500000000, 'volume_percentage': 16.80, 'transaction_count': 8950000, 'transaction_percentage': 17.20},
                {'name_cn': '医药生物', 'name_en': 'Pharmaceuticals', 'trading_days': 20, 'trading_amount': 2340000000000, 'amount_percentage': 15.20, 'trading_volume': 35800000000, 'volume_percentage': 14.15, 'transaction_count': 7650000, 'transaction_percentage': 14.70},
                {'name_cn': '化工', 'name_en': 'Chemical', 'trading_days': 20, 'trading_amount': 1980000000000, 'amount_percentage': 12.85, 'trading_volume': 31200000000, 'volume_percentage': 12.35, 'transaction_count': 6780000, 'transaction_percentage': 13.05},
                {'name_cn': '机械设备', 'name_en': 'Machinery', 'trading_days': 20, 'trading_amount': 1650000000000, 'amount_percentage': 10.70, 'trading_volume': 26400000000, 'volume_percentage': 10.45, 'transaction_count': 5890000, 'transaction_percentage': 11.30},
                {'name_cn': '计算机', 'name_en': 'Computer', 'trading_days': 20, 'trading_amount': 1420000000000, 'amount_percentage': 9.22, 'trading_volume': 23100000000, 'volume_percentage': 9.15, 'transaction_count': 5120000, 'transaction_percentage': 9.85},
                {'name_cn': '电力设备', 'name_en': 'Power Equipment', 'trading_days': 20, 'trading_amount': 1180000000000, 'amount_percentage': 7.65, 'trading_volume': 19800000000, 'volume_percentage': 7.85, 'transaction_count': 4320000, 'transaction_percentage': 8.30},
                {'name_cn': '汽车', 'name_en': 'Automotive', 'trading_days': 20, 'trading_amount': 980000000000, 'amount_percentage': 6.36, 'trading_volume': 16500000000, 'volume_percentage': 6.52, 'transaction_count': 3780000, 'transaction_percentage': 7.25},
                {'name_cn': '有色金属', 'name_en': 'Non-ferrous Metals', 'trading_days': 20, 'trading_amount': 850000000000, 'amount_percentage': 5.52, 'trading_volume': 14200000000, 'volume_percentage': 5.62, 'transaction_count': 3210000, 'transaction_percentage': 6.17},
                {'name_cn': '通信', 'name_en': 'Telecommunications', 'trading_days': 20, 'trading_amount': 720000000000, 'amount_percentage': 4.68, 'trading_volume': 12100000000, 'volume_percentage': 4.78, 'transaction_count': 2850000, 'transaction_percentage': 5.48},
                {'name_cn': '轻工制造', 'name_en': 'Light Manufacturing', 'trading_days': 20, 'trading_amount': 610000000000, 'amount_percentage': 3.96, 'trading_volume': 10300000000, 'volume_percentage': 4.08, 'transaction_count': 2450000, 'transaction_percentage': 4.71}
            ]
            
            # Calculate summary statistics from sample data
            total_trading_amount = sum(r['trading_amount'] for r in sample_records)
            total_trading_volume = sum(r['trading_volume'] for r in sample_records)
            avg_amount_percentage = sum(r['amount_percentage'] for r in sample_records) / len(sample_records)
            avg_trading_days = sum(r['trading_days'] for r in sample_records) / len(sample_records)
            top_industries = [r['name_cn'] for r in sample_records[:5]]
            top_trading_amounts = [r['trading_amount'] for r in sample_records[:5]]
            
            return {
                'success': True,
                'data': {
                    'records': sample_records,
                    'summary': {
                        'total_industries': len(sample_records),
                        'total_trading_amount': total_trading_amount,
                        'total_trading_volume': total_trading_volume,
                        'avg_amount_percentage': avg_amount_percentage,
                        'avg_trading_days': avg_trading_days,
                        'top_industries': top_industries,
                        'top_trading_amounts': top_trading_amounts
                    },
                    'date_range': {
                        'start': start_date or (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
                        'end': end_date or datetime.now().strftime('%Y-%m-%d')
                    },
                    'source': 'sample_data',
                    'total_count': len(sample_records)
                },
                'message': f'Sample SZSE sector data provided for demonstration ({len(sample_records)} industries)'
            }
            
        except Exception as e:
            logger.error(f"Error getting SZSE sector data: {str(e)}")
            return {
                'success': False,
                'data': None,
                'error': f'Error retrieving SZSE sector data: {str(e)}'
            }

# Create a singleton instance
market_data_service = MarketDataService()