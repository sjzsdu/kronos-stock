# -*- coding: utf-8 -*-
"""
用户模型
定义用户、用户档案、会话等数据模型
"""

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import json

from app import db

class User(UserMixin, db.Model):
    """用户基础模型"""
    __tablename__ = 'users'
    
    # 主键和基本信息
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    
    # 用户状态和角色
    role = db.Column(db.String(20), default='user', nullable=False)  # user, premium, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    email_verified = db.Column(db.Boolean, default=False, nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_login = db.Column(db.DateTime)
    
    # 关联关系
    profile = db.relationship('UserProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    sessions = db.relationship('UserSession', backref='user', cascade='all, delete-orphan')
    predictions = db.relationship('UserPrediction', backref='user', cascade='all, delete-orphan')
    watchlist = db.relationship('Watchlist', backref='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码哈希"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Flask-Login 要求的方法"""
        return str(self.id)
    
    def has_role(self, role):
        """检查用户是否有指定角色"""
        if role == 'admin':
            return self.role == 'admin'
        elif role == 'premium':
            return self.role in ['premium', 'admin']
        else:
            return True  # 所有用户都有基础权限
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class UserProfile(db.Model):
    """用户档案扩展信息"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 个人信息
    phone = db.Column(db.String(20))
    timezone = db.Column(db.String(50), default='Asia/Shanghai')
    
    # 偏好设置 (JSON 格式)
    notification_preferences = db.Column(db.Text, default='{}')
    
    # 订阅信息
    subscription_tier = db.Column(db.String(20), default='free')  # free, premium, enterprise
    subscription_expires = db.Column(db.DateTime)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def get_notification_preferences(self):
        """获取通知偏好设置"""
        try:
            return json.loads(self.notification_preferences or '{}')
        except:
            return {}
    
    def set_notification_preferences(self, preferences):
        """设置通知偏好"""
        self.notification_preferences = json.dumps(preferences)
    
    def is_premium(self):
        """检查是否为高级用户"""
        if self.subscription_tier in ['premium', 'enterprise']:
            if self.subscription_expires:
                return datetime.now(timezone.utc) < self.subscription_expires.replace(tzinfo=timezone.utc)
            return True
        return False
    
    def __repr__(self):
        return f'<UserProfile {self.user_id}>'


class UserSession(db.Model):
    """用户会话管理"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.String(255), primary_key=True)  # 会话ID
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 会话信息
    session_token = db.Column(db.String(255), nullable=False, index=True)
    ip_address = db.Column(db.String(45))  # 支持 IPv6
    user_agent = db.Column(db.Text)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def is_expired(self):
        """检查会话是否过期"""
        return datetime.now(timezone.utc) > self.expires_at.replace(tzinfo=timezone.utc)
    
    def __repr__(self):
        return f'<UserSession {self.id} for user {self.user_id}>'


class UserPrediction(db.Model):
    """用户预测关联"""
    __tablename__ = 'user_predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 关联到预测系统
    prediction_id = db.Column(db.String(100), nullable=False)  # 关联现有预测系统
    stock_code = db.Column(db.String(10), nullable=False)
    
    # 用户标记
    is_favorite = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)  # 用户笔记
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<UserPrediction {self.prediction_id} by user {self.user_id}>'


class Watchlist(db.Model):
    """用户股票关注列表"""
    __tablename__ = 'watchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 股票信息
    stock_code = db.Column(db.String(10), nullable=False)
    stock_name = db.Column(db.String(100))
    
    # 提醒设置 (JSON 格式)
    alert_thresholds = db.Column(db.Text, default='{}')
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # 唯一约束：用户不能重复添加同一股票
    __table_args__ = (db.UniqueConstraint('user_id', 'stock_code', name='unique_user_stock'),)
    
    def get_alert_thresholds(self):
        """获取提醒阈值"""
        try:
            return json.loads(self.alert_thresholds or '{}')
        except:
            return {}
    
    def set_alert_thresholds(self, thresholds):
        """设置提醒阈值"""
        self.alert_thresholds = json.dumps(thresholds)
    
    def __repr__(self):
        return f'<Watchlist {self.stock_code} for user {self.user_id}>'