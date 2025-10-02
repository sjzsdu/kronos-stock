# -*- coding: utf-8 -*-
"""
数据库索引优化迁移
为用户系统相关表添加性能优化索引

Revision ID: user_indexes_optimization
Revises: 
Create Date: 2025-10-02 14:30:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite, mysql


# revision identifiers
revision = 'user_indexes_optimization'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """
    添加用户系统性能优化索引
    """
    
    # 1. 用户表索引优化
    # email字段已经在模型中设置了index=True，这里添加额外的复合索引
    
    # 用户活跃状态和角色查询优化
    op.create_index('idx_users_active_role', 'users', ['is_active', 'role'])
    
    # 邮箱验证状态查询优化
    op.create_index('idx_users_email_verified', 'users', ['email_verified'])
    
    # 用户创建时间查询优化（用于统计和分析）
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # 最后登录时间查询优化
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    
    
    # 2. 用户会话表索引优化
    # token字段已经在模型中设置了index=True
    
    # 会话活跃状态和过期时间复合查询优化
    op.create_index('idx_user_sessions_active_expires', 'user_sessions', 
                   ['is_active', 'expires_at'])
    
    # 用户ID和活跃状态复合查询优化（清理用户会话时使用）
    op.create_index('idx_user_sessions_user_active', 'user_sessions', 
                   ['user_id', 'is_active'])
    
    # 最后活动时间查询优化（用于清理过期会话）
    op.create_index('idx_user_sessions_last_activity', 'user_sessions', 
                   ['last_activity'])
    
    # IP地址查询优化（安全监控）
    op.create_index('idx_user_sessions_ip', 'user_sessions', ['ip_address'])
    
    
    # 3. 用户预测记录索引优化
    
    # 用户ID和股票代码复合查询优化（用户查看特定股票的预测历史）
    op.create_index('idx_user_predictions_user_stock', 'user_predictions', 
                   ['user_id', 'stock_code'])
    
    # 用户ID和创建时间复合查询优化（按时间排序的预测列表）
    op.create_index('idx_user_predictions_user_created', 'user_predictions', 
                   ['user_id', 'created_at'])
    
    # 股票代码和创建时间复合查询优化（特定股票的预测历史）
    op.create_index('idx_user_predictions_stock_created', 'user_predictions', 
                   ['stock_code', 'created_at'])
    
    # 模型类型查询优化（按模型统计预测）
    op.create_index('idx_user_predictions_model_type', 'user_predictions', 
                   ['model_type'])
    
    # 预测类型查询优化
    op.create_index('idx_user_predictions_prediction_type', 'user_predictions', 
                   ['prediction_type'])
    
    # 收藏状态查询优化（用户查看收藏的预测）
    op.create_index('idx_user_predictions_favorite', 'user_predictions', 
                   ['user_id', 'is_favorite'])
    
    
    # 4. 关注列表索引优化
    
    # 用户ID和激活状态复合查询优化（用户的活跃关注列表）
    op.create_index('idx_watchlists_user_active', 'watchlists', 
                   ['user_id', 'is_active'])
    
    # 用户ID和排序复合查询优化（按用户自定义顺序显示）
    op.create_index('idx_watchlists_user_sort', 'watchlists', 
                   ['user_id', 'sort_order'])
    
    # 股票代码查询优化（统计关注某股票的用户数量）
    op.create_index('idx_watchlists_stock_code', 'watchlists', ['stock_code'])
    
    # 更新时间查询优化（最近更新的关注列表）
    op.create_index('idx_watchlists_updated_at', 'watchlists', ['updated_at'])
    
    
    # 5. 用户档案索引优化
    
    # 订阅层级查询优化（查找高级用户）
    op.create_index('idx_user_profiles_subscription', 'user_profiles', 
                   ['subscription_tier'])
    
    # 订阅过期时间查询优化（清理过期订阅）
    op.create_index('idx_user_profiles_subscription_expires', 'user_profiles', 
                   ['subscription_expires'])
    
    # 投资经验查询优化（用户分析）
    op.create_index('idx_user_profiles_experience', 'user_profiles', 
                   ['investment_experience'])
    
    # 风险偏好查询优化（用户分析）
    op.create_index('idx_user_profiles_risk_preference', 'user_profiles', 
                   ['risk_preference'])
    
    
    # 6. 密码重置令牌索引优化
    # token字段已经在模型中设置了index=True
    
    # 过期时间和使用状态复合查询优化
    op.create_index('idx_password_reset_expires_used', 'password_reset_tokens', 
                   ['expires_at', 'is_used'])
    
    # 用户ID和使用状态复合查询优化
    op.create_index('idx_password_reset_user_used', 'password_reset_tokens', 
                   ['user_id', 'is_used'])
    
    
    # 7. 邮箱验证令牌索引优化
    # token字段已经在模型中设置了index=True
    
    # 过期时间和验证状态复合查询优化
    op.create_index('idx_email_verification_expires_verified', 'email_verifications', 
                   ['expires_at', 'is_verified'])
    
    # 用户ID和验证状态复合查询优化
    op.create_index('idx_email_verification_user_verified', 'email_verifications', 
                   ['user_id', 'is_verified'])
    
    
    # 8. 全文搜索索引（如果数据库支持）
    # 这部分需要根据实际使用的数据库引擎来决定
    
    # MySQL全文索引示例（生产环境如果使用MySQL）
    # op.execute("ALTER TABLE user_profiles ADD FULLTEXT(nickname, bio)")
    
    # SQLite FTS表示例（开发环境）
    # 这里暂时跳过，因为需要额外的FTS配置


def downgrade():
    """
    删除性能优化索引
    """
    
    # 删除邮箱验证令牌索引
    op.drop_index('idx_email_verification_user_verified', 'email_verifications')
    op.drop_index('idx_email_verification_expires_verified', 'email_verifications')
    
    # 删除密码重置令牌索引
    op.drop_index('idx_password_reset_user_used', 'password_reset_tokens')
    op.drop_index('idx_password_reset_expires_used', 'password_reset_tokens')
    
    # 删除用户档案索引
    op.drop_index('idx_user_profiles_risk_preference', 'user_profiles')
    op.drop_index('idx_user_profiles_experience', 'user_profiles')
    op.drop_index('idx_user_profiles_subscription_expires', 'user_profiles')
    op.drop_index('idx_user_profiles_subscription', 'user_profiles')
    
    # 删除关注列表索引
    op.drop_index('idx_watchlists_updated_at', 'watchlists')
    op.drop_index('idx_watchlists_stock_code', 'watchlists')
    op.drop_index('idx_watchlists_user_sort', 'watchlists')
    op.drop_index('idx_watchlists_user_active', 'watchlists')
    
    # 删除用户预测索引
    op.drop_index('idx_user_predictions_favorite', 'user_predictions')
    op.drop_index('idx_user_predictions_prediction_type', 'user_predictions')
    op.drop_index('idx_user_predictions_model_type', 'user_predictions')
    op.drop_index('idx_user_predictions_stock_created', 'user_predictions')
    op.drop_index('idx_user_predictions_user_created', 'user_predictions')
    op.drop_index('idx_user_predictions_user_stock', 'user_predictions')
    
    # 删除用户会话索引
    op.drop_index('idx_user_sessions_ip', 'user_sessions')
    op.drop_index('idx_user_sessions_last_activity', 'user_sessions')
    op.drop_index('idx_user_sessions_user_active', 'user_sessions')
    op.drop_index('idx_user_sessions_active_expires', 'user_sessions')
    
    # 删除用户表索引
    op.drop_index('idx_users_last_login', 'users')
    op.drop_index('idx_users_created_at', 'users')
    op.drop_index('idx_users_email_verified', 'users')
    op.drop_index('idx_users_active_role', 'users')