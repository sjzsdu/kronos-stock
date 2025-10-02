# -*- coding: utf-8 -*-
"""
优化的用户服务层
集成缓存策略，提升用户数据查询性能
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash, check_password_hash

from app.models import db
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.watchlist import Watchlist
from app.models.prediction_history import PredictionHistory
from app.services.user_cache_service import user_cache_service


class OptimizedUserService:
    """优化的用户服务类，集成缓存策略"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    # ===== 用户基础操作（带缓存） =====
    
    def get_user_by_id(self, user_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        根据ID获取用户信息（优先使用缓存）
        
        Args:
            user_id: 用户ID
            use_cache: 是否使用缓存
            
        Returns:
            用户信息字典或None
        """
        try:
            # 尝试从缓存获取
            if use_cache:
                cached_user = user_cache_service.get_cached_user_info(user_id)
                if cached_user:
                    self.logger.debug(f"从缓存获取用户信息: user_id={user_id}")
                    return cached_user
            
            # 从数据库查询
            user = User.query.get(user_id)
            if not user:
                return None
            
            user_data = self._user_to_dict(user)
            
            # 缓存用户信息
            if use_cache:
                cache_ttl = current_app.config.get('USER_CACHE_TTL', 300)
                user_cache_service.cache_user_info(user_id, user_data, cache_ttl)
                self.logger.debug(f"用户信息已缓存: user_id={user_id}")
            
            return user_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"数据库查询用户失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str, use_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        根据用户名获取用户信息
        
        Args:
            username: 用户名
            use_cache: 是否使用缓存（用户名查询通常不缓存）
            
        Returns:
            用户信息字典或None
        """
        try:
            user = User.query.filter_by(username=username).first()
            if not user:
                return None
            
            user_data = self._user_to_dict(user)
            
            # 可选择性缓存
            if use_cache:
                cache_ttl = current_app.config.get('USER_CACHE_TTL', 300)
                user_cache_service.cache_user_info(user.id, user_data, cache_ttl)
            
            return user_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"根据用户名查询用户失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str, use_cache: bool = False) -> Optional[Dict[str, Any]]:
        """
        根据邮箱获取用户信息
        
        Args:
            email: 邮箱地址
            use_cache: 是否使用缓存
            
        Returns:
            用户信息字典或None
        """
        try:
            user = User.query.filter_by(email=email).first()
            if not user:
                return None
            
            user_data = self._user_to_dict(user)
            
            if use_cache:
                cache_ttl = current_app.config.get('USER_CACHE_TTL', 300)
                user_cache_service.cache_user_info(user.id, user_data, cache_ttl)
            
            return user_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"根据邮箱查询用户失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"获取用户信息失败: {str(e)}")
            return None
    
    # ===== 用户档案操作（带缓存） =====
    
    def get_user_profile(self, user_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        获取用户档案信息（优先使用缓存）
        
        Args:
            user_id: 用户ID
            use_cache: 是否使用缓存
            
        Returns:
            用户档案字典或None
        """
        try:
            # 尝试从缓存获取
            if use_cache:
                cached_profile = user_cache_service.get_cached_user_profile(user_id)
                if cached_profile:
                    self.logger.debug(f"从缓存获取用户档案: user_id={user_id}")
                    return cached_profile
            
            # 从数据库查询
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            
            if profile:
                profile_data = self._profile_to_dict(profile)
            else:
                # 创建默认档案
                profile_data = self._create_default_profile(user_id)
            
            # 缓存用户档案
            if use_cache and profile_data:
                cache_ttl = current_app.config.get('USER_PROFILE_CACHE_TTL', 1800)
                user_cache_service.cache_user_profile(user_id, profile_data, cache_ttl)
                self.logger.debug(f"用户档案已缓存: user_id={user_id}")
            
            return profile_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"数据库查询用户档案失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"获取用户档案失败: {str(e)}")
            return None
    
    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> bool:
        """
        更新用户档案信息
        
        Args:
            user_id: 用户ID
            profile_data: 档案数据
            
        Returns:
            是否更新成功
        """
        try:
            profile = UserProfile.query.filter_by(user_id=user_id).first()
            
            if not profile:
                # 创建新档案
                profile = UserProfile(user_id=user_id)
                db.session.add(profile)
            
            # 更新档案字段
            updatable_fields = [
                'real_name', 'phone', 'gender', 'birth_date', 'location',
                'bio', 'investment_experience', 'risk_tolerance', 'investment_goal'
            ]
            
            for field in updatable_fields:
                if field in profile_data:
                    setattr(profile, field, profile_data[field])
            
            profile.updated_at = datetime.now(timezone.utc)
            
            db.session.commit()
            
            # 更新缓存
            updated_profile_data = self._profile_to_dict(profile)
            cache_ttl = current_app.config.get('USER_PROFILE_CACHE_TTL', 1800)
            user_cache_service.cache_user_profile(user_id, updated_profile_data, cache_ttl)
            
            self.logger.info(f"用户档案已更新: user_id={user_id}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"数据库更新用户档案失败: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"更新用户档案失败: {str(e)}")
            return False
    
    # ===== 用户关注列表操作（带缓存） =====
    
    def get_user_watchlist(self, user_id: int, use_cache: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        获取用户关注列表（优先使用缓存）
        
        Args:
            user_id: 用户ID
            use_cache: 是否使用缓存
            
        Returns:
            关注列表或None
        """
        try:
            # 尝试从缓存获取
            if use_cache:
                cached_watchlist = user_cache_service.get_cached_user_watchlist(user_id)
                if cached_watchlist:
                    self.logger.debug(f"从缓存获取用户关注列表: user_id={user_id}")
                    return cached_watchlist.get('watchlist', [])
            
            # 从数据库查询
            watchlist_items = Watchlist.query.filter_by(user_id=user_id).order_by(
                Watchlist.created_at.desc()
            ).all()
            
            watchlist_data = [self._watchlist_item_to_dict(item) for item in watchlist_items]
            
            # 缓存关注列表
            if use_cache:
                cache_ttl = current_app.config.get('USER_CACHE_TTL', 300)
                user_cache_service.cache_user_watchlist(user_id, watchlist_data, cache_ttl)
                self.logger.debug(f"用户关注列表已缓存: user_id={user_id}, count={len(watchlist_data)}")
            
            return watchlist_data
            
        except SQLAlchemyError as e:
            self.logger.error(f"数据库查询用户关注列表失败: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"获取用户关注列表失败: {str(e)}")
            return None
    
    def add_to_watchlist(self, user_id: int, stock_code: str, stock_name: str = None) -> bool:
        """
        添加股票到关注列表
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            stock_name: 股票名称（可选）
            
        Returns:
            是否添加成功
        """
        try:
            # 检查是否已存在
            existing = Watchlist.query.filter_by(
                user_id=user_id,
                stock_code=stock_code
            ).first()
            
            if existing:
                self.logger.info(f"股票已在关注列表中: user_id={user_id}, stock_code={stock_code}")
                return True
            
            # 创建新的关注项
            watchlist_item = Watchlist(
                user_id=user_id,
                stock_code=stock_code,
                stock_name=stock_name or stock_code,
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(watchlist_item)
            db.session.commit()
            
            # 清除缓存，下次查询时会重新加载
            user_cache_service.invalidate_user_watchlist(user_id)
            
            self.logger.info(f"股票已添加到关注列表: user_id={user_id}, stock_code={stock_code}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"数据库添加关注列表失败: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"添加关注列表失败: {str(e)}")
            return False
    
    def remove_from_watchlist(self, user_id: int, stock_code: str) -> bool:
        """
        从关注列表移除股票
        
        Args:
            user_id: 用户ID
            stock_code: 股票代码
            
        Returns:
            是否移除成功
        """
        try:
            watchlist_item = Watchlist.query.filter_by(
                user_id=user_id,
                stock_code=stock_code
            ).first()
            
            if not watchlist_item:
                self.logger.info(f"关注列表中不存在该股票: user_id={user_id}, stock_code={stock_code}")
                return True
            
            db.session.delete(watchlist_item)
            db.session.commit()
            
            # 清除缓存
            user_cache_service.invalidate_user_watchlist(user_id)
            
            self.logger.info(f"股票已从关注列表移除: user_id={user_id}, stock_code={stock_code}")
            return True
            
        except SQLAlchemyError as e:
            db.session.rollback()
            self.logger.error(f"数据库移除关注列表失败: {str(e)}")
            return False
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"移除关注列表失败: {str(e)}")
            return False
    
    # ===== 用户预测历史操作 =====
    
    def get_user_prediction_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """
        获取用户预测历史记录
        
        Args:
            user_id: 用户ID
            limit: 返回记录数限制
            
        Returns:
            预测历史列表
        """
        try:
            predictions = PredictionHistory.query.filter_by(user_id=user_id).order_by(
                PredictionHistory.created_at.desc()
            ).limit(limit).all()
            
            return [self._prediction_to_dict(pred) for pred in predictions]
            
        except SQLAlchemyError as e:
            self.logger.error(f"数据库查询用户预测历史失败: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"获取用户预测历史失败: {str(e)}")
            return []
    
    # ===== 缓存管理操作 =====
    
    def invalidate_user_cache(self, user_id: int):
        """使指定用户的所有缓存失效"""
        try:
            user_cache_service.invalidate_user_all_cache(user_id)
            self.logger.info(f"用户缓存已失效: user_id={user_id}")
        except Exception as e:
            self.logger.error(f"用户缓存失效失败: {str(e)}")
    
    def refresh_user_cache(self, user_id: int):
        """刷新用户缓存"""
        try:
            # 清除旧缓存
            self.invalidate_user_cache(user_id)
            
            # 预加载用户数据到缓存
            self.get_user_by_id(user_id, use_cache=True)
            self.get_user_profile(user_id, use_cache=True)
            self.get_user_watchlist(user_id, use_cache=True)
            
            self.logger.info(f"用户缓存已刷新: user_id={user_id}")
            
        except Exception as e:
            self.logger.error(f"刷新用户缓存失败: {str(e)}")
    
    # ===== 辅助方法 =====
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """将用户对象转换为字典"""
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'nickname': user.nickname,
            'avatar_url': user.avatar_url,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'last_login_at': user.last_login_at.isoformat() if user.last_login_at else None,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }
    
    def _profile_to_dict(self, profile: UserProfile) -> Dict[str, Any]:
        """将用户档案对象转换为字典"""
        return {
            'id': profile.id,
            'user_id': profile.user_id,
            'real_name': profile.real_name,
            'phone': profile.phone,
            'gender': profile.gender,
            'birth_date': profile.birth_date.isoformat() if profile.birth_date else None,
            'location': profile.location,
            'bio': profile.bio,
            'investment_experience': profile.investment_experience,
            'risk_tolerance': profile.risk_tolerance,
            'investment_goal': profile.investment_goal,
            'created_at': profile.created_at.isoformat() if profile.created_at else None,
            'updated_at': profile.updated_at.isoformat() if profile.updated_at else None
        }
    
    def _create_default_profile(self, user_id: int) -> Dict[str, Any]:
        """创建默认用户档案"""
        try:
            profile = UserProfile(
                user_id=user_id,
                investment_experience='新手',
                risk_tolerance='保守',
                investment_goal='稳健增值',
                created_at=datetime.now(timezone.utc)
            )
            
            db.session.add(profile)
            db.session.commit()
            
            return self._profile_to_dict(profile)
            
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"创建默认用户档案失败: {str(e)}")
            return {
                'user_id': user_id,
                'investment_experience': '新手',
                'risk_tolerance': '保守',
                'investment_goal': '稳健增值'
            }
    
    def _watchlist_item_to_dict(self, item: Watchlist) -> Dict[str, Any]:
        """将关注列表项转换为字典"""
        return {
            'id': item.id,
            'user_id': item.user_id,
            'stock_code': item.stock_code,
            'stock_name': item.stock_name,
            'created_at': item.created_at.isoformat() if item.created_at else None
        }
    
    def _prediction_to_dict(self, prediction: PredictionHistory) -> Dict[str, Any]:
        """将预测历史对象转换为字典"""
        return {
            'id': prediction.id,
            'user_id': prediction.user_id,
            'stock_code': prediction.stock_code,
            'stock_name': prediction.stock_name,
            'model_name': prediction.model_name,
            'prediction_result': prediction.prediction_result,
            'accuracy': prediction.accuracy,
            'created_at': prediction.created_at.isoformat() if prediction.created_at else None
        }


# 创建全局用户服务实例
optimized_user_service = OptimizedUserService()