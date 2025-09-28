#!/usr/bin/env python3
"""
查看china_stock_data包中市场数据的结构
"""

def explore_market_data():
    try:
        from china_stock_data import MarketData
        
        print("🔍 正在初始化MarketData...")
        market = MarketData()
        
        # 获取所有可用的fetcher
        fetchers = market.get_fetchers()
        print(f"📋 可用的数据获取器: {len(fetchers)}个")
        
        # 重点关注龙虎榜相关的fetcher
        target_fetchers = [
            ('lhb', '龙虎榜数据'),
            ('margin_trading', '融资融券数据'), 
            ('northbound_funds', '北向资金数据'),
            ('sse_summary', '上交所数据'),
            ('szse_summary', '深交所数据')
        ]
        
        for fetcher_name, description in target_fetchers:
            if fetcher_name in fetchers:
                display_fetcher_data(fetcher_name, description, market)
            else:
                print(f"⚠️  未找到 {fetcher_name} fetcher")
        
        # 显示所有可用的fetcher名称
        print(f"\n📚 所有可用的fetcher:")
        for i, fetcher in enumerate(fetchers, 1):
            print(f"   {i:2d}. {fetcher}")
            
    except ImportError:
        print("❌ 未找到china_stock_data包，请先安装")
    except Exception as e:
        print(f"❌ 初始化时出错: {str(e)}")

def display_fetcher_data(fetcher_name, description, market_instance):
    """
    展示指定fetcher的数据内容和结构
    """
    print(f"\n{'='*80}")
    print(f"📊 {description}")
    print(f"🔗 访问名称: {fetcher_name}")
    print(f"{'='*80}")
    
    try:
        # 获取数据
        data = market_instance.get_data(fetcher_name)
        
        if data.empty:
            print("❌ 数据为空")
            return
        
        # 基本信息
        print(f"📈 数据形状: {data.shape[0]}行 x {data.shape[1]}列")
        print(f"📋 列名: {list(data.columns)}")
        
        # 数据类型
        print(f"\n🔢 数据类型:")
        for col, dtype in data.dtypes.items():
            print(f"   {col}: {dtype}")
        
        # 数据预览
        print(f"\n📄 数据预览 (前3行):")
        print(data.head(3).to_string())
        
        if len(data) > 6:
            print(f"\n📄 数据预览 (后3行):")
            print(data.tail(3).to_string())
        
        # 数值列的统计信息
        numeric_cols = data.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            print(f"\n📊 数值列统计:")
            print(data[numeric_cols].describe().to_string())
        
        print(f"\n✅ 数据获取成功")
        
    except Exception as e:
        print(f"❌ 获取数据时出错: {str(e)}")

if __name__ == "__main__":
    explore_market_data()