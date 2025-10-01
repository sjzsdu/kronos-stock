# -*- coding: utf-8 -*-
"""
用户管理服务
处理用户信息更新、档案管理、设置等功能
"""

from datetime import datetime, timezone
from typing import Optional, Dict, List, Any, Tuple

from flask import current_app

from app.models import db
from app.models.user import User, UserProfile, UserPrediction, Watchlist


class UserService:
    """用户管理服务类"""
    
    @staticmethod
    def get_user_profile(user_id: int) -> Optional[UserProfile]:
        """
        获取用户档案
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户档案对象或None
        """
        return UserProfile.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def update_user_profile(user_id: int, profile_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新用户档案
        
        Args:
            user_id: 用户ID
            profile_data: 档案数据
            
        Returns:
            (成功标志, 消息)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            # 更新用户基本信息
            if 'full_name' in profile_data:
                user.full_name = profile_data['full_name'].strip()
            
            # 获取或创建用户档案
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not profile:
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
            
            # 更新档案信息
            allowed_fields = [
                'nickname', 'phone', 'avatar_url', 'bio', 'location',
                'birth_date', 'gender', 'investment_experience', 'risk_preference',
                'investment_style', 'risk_tolerance'
            ]
            
            for field in allowed_fields:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            
            # 更新偏好设置
            if 'preferences' in profile_data:
                current_prefs = profile.get_preferences()
                current_prefs.update(profile_data['preferences'])
                profile.set_preferences(current_prefs)
            
            # 更新通知设置
            if 'notification_settings' in profile_data:
                current_alerts = profile.get_notification_settings()
                current_alerts.update(profile_data['notification_settings'])
                profile.set_notification_settings(current_alerts)
            
            # 更新偏好行业
            if 'preferred_sectors' in profile_data:
                profile.set_preferred_sectors(profile_data['preferred_sectors'])
            
            # 更新通知偏好设置
            if 'notification_preferences' in profile_data:
                current_notif_prefs = profile.get_notification_preferences()
                current_notif_prefs.update(profile_data['notification_preferences'])
                profile.set_notification_preferences(current_notif_prefs)
            
            user.updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            return True, "档案更新成功"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新用户档案失败: {str(e)}")
            return False, "档案更新失败，请稍后重试"
    
    @staticmethod
    def get_user_predictions(user_id: int, limit: int = 20, offset: int = 0) -> List[UserPrediction]:
        """
        获取用户预测记录
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            预测记录列表
        """
        return UserPrediction.query.filter_by(user_id=user_id)\
            .order_by(UserPrediction.created_at.desc())\
            .limit(limit).offset(offset).all()
    
    @staticmethod
    def create_prediction_record(user_id: int, stock_code: str, prediction_data: Dict[str, Any]) -> Optional[UserPrediction]:
        """
        创建预测记录
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            prediction_data: 预测数据
            
        Returns:
            预测记录对象或None
        """
        try:
            prediction = UserPrediction(
                user_id=user_id,
                stock_code=stock_code,
                model_type=prediction_data.get('model_type', 'kronos-mini'),
                prediction_type=prediction_data.get('prediction_type', 'price'),
                prediction_result=prediction_data.get('result', {}),
                metadata=prediction_data.get('metadata', {})
            )
            
            db.session.add(prediction)
            db.session.commit()
            
            return prediction
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建预测记录失败: {str(e)}")
            return None
    
    @staticmethod
    def get_user_watchlist(user_id: int) -> List[Watchlist]:
        """
        获取用户关注股票列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            关注列表
        """
        return Watchlist.query.filter_by(user_id=user_id)\
            .filter_by(is_active=True)\
            .order_by(Watchlist.sort_order.asc()).all()
    
    @staticmethod
    def add_to_watchlist(user_id: int, stock_code: str, stock_name: str = '', notes: str = '') -> Tuple[bool, str]:
        """
        添加股票到关注列表
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            stock_name: 股票名称
            notes: 备注
            
        Returns:
            (成功标志, 消息)
        """
        try:
            # 检查是否已存在
            existing = Watchlist.query.filter_by(
                user_id=user_id,
                stock_code=stock_code,
                is_active=True
            ).first()
            
            if existing:
                return False, "该股票已在关注列表中"
            
            # 获取下一个排序位置
            max_order = db.session.query(db.func.max(Watchlist.sort_order))\
                .filter_by(user_id=user_id, is_active=True).scalar() or 0
            
            watchlist_item = Watchlist(
                user_id=user_id,
                stock_code=stock_code,
                stock_name=stock_name,
                notes=notes,
                sort_order=max_order + 1
            )
            
            db.session.add(watchlist_item)
            db.session.commit()
            
            return True, "已添加到关注列表"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"添加关注股票失败: {str(e)}")
            return False, "添加失败，请稍后重试"
    
    @staticmethod
    def remove_from_watchlist(user_id: int, stock_code: str) -> Tuple[bool, str]:
        """
        从关注列表移除股票
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            
        Returns:
            (成功标志, 消息)
        """
        try:
            watchlist_item = Watchlist.query.filter_by(
                user_id=user_id,
                stock_code=stock_code,
                is_active=True
            ).first()
            
            if not watchlist_item:
                return False, "股票不在关注列表中"
            
            # 软删除
            watchlist_item.is_active = False
            watchlist_item.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return True, "已从关注列表移除"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"移除关注股票失败: {str(e)}")
            return False, "移除失败，请稍后重试"
    
    @staticmethod
    def update_watchlist_order(user_id: int, stock_codes: List[str]) -> Tuple[bool, str]:
        """
        更新关注列表排序
        
        Args:
            user_id: 用户ID
            stock_codes: 排序后的股票代码列表
            
        Returns:
            (成功标志, 消息)
        """
        try:
            for index, stock_code in enumerate(stock_codes, 1):
                watchlist_item = Watchlist.query.filter_by(
                    user_id=user_id,
                    stock_code=stock_code,
                    is_active=True
                ).first()
                
                if watchlist_item:
                    watchlist_item.sort_order = index
                    watchlist_item.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            return True, "排序更新成功"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新关注列表排序失败: {str(e)}")
            return False, "排序更新失败，请稍后重试"
    
    @staticmethod
    def get_user_statistics(user_id: int) -> Dict[str, Any]:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            统计信息字典
        """
        try:
            # 预测总数
            total_predictions = UserPrediction.query.filter_by(user_id=user_id).count()
            
            # 本月预测数
            from sqlalchemy import func, extract
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            monthly_predictions = UserPrediction.query.filter(
                UserPrediction.user_id == user_id,
                extract('month', UserPrediction.created_at) == current_month,
                extract('year', UserPrediction.created_at) == current_year
            ).count()
            
            # 关注股票数
            watchlist_count = Watchlist.query.filter_by(
                user_id=user_id,
                is_active=True
            ).count()
            
            # 最近预测时间
            last_prediction = UserPrediction.query.filter_by(user_id=user_id)\
                .order_by(UserPrediction.created_at.desc()).first()
            
            # 常用模型统计
            model_stats = db.session.query(
                UserPrediction.model_type,
                func.count(UserPrediction.id).label('count')
            ).filter_by(user_id=user_id)\
            .group_by(UserPrediction.model_type)\
            .order_by(func.count(UserPrediction.id).desc()).all()
            
            return {
                'total_predictions': total_predictions,
                'monthly_predictions': monthly_predictions,
                'watchlist_count': watchlist_count,
                'last_prediction_at': last_prediction.created_at if last_prediction else None,
                'favorite_models': [{'model': stat[0], 'count': stat[1]} for stat in model_stats[:3]],
                'joined_at': User.query.get(user_id).created_at
            }
            
        except Exception as e:
            current_app.logger.error(f"获取用户统计信息失败: {str(e)}")
            return {}
    
    @staticmethod
    def delete_user_account(user_id: int, password: str) -> Tuple[bool, str]:
        """
        删除用户账户（软删除）
        
        Args:
            user_id: 用户ID
            password: 确认密码
            
        Returns:
            (成功标志, 消息)
        """
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "用户不存在"
            
            # 验证密码
            if not user.check_password(password):
                return False, "密码错误"
            
            # 软删除用户
            user.is_active = False
            user.updated_at = datetime.now(timezone.utc)
            
            # 清理相关数据
            # 删除所有会话
            from app.models.user import UserSession
            UserSession.query.filter_by(user_id=user_id).delete()
            
            # 软删除关注列表
            Watchlist.query.filter_by(user_id=user_id).update({'is_active': False})
            
            db.session.commit()
            
            return True, "账户已删除"
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除用户账户失败: {str(e)}")
            return False, "删除失败，请稍后重试"