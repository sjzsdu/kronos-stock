# -*- coding: utf-8 -*-
"""
用户服务单元测试
测试用户管理服务的各种功能
"""

import pytest
import unittest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.user_service import UserService
from app.models.user import User


class TestUserService(unittest.TestCase):
    """用户服务测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.user_service = UserService()
        self.mock_user_data = {
            'id': 1,
            'username': 'test_user',
            'email': 'test@example.com',
            'nickname': '测试用户',
            'password_hash': 'hashed_password',
            'is_active': True,
            'is_admin': False,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    
    @patch('app.services.user_service.User')
    def test_create_user_success(self, mock_user_class):
        """测试成功创建用户"""
        # 设置mock
        mock_user_instance = Mock()
        mock_user_class.return_value = mock_user_instance
        mock_user_class.query.filter_by.return_value.first.return_value = None  # 用户不存在
        
        with patch('app.services.user_service.db.session') as mock_session:
            # 执行测试
            result = self.user_service.create_user(
                username='test_user',
                email='test@example.com',
                password='password123',
                nickname='测试用户'
            )
            
            # 验证结果
            self.assertTrue(result['success'])
            self.assertIn('用户创建成功', result['message'])
            mock_session.add.assert_called_once_with(mock_user_instance)
            mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.User')
    def test_create_user_duplicate_username(self, mock_user_class):
        """测试创建重复用户名的用户"""
        # 设置mock - 用户名已存在
        existing_user = Mock()
        mock_user_class.query.filter_by.return_value.first.return_value = existing_user
        
        # 执行测试
        result = self.user_service.create_user(
            username='existing_user',
            email='test@example.com',
            password='password123'
        )
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户名已存在', result['message'])
    
    @patch('app.services.user_service.User')
    def test_create_user_duplicate_email(self, mock_user_class):
        """测试创建重复邮箱的用户"""
        # 设置mock - 邮箱已存在
        def mock_filter_by(**kwargs):
            mock_query = Mock()
            if 'email' in kwargs:
                mock_query.first.return_value = Mock()  # 邮箱存在
            else:
                mock_query.first.return_value = None  # 用户名不存在
            return mock_query
        
        mock_user_class.query.filter_by.side_effect = mock_filter_by
        
        # 执行测试
        result = self.user_service.create_user(
            username='new_user',
            email='existing@example.com',
            password='password123'
        )
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('邮箱已被注册', result['message'])
    
    @patch('app.services.user_service.User')
    def test_authenticate_user_success(self, mock_user_class):
        """测试用户认证成功"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'test_user'
        mock_user.is_active = True
        mock_user.check_password.return_value = True
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        # 执行测试
        result = self.user_service.authenticate_user('test_user', 'correct_password')
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], mock_user)
        self.assertIn('认证成功', result['message'])
    
    @patch('app.services.user_service.User')
    def test_authenticate_user_not_found(self, mock_user_class):
        """测试用户认证 - 用户不存在"""
        # 设置mock - 用户不存在
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        # 执行测试
        result = self.user_service.authenticate_user('nonexistent_user', 'password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户名或密码错误', result['message'])
    
    @patch('app.services.user_service.User')
    def test_authenticate_user_wrong_password(self, mock_user_class):
        """测试用户认证 - 密码错误"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.is_active = True
        mock_user.check_password.return_value = False
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        # 执行测试
        result = self.user_service.authenticate_user('test_user', 'wrong_password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户名或密码错误', result['message'])
    
    @patch('app.services.user_service.User')
    def test_authenticate_user_inactive(self, mock_user_class):
        """测试用户认证 - 用户已禁用"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.is_active = False
        mock_user.check_password.return_value = True
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        
        # 执行测试
        result = self.user_service.authenticate_user('test_user', 'correct_password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户账户已被禁用', result['message'])
    
    @patch('app.services.user_service.User')
    def test_get_user_by_id_success(self, mock_user_class):
        """测试根据ID获取用户成功"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = 'test_user'
        mock_user_class.query.get.return_value = mock_user
        
        # 执行测试
        result = self.user_service.get_user_by_id(1)
        
        # 验证结果
        self.assertEqual(result, mock_user)
        mock_user_class.query.get.assert_called_once_with(1)
    
    @patch('app.services.user_service.User')
    def test_get_user_by_id_not_found(self, mock_user_class):
        """测试根据ID获取用户 - 用户不存在"""
        # 设置mock - 用户不存在
        mock_user_class.query.get.return_value = None
        
        # 执行测试
        result = self.user_service.get_user_by_id(999)
        
        # 验证结果
        self.assertIsNone(result)
        mock_user_class.query.get.assert_called_once_with(999)
    
    @patch('app.services.user_service.User')
    def test_update_user_profile_success(self, mock_user_class):
        """测试更新用户资料成功"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user_class.query.get.return_value = mock_user
        
        with patch('app.services.user_service.db.session') as mock_session:
            # 执行测试
            update_data = {
                'nickname': '新昵称',
                'email': 'new@example.com'
            }
            result = self.user_service.update_user_profile(1, update_data)
            
            # 验证结果
            self.assertTrue(result['success'])
            self.assertIn('用户资料更新成功', result['message'])
            self.assertEqual(mock_user.nickname, '新昵称')
            self.assertEqual(mock_user.email, 'new@example.com')
            mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.User')
    def test_update_user_profile_not_found(self, mock_user_class):
        """测试更新用户资料 - 用户不存在"""
        # 设置mock - 用户不存在
        mock_user_class.query.get.return_value = None
        
        # 执行测试
        result = self.user_service.update_user_profile(999, {'nickname': '新昵称'})
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户不存在', result['message'])
    
    @patch('app.services.user_service.User')
    def test_deactivate_user_success(self, mock_user_class):
        """测试禁用用户成功"""
        # 设置mock用户
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user_class.query.get.return_value = mock_user
        
        with patch('app.services.user_service.db.session') as mock_session:
            # 执行测试
            result = self.user_service.deactivate_user(1)
            
            # 验证结果
            self.assertTrue(result['success'])
            self.assertIn('用户已禁用', result['message'])
            self.assertFalse(mock_user.is_active)
            mock_session.commit.assert_called_once()
    
    @patch('app.services.user_service.User')
    def test_deactivate_user_not_found(self, mock_user_class):
        """测试禁用用户 - 用户不存在"""
        # 设置mock - 用户不存在
        mock_user_class.query.get.return_value = None
        
        # 执行测试
        result = self.user_service.deactivate_user(999)
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户不存在', result['message'])
    
    @patch('app.services.user_service.User')
    def test_get_user_list_success(self, mock_user_class):
        """测试获取用户列表成功"""
        # 设置mock用户列表
        mock_users = [Mock(), Mock(), Mock()]
        mock_query = Mock()
        mock_query.limit.return_value.offset.return_value.all.return_value = mock_users
        mock_user_class.query.filter_by.return_value = mock_query
        
        # 执行测试
        result = self.user_service.get_user_list(page=1, per_page=10, is_active=True)
        
        # 验证结果
        self.assertEqual(len(result), 3)
        mock_user_class.query.filter_by.assert_called_once_with(is_active=True)
    
    def test_validate_user_data_success(self):
        """测试用户数据验证成功"""
        # 执行测试
        user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        result = self.user_service.validate_user_data(user_data)
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_user_data_invalid_email(self):
        """测试用户数据验证 - 无效邮箱"""
        # 执行测试
        user_data = {
            'username': 'test_user',
            'email': 'invalid_email',
            'password': 'Password123!'
        }
        result = self.user_service.validate_user_data(user_data)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('email', result['errors'])
    
    def test_validate_user_data_weak_password(self):
        """测试用户数据验证 - 弱密码"""
        # 执行测试
        user_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'password': '123'
        }
        result = self.user_service.validate_user_data(user_data)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('password', result['errors'])
    
    def test_validate_user_data_short_username(self):
        """测试用户数据验证 - 用户名太短"""
        # 执行测试
        user_data = {
            'username': 'ab',
            'email': 'test@example.com',
            'password': 'Password123!'
        }
        result = self.user_service.validate_user_data(user_data)
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('username', result['errors'])


if __name__ == '__main__':
    # 运行测试
    unittest.main()