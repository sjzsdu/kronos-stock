from flask import jsonify, request
from . import api_bp
from datetime import datetime, timedelta
import random

# Mock notification data
mock_notifications = [
    {
        "id": 1,
        "title": "价格预警",
        "message": "贵州茅台(600519)已触及价格预警线：1650元",
        "type": "price_alert",
        "priority": "high",
        "read": False,
        "created_at": datetime.now() - timedelta(minutes=5),
        "data": {
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "price": 1650.00,
            "change": "+2.1%"
        }
    },
    {
        "id": 2,
        "title": "模型预测完成",
        "message": "比亚迪(002594)的7天预测已完成",
        "type": "prediction_complete",
        "priority": "normal",
        "read": False,
        "created_at": datetime.now() - timedelta(minutes=15),
        "data": {
            "stock_code": "002594",
            "stock_name": "比亚迪",
            "prediction_id": 123
        }
    },
    {
        "id": 3,
        "title": "系统通知",
        "message": "AI模型已更新到最新版本",
        "type": "system",
        "priority": "low",
        "read": True,
        "created_at": datetime.now() - timedelta(hours=2),
        "data": {
            "model_version": "v2.1.0"
        }
    }
]

@api_bp.route('/notifications/check')
def check_notifications():
    """Check for new notifications"""
    try:
        print("Checking notifications...")  # Debug log
        
        # Get unread notifications count
        unread_count = len([n for n in mock_notifications if not n['read']])
        print(f"Unread count: {unread_count}")  # Debug log
        
        # Get recent notifications (last 24 hours)
        recent_notifications = []
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for notification in mock_notifications:
            if notification['created_at'] > cutoff_time:
                # Convert datetime to string for JSON serialization
                notification_copy = notification.copy()
                notification_copy['created_at'] = notification['created_at'].isoformat()
                recent_notifications.append(notification_copy)
        
        # Sort by creation time (newest first)
        recent_notifications.sort(key=lambda x: x['created_at'], reverse=True)
        
        result = {
            "success": True,
            "data": {
                "unread_count": unread_count,
                "notifications": recent_notifications[:10],  # Limit to 10 most recent
                "has_more": len(recent_notifications) > 10
            }
        }
        
        print(f"Returning: {result}")  # Debug log
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in check_notifications: {str(e)}")  # Debug log
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/notifications')
def get_notifications():
    """Get all notifications with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        show_read = request.args.get('show_read', 'true').lower() == 'true'
        
        # Filter notifications
        filtered_notifications = mock_notifications
        if not show_read:
            filtered_notifications = [n for n in mock_notifications if not n['read']]
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_notifications = filtered_notifications[start:end]
        
        # Convert datetime to string for JSON serialization
        result_notifications = []
        for notification in paginated_notifications:
            notification_copy = notification.copy()
            notification_copy['created_at'] = notification['created_at'].isoformat()
            result_notifications.append(notification_copy)
        
        return jsonify({
            "success": True,
            "data": {
                "notifications": result_notifications,
                "pagination": {
                    "page": page,
                    "per_page": per_page,
                    "total": len(filtered_notifications),
                    "pages": (len(filtered_notifications) + per_page - 1) // per_page
                }
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        # Find and update notification
        for notification in mock_notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return jsonify({
                    "success": True,
                    "message": "Notification marked as read"
                })
        
        return jsonify({
            "success": False,
            "error": "Notification not found"
        }), 404
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/notifications/mark-all-read', methods=['POST'])
def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        for notification in mock_notifications:
            notification['read'] = True
        
        return jsonify({
            "success": True,
            "message": "All notifications marked as read"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """Delete a notification"""
    try:
        global mock_notifications
        mock_notifications = [n for n in mock_notifications if n['id'] != notification_id]
        
        return jsonify({
            "success": True,
            "message": "Notification deleted"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500