"""
Menu configuration for header (primary) and sidebar (secondary) navigation
"""

# Primary menu configuration (header navigation)
PRIMARY_MENU = [
    {
        'key': 'prediction',
        'title': '股票预测',
        'icon': 'fas fa-chart-line',
        'has_sidebar': True,
        'default_url': 'views.prediction'
    },
    {
        'key': 'market',
        'title': '市场数据',
        'icon': 'fas fa-chart-bar',
        'has_sidebar': True,
        'default_url': 'views.market_top_list'
    }
]

# Secondary menu configuration (sidebar navigation)
SIDEBAR_MENUS = {
    'prediction': [
        {
            'title': '预测功能',
            'icon': 'fas fa-crystal-ball',
            'items': [
                {
                    'title': '股票预测',
                    'icon': 'fas fa-chart-line',
                    'url': 'views.prediction',
                    'endpoint': 'views.prediction'
                },
                {
                    'title': '预测历史',
                    'icon': 'fas fa-history',
                    'url': 'views.history',
                    'endpoint': 'views.history'
                }
            ]
        }
    ],
    'market': [
        {
            'title': '交易数据',
            'icon': 'fas fa-exchange-alt',
            'items': [
                {
                    'title': '龙虎榜数据',
                    'icon': 'fas fa-trophy',
                    'url': 'views.market_top_list',
                    'endpoint': 'views.market_top_list',
                    'description': '大额交易明细'
                },
                {
                    'title': '融资融券数据',
                    'icon': 'fas fa-balance-scale',
                    'url': 'views.market_margin',
                    'endpoint': 'views.market_margin',
                    'description': '融资融券余额统计'
                },
                {
                    'title': '北向资金数据',
                    'icon': 'fas fa-arrow-down',
                    'url': 'views.market_northbound',
                    'endpoint': 'views.market_northbound',
                    'description': '外资持股情况'
                }
            ]
        },
        {
            'title': '交易所数据',
            'icon': 'fas fa-building',
            'items': [
                {
                    'title': '上交所数据',
                    'icon': 'fas fa-chart-area',
                    'url': 'views.market_sse',
                    'endpoint': 'views.market_sse',
                    'description': '上海证券交易所市场统计'
                },
                {
                    'title': '深交所数据',
                    'icon': 'fas fa-chart-pie',
                    'url': 'views.market_szse',
                    'endpoint': 'views.market_szse',
                    'description': '深圳证券交易所市场统计'
                }
            ]
        },
        {
            'title': '分类统计',
            'icon': 'fas fa-chart-column',
            'items': [
                {
                    'title': '地区成交数据',
                    'icon': 'fas fa-map-marker-alt',
                    'url': 'views.market_region_data',
                    'endpoint': 'views.market_region_data',
                    'description': '按地区分类的交易统计'
                },
                {
                    'title': '行业成交数据',
                    'icon': 'fas fa-industry',
                    'url': 'views.market_industry',
                    'endpoint': 'views.market_industry',
                    'description': '按行业分类的交易统计'
                }
            ]
        }
    ]
}

def get_theme_for_endpoint(endpoint):
    """
    Determine which theme/menu a specific endpoint belongs to
    """
    # Map endpoints to themes
    endpoint_theme_map = {
        # Prediction theme
        'views.prediction': 'prediction',
        'views.history': 'prediction',
        
        # Market theme
        'views.market_top_list': 'market',
        'views.market_margin': 'market',
        'views.market_northbound': 'market',
        'views.market_sse': 'market',
        'views.market_szse': 'market',
        'views.market_region': 'market',
        'views.market_industry': 'market',
    }
    
    return endpoint_theme_map.get(endpoint)

def get_sidebar_menu_for_theme(theme):
    """
    Get sidebar menu configuration for a specific theme
    """
    return SIDEBAR_MENUS.get(theme, [])

def should_use_sidebar(endpoint):
    """
    Determine if an endpoint should use sidebar layout
    """
    theme = get_theme_for_endpoint(endpoint)
    return theme is not None