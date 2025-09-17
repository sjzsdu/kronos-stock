from flask import jsonify
from datetime import datetime, timedelta
import random
from . import api_bp

@api_bp.route('/alerts')
def get_alerts():
    """Get user price alerts"""
    
    # Mock alerts data
    alerts = [
        {
            "id": 1,
            "stock_symbol": "000001",
            "stock_name": "平安银行",
            "alert_type": "above",
            "target_value": 15.50,
            "current_price": 14.80,
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
            "triggered_at": None,
            "notification_methods": ["email", "app"]
        },
        {
            "id": 2,
            "stock_symbol": "600519",
            "stock_name": "贵州茅台",
            "alert_type": "below",
            "target_value": 1800.00,
            "current_price": 1850.20,
            "status": "active",
            "created_at": (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d %H:%M'),
            "triggered_at": None,
            "notification_methods": ["email", "sms", "app"]
        },
        {
            "id": 3,
            "stock_symbol": "000858",
            "stock_name": "五粮液",
            "alert_type": "change_percent",
            "target_value": 5.0,
            "current_price": 168.90,
            "change_percent": 2.3,
            "status": "triggered",
            "created_at": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            "triggered_at": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
            "notification_methods": ["app"]
        },
        {
            "id": 4,
            "stock_symbol": "002594",
            "stock_name": "比亚迪",
            "alert_type": "above",
            "target_value": 280.00,
            "current_price": 275.50,
            "status": "active",
            "created_at": (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M'),
            "triggered_at": None,
            "notification_methods": ["email", "app"]
        },
        {
            "id": 5,
            "stock_symbol": "300750",
            "stock_name": "宁德时代",
            "alert_type": "below",
            "target_value": 200.00,
            "current_price": 215.30,
            "status": "inactive",
            "created_at": (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M'),
            "triggered_at": None,
            "notification_methods": ["email"]
        }
    ]
    
    # Calculate statistics
    total_alerts = len(alerts)
    active_alerts = len([a for a in alerts if a['status'] == 'active'])
    triggered_alerts = len([a for a in alerts if a['status'] == 'triggered'])
    today_alerts = len([a for a in alerts if a['created_at'].startswith(datetime.now().strftime('%Y-%m-%d'))])
    
    stats = {
        "total": total_alerts,
        "active": active_alerts,
        "triggered": triggered_alerts,
        "today": today_alerts
    }
    
    return jsonify({
        "success": True,
        "data": {
            "alerts": alerts,
            "stats": stats,
            "updated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    })

@api_bp.route('/alerts/<int:alert_id>/toggle', methods=['POST'])
def toggle_alert(alert_id):
    """Toggle alert status"""
    # Mock toggle functionality
    return jsonify({
        "success": True,
        "message": f"Alert {alert_id} status toggled",
        "data": {
            "alert_id": alert_id,
            "new_status": "active" if random.choice([True, False]) else "inactive"
        }
    })

@api_bp.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert"""
    # Mock delete functionality
    return jsonify({
        "success": True,
        "message": f"Alert {alert_id} deleted successfully"
    })

@api_bp.route('/alerts', methods=['POST'])
def create_alert():
    """Create a new price alert"""
    # Mock create functionality
    return jsonify({
        "success": True,
        "message": "Alert created successfully",
        "data": {
            "alert_id": random.randint(1000, 9999),
            "status": "active"
        }
    })