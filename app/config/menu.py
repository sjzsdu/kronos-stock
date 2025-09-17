"""
Menu configuration for header (primary) and sidebar (secondary) navigation
"""

# Primary menu configuration (header navigation)
PRIMARY_MENU = [
    {
        'key': 'prediction',
        'title': '股票预测',
        'icon': 'fas fa-chart-line',
        'has_sidebar': True
    },
    {
        'key': 'trading', 
        'title': '投资交易',
        'icon': 'fas fa-chart-pie',
        'has_sidebar': True
    },
    {
        'key': 'analysis',
        'title': '分析工具', 
        'icon': 'fas fa-chart-area',
        'has_sidebar': True
    },
    {
        'key': 'market_news',
        'title': '市场资讯',
        'icon': 'fas fa-newspaper',
        'has_sidebar': False,
        'url': 'views.market_news'
    },
    {
        'key': 'community',
        'title': '投资社区',
        'icon': 'fas fa-users', 
        'has_sidebar': False,
        'url': 'views.community'
    },
    {
        'key': 'learning',
        'title': '学习中心',
        'icon': 'fas fa-graduation-cap',
        'has_sidebar': False,
        'url': 'views.learning'
    },
    {
        'key': 'admin',
        'title': '系统管理',
        'icon': 'fas fa-user-cog',
        'has_sidebar': True
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
                    'title': 'AI预测',
                    'icon': 'fas fa-robot',
                    'url': 'views.prediction', 
                    'endpoint': 'views.prediction'
                },
                {
                    'title': '股票搜索',
                    'icon': 'fas fa-search',
                    'url': 'views.stock_search',
                    'endpoint': 'views.stock_search' 
                },
                {
                    'title': '预测历史',
                    'icon': 'fas fa-history',
                    'url': 'views.history',
                    'endpoint': 'views.history'
                }
            ]
        },
        {
            'title': '市场概览',
            'icon': 'fas fa-chart-bar',
            'items': [
                {
                    'title': '仪表盘',
                    'icon': 'fas fa-tachometer-alt',
                    'url': 'views.dashboard',
                    'endpoint': 'views.dashboard'
                },
                {
                    'title': '主页',
                    'icon': 'fas fa-home',
                    'url': 'views.index',
                    'endpoint': 'views.index'
                }
            ]
        }
    ],
    
    'trading': [
        {
            'title': '投资组合',
            'icon': 'fas fa-briefcase',
            'items': [
                {
                    'title': '我的组合',
                    'icon': 'fas fa-wallet',
                    'url': 'views.portfolio',
                    'endpoint': 'views.portfolio'
                },
                {
                    'title': '监控列表',
                    'icon': 'fas fa-list-ul',
                    'url': 'views.watchlist',
                    'endpoint': 'views.watchlist'
                }
            ]
        },
        {
            'title': '交易管理',
            'icon': 'fas fa-exchange-alt',
            'items': [
                {
                    'title': '实时监控',
                    'icon': 'fas fa-tv',
                    'url': 'views.monitoring',
                    'endpoint': 'views.monitoring'
                },
                {
                    'title': '价格预警',
                    'icon': 'fas fa-bell',
                    'url': 'views.alerts',
                    'endpoint': 'views.alerts'
                }
            ]
        }
    ],
    
    'analysis': [
        {
            'title': '技术分析',
            'icon': 'fas fa-chart-line',
            'items': [
                {
                    'title': '技术指标',
                    'icon': 'fas fa-signal',
                    'url': 'views.technical_analysis',
                    'endpoint': 'views.technical_analysis'
                },
                {
                    'title': '模型对比',
                    'icon': 'fas fa-balance-scale',
                    'url': 'views.model_comparison',
                    'endpoint': 'views.model_comparison'
                }
            ]
        }
    ],
    
    'admin': [
        {
            'title': '用户管理',
            'icon': 'fas fa-user-cog',
            'items': [
                {
                    'title': '个人资料',
                    'icon': 'fas fa-user',
                    'url': 'views.profile',
                    'endpoint': 'views.profile'
                },
                {
                    'title': '系统设置',
                    'icon': 'fas fa-cog',
                    'url': 'views.settings',
                    'endpoint': 'views.settings'
                }
            ]
        },
        {
            'title': '系统工具',
            'icon': 'fas fa-tools',
            'items': [
                {
                    'title': '系统测试',
                    'icon': 'fas fa-flask',
                    'url': 'views.test',
                    'endpoint': 'views.test'
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
        'views.index': 'prediction',
        'views.prediction': 'prediction',
        'views.stock_search': 'prediction', 
        'views.history': 'prediction',
        'views.dashboard': 'prediction',
        
        # Trading theme
        'views.portfolio': 'trading',
        'views.monitoring': 'trading',
        'views.alerts': 'trading', 
        'views.watchlist': 'trading',
        
        # Analysis theme
        'views.model_comparison': 'analysis',
        'views.technical_analysis': 'analysis',
        
        # Admin theme
        'views.profile': 'admin',
        'views.settings': 'admin',
        'views.test': 'admin',
        
        # No sidebar pages
        'views.market_news': None,
        'views.community': None,
        'views.learning': None
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