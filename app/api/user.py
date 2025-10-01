# -*- coding: utf-8 -*-
"""
用户管理API
提供用户信息管理、关注列表、预测记录等接口
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user

from app.services.user_service import UserService
from app.utils.validators import sanitize_input


user_bp = Blueprint('user', __name__, url_prefix='/api/user')


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户完整档案"""
    try:
        profile = UserService.get_user_profile(current_user.id)
        
        if profile:
            profile_data = {
                'user_id': profile.user_id,
                'nickname': profile.nickname,
                'phone': profile.phone,
                'avatar_url': profile.avatar_url,
                'bio': profile.bio,
                'location': profile.location,
                'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
                'gender': profile.gender,
                'investment_experience': profile.investment_experience,
                'risk_preference': profile.risk_preference,
                'preferences': profile.get_preferences(),
                'notification_settings': profile.get_notification_settings(),
                'created_at': profile.created_at.isoformat(),
                'updated_at': profile.updated_at.isoformat() if profile.updated_at else None
            }
        else:
            profile_data = None
        
        return jsonify({
            'success': True,
            'profile': profile_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户档案API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取用户档案失败'
        }), 500


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户档案"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供更新数据'
            }), 400
        
        # 清理输入数据
        clean_data = {}
        text_fields = ['full_name', 'nickname', 'bio', 'location']
        for field in text_fields:
            if field in data:
                clean_data[field] = sanitize_input(data[field], 200)
        
        # 其他字段直接复制
        direct_fields = [
            'phone', 'avatar_url', 'birth_date', 'gender',
            'investment_experience', 'risk_preference',
            'preferences', 'notification_settings'
        ]
        for field in direct_fields:
            if field in data:
                clean_data[field] = data[field]
        
        # 更新档案
        success, message = UserService.update_user_profile(current_user.id, clean_data)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"更新用户档案API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '更新用户档案失败，请稍后重试'
        }), 500


@user_bp.route('/predictions', methods=['GET'])
@login_required
def get_predictions():
    """获取用户预测记录"""
    try:
        # 分页参数
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        offset = (page - 1) * per_page
        
        predictions = UserService.get_user_predictions(
            current_user.id, limit=per_page, offset=offset
        )
        
        predictions_data = []
        for pred in predictions:
            predictions_data.append({
                'id': pred.id,
                'stock_code': pred.stock_code,
                'model_type': pred.model_type,
                'prediction_type': pred.prediction_type,
                'prediction_result': pred.prediction_result,
                'metadata': pred.metadata,
                'created_at': pred.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'predictions': predictions_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'has_more': len(predictions) == per_page
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取预测记录API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取预测记录失败'
        }), 500


@user_bp.route('/watchlist', methods=['GET'])
@login_required
def get_watchlist():
    """获取关注股票列表"""
    try:
        watchlist = UserService.get_user_watchlist(current_user.id)
        
        watchlist_data = []
        for item in watchlist:
            watchlist_data.append({
                'id': item.id,
                'stock_code': item.stock_code,
                'stock_name': item.stock_name,
                'notes': item.notes,
                'sort_order': item.sort_order,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat() if item.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'watchlist': watchlist_data
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取关注列表API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取关注列表失败'
        }), 500


@user_bp.route('/watchlist', methods=['POST'])
@login_required
def add_to_watchlist():
    """添加股票到关注列表"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请提供股票信息'
            }), 400
        
        stock_code = sanitize_input(data.get('stock_code', ''))
        stock_name = sanitize_input(data.get('stock_name', ''))
        notes = sanitize_input(data.get('notes', ''), 500)
        
        if not stock_code:
            return jsonify({
                'success': False,
                'message': '股票代码是必填项'
            }), 400
        
        success, message = UserService.add_to_watchlist(
            current_user.id, stock_code, stock_name, notes
        )
        
        return jsonify({
            'success': success,
            'message': message
        }), 201 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"添加关注股票API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '添加失败，请稍后重试'
        }), 500


@user_bp.route('/watchlist/<stock_code>', methods=['DELETE'])
@login_required
def remove_from_watchlist(stock_code):
    """从关注列表移除股票"""
    try:
        stock_code = sanitize_input(stock_code)
        
        if not stock_code:
            return jsonify({
                'success': False,
                'message': '无效的股票代码'
            }), 400
        
        success, message = UserService.remove_from_watchlist(current_user.id, stock_code)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"移除关注股票API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '移除失败，请稍后重试'
        }), 500


@user_bp.route('/watchlist/reorder', methods=['PUT'])
@login_required
def reorder_watchlist():
    """重新排序关注列表"""
    try:
        data = request.get_json()
        
        if not data or 'stock_codes' not in data:
            return jsonify({
                'success': False,
                'message': '请提供排序后的股票代码列表'
            }), 400
        
        stock_codes = data['stock_codes']
        if not isinstance(stock_codes, list):
            return jsonify({
                'success': False,
                'message': '股票代码列表格式错误'
            }), 400
        
        # 清理股票代码
        clean_codes = [sanitize_input(code) for code in stock_codes if code]
        
        success, message = UserService.update_watchlist_order(current_user.id, clean_codes)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"排序关注列表API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '排序失败，请稍后重试'
        }), 500


@user_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """获取用户统计信息"""
    try:
        stats = UserService.get_user_statistics(current_user.id)
        
        # 格式化统计数据
        formatted_stats = {
            'total_predictions': stats.get('total_predictions', 0),
            'monthly_predictions': stats.get('monthly_predictions', 0),
            'watchlist_count': stats.get('watchlist_count', 0),
            'last_prediction_at': stats.get('last_prediction_at').isoformat() if stats.get('last_prediction_at') else None,
            'favorite_models': stats.get('favorite_models', []),
            'joined_at': stats.get('joined_at').isoformat() if stats.get('joined_at') else None
        }
        
        return jsonify({
            'success': True,
            'statistics': formatted_stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"获取用户统计API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取统计信息失败'
        }), 500


@user_bp.route('/account', methods=['DELETE'])
@login_required
def delete_account():
    """删除用户账户"""
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': '请提供当前密码以确认删除'
            }), 400
        
        password = data['password']
        
        success, message = UserService.delete_user_account(current_user.id, password)
        
        return jsonify({
            'success': success,
            'message': message
        }), 200 if success else 400
        
    except Exception as e:
        current_app.logger.error(f"删除账户API错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '删除账户失败，请稍后重试'
        }), 500