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
        },
        {
            'title': '系统工具',
            'icon': 'fas fa-tools',
            'items': [
                {
                    'title': '系统警报',
                    'icon': 'fas fa-bell',
                    'url': 'views.alerts',
                    'endpoint': 'views.alerts'
                },
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
        'views.prediction': 'prediction',
        'views.history': 'prediction',
        'views.alerts': 'prediction',
        'views.test': 'prediction'
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