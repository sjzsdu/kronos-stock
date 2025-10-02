# -*- coding: utf-8 -*-
"""
认证服务单元测试
测试用户认证服务的各种功能
"""

import pytest
import unittest
import jwt
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

from app.services.auth_service import AuthService
from app.models.user import User, UserSession


class TestAuthService(unittest.TestCase):
    """认证服务测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.auth_service = AuthService()
        self.mock_user_data = {
            'id': 1,
            'username': 'test_user',
            'email': 'test@example.com',
            'password_hash': 'hashed_password',
            'is_active': True,
            'is_admin': False
        }
        self.mock_secret_key = 'test_secret_key'
    
    @patch('app.services.auth_service.current_app')
    @patch('app.services.auth_service.UserSession')
    @patch('app.services.auth_service.jwt.encode')
    def test_generate_token_success(self, mock_jwt_encode, mock_session_class, mock_app):
        """测试生成token成功"""
        # 设置mock
        mock_app.config = {'SECRET_KEY': self.mock_secret_key}
        mock_jwt_encode.return_value = 'generated_token'
        mock_session_instance = Mock()
        mock_session_class.return_value = mock_session_instance
        
        with patch('app.services.auth_service.db.session') as mock_db_session:
            # 执行测试
            token = self.auth_service.generate_token(1)
            
            # 验证结果
            self.assertEqual(token, 'generated_token')
            mock_db_session.add.assert_called_once_with(mock_session_instance)
            mock_db_session.commit.assert_called_once()
    
    @patch('app.services.auth_service.current_app')
    @patch('app.services.auth_service.jwt.decode')
    @patch('app.services.auth_service.UserSession')
    def test_verify_token_success(self, mock_session_class, mock_jwt_decode, mock_app):
        """测试验证token成功"""
        # 设置mock
        mock_app.config = {'SECRET_KEY': self.mock_secret_key}
        mock_jwt_decode.return_value = {'user_id': 1, 'exp': int(datetime.now(timezone.utc).timestamp()) + 3600}
        
        mock_session = Mock()
        mock_session.is_active = True
        mock_session.is_expired.return_value = False
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        # 执行测试
        result = self.auth_service.verify_token('valid_token')
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(result['user_id'], 1)
    
    @patch('app.services.auth_service.current_app')
    @patch('app.services.auth_service.jwt.decode')
    def test_verify_token_invalid(self, mock_jwt_decode, mock_app):
        """测试验证无效token"""
        # 设置mock
        mock_app.config = {'SECRET_KEY': self.mock_secret_key}
        mock_jwt_decode.side_effect = jwt.InvalidTokenError('Invalid token')
        
        # 执行测试
        result = self.auth_service.verify_token('invalid_token')
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('token无效', result['message'])
    
    @patch('app.services.auth_service.current_app')
    @patch('app.services.auth_service.jwt.decode')
    @patch('app.services.auth_service.UserSession')
    def test_verify_token_expired(self, mock_session_class, mock_jwt_decode, mock_app):
        """测试验证过期token"""
        # 设置mock
        mock_app.config = {'SECRET_KEY': self.mock_secret_key}
        mock_jwt_decode.return_value = {'user_id': 1, 'exp': int(datetime.now(timezone.utc).timestamp()) - 3600}
        
        mock_session = Mock()
        mock_session.is_active = True
        mock_session.is_expired.return_value = True
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        with patch('app.services.auth_service.db.session') as mock_db_session:
            # 执行测试
            result = self.auth_service.verify_token('expired_token')
            
            # 验证结果
            self.assertFalse(result['valid'])
            self.assertIn('token已过期', result['message'])
    
    @patch('app.services.auth_service.UserSession')
    def test_revoke_token_success(self, mock_session_class):
        """测试撤销token成功"""
        # 设置mock
        mock_session = Mock()
        mock_session.is_active = True
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        with patch('app.services.auth_service.db.session') as mock_db_session:
            # 执行测试
            result = self.auth_service.revoke_token('valid_token')
            
            # 验证结果
            self.assertTrue(result['success'])
            self.assertFalse(mock_session.is_active)
            mock_db_session.commit.assert_called_once()
    
    @patch('app.services.auth_service.UserSession')
    def test_revoke_token_not_found(self, mock_session_class):
        """测试撤销不存在的token"""
        # 设置mock
        mock_session_class.query.filter_by.return_value.first.return_value = None
        
        # 执行测试
        result = self.auth_service.revoke_token('nonexistent_token')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('token不存在', result['message'])
    
    @patch('app.services.auth_service.UserSession')
    def test_revoke_all_user_tokens_success(self, mock_session_class):
        """测试撤销用户所有token成功"""
        # 设置mock
        mock_sessions = [Mock(), Mock(), Mock()]
        mock_session_class.query.filter_by.return_value.all.return_value = mock_sessions
        
        with patch('app.services.auth_service.db.session') as mock_db_session:
            # 执行测试
            result = self.auth_service.revoke_all_user_tokens(1)
            
            # 验证结果
            self.assertTrue(result['success'])
            for session in mock_sessions:
                self.assertFalse(session.is_active)
            mock_db_session.commit.assert_called_once()
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.bcrypt.check_password_hash')
    def test_authenticate_with_credentials_success(self, mock_check_password, mock_user_class):
        """测试凭据认证成功"""
        # 设置mock
        mock_user = Mock()
        mock_user.id = 1
        mock_user.is_active = True
        mock_user.password_hash = 'hashed_password'
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        mock_check_password.return_value = True
        
        # 执行测试
        result = self.auth_service.authenticate_with_credentials('test_user', 'correct_password')
        
        # 验证结果
        self.assertTrue(result['success'])
        self.assertEqual(result['user'], mock_user)
    
    @patch('app.services.auth_service.User')
    def test_authenticate_with_credentials_user_not_found(self, mock_user_class):
        """测试凭据认证 - 用户不存在"""
        # 设置mock
        mock_user_class.query.filter_by.return_value.first.return_value = None
        
        # 执行测试
        result = self.auth_service.authenticate_with_credentials('nonexistent_user', 'password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('认证失败', result['message'])
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.bcrypt.check_password_hash')
    def test_authenticate_with_credentials_wrong_password(self, mock_check_password, mock_user_class):
        """测试凭据认证 - 密码错误"""
        # 设置mock
        mock_user = Mock()
        mock_user.is_active = True
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        mock_check_password.return_value = False
        
        # 执行测试
        result = self.auth_service.authenticate_with_credentials('test_user', 'wrong_password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('认证失败', result['message'])
    
    @patch('app.services.auth_service.User')
    @patch('app.services.auth_service.bcrypt.check_password_hash')
    def test_authenticate_with_credentials_inactive_user(self, mock_check_password, mock_user_class):
        """测试凭据认证 - 用户已禁用"""
        # 设置mock
        mock_user = Mock()
        mock_user.is_active = False
        mock_user_class.query.filter_by.return_value.first.return_value = mock_user
        mock_check_password.return_value = True
        
        # 执行测试
        result = self.auth_service.authenticate_with_credentials('test_user', 'correct_password')
        
        # 验证结果
        self.assertFalse(result['success'])
        self.assertIn('用户账户已被禁用', result['message'])
    
    @patch('app.services.auth_service.UserSession')
    def test_get_user_sessions_success(self, mock_session_class):
        """测试获取用户会话成功"""
        # 设置mock
        mock_sessions = [Mock(), Mock()]
        mock_session_class.query.filter_by.return_value.order_by.return_value.all.return_value = mock_sessions
        
        # 执行测试
        sessions = self.auth_service.get_user_sessions(1)
        
        # 验证结果
        self.assertEqual(len(sessions), 2)
        mock_session_class.query.filter_by.assert_called_once_with(user_id=1)
    
    @patch('app.services.auth_service.UserSession')
    def test_cleanup_expired_sessions_success(self, mock_session_class):
        """测试清理过期会话成功"""
        # 设置mock
        mock_expired_sessions = [Mock(), Mock(), Mock()]
        mock_session_class.query.filter.return_value.all.return_value = mock_expired_sessions
        
        with patch('app.services.auth_service.db.session') as mock_db_session:
            # 执行测试
            result = self.auth_service.cleanup_expired_sessions()
            
            # 验证结果
            self.assertTrue(result['success'])
            self.assertEqual(result['cleaned_count'], 3)
            for session in mock_expired_sessions:
                mock_db_session.delete.assert_any_call(session)
            mock_db_session.commit.assert_called_once()
    
    def test_validate_password_strength_success(self):
        """测试密码强度验证成功"""
        # 执行测试
        result = self.auth_service.validate_password_strength('StrongPassword123!')
        
        # 验证结果
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_password_strength_too_short(self):
        """测试密码强度验证 - 过短"""
        # 执行测试
        result = self.auth_service.validate_password_strength('123')
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('密码长度至少8位', result['errors'])
    
    def test_validate_password_strength_no_uppercase(self):
        """测试密码强度验证 - 无大写字母"""
        # 执行测试
        result = self.auth_service.validate_password_strength('lowercase123!')
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含大写字母', result['errors'])
    
    def test_validate_password_strength_no_digits(self):
        """测试密码强度验证 - 无数字"""
        # 执行测试
        result = self.auth_service.validate_password_strength('PasswordOnly!')
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含数字', result['errors'])
    
    def test_validate_password_strength_no_special_chars(self):
        """测试密码强度验证 - 无特殊字符"""
        # 执行测试
        result = self.auth_service.validate_password_strength('Password123')
        
        # 验证结果
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含特殊字符', result['errors'])
    
    @patch('app.services.auth_service.UserSession')
    def test_is_session_valid_success(self, mock_session_class):
        """测试会话有效性检查成功"""
        # 设置mock
        mock_session = Mock()
        mock_session.is_active = True
        mock_session.is_expired.return_value = False
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        # 执行测试
        result = self.auth_service.is_session_valid('valid_token')
        
        # 验证结果
        self.assertTrue(result)
    
    @patch('app.services.auth_service.UserSession')
    def test_is_session_valid_inactive(self, mock_session_class):
        """测试会话有效性检查 - 会话未激活"""
        # 设置mock
        mock_session = Mock()
        mock_session.is_active = False
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        # 执行测试
        result = self.auth_service.is_session_valid('inactive_token')
        
        # 验证结果
        self.assertFalse(result)
    
    @patch('app.services.auth_service.UserSession')
    def test_is_session_valid_expired(self, mock_session_class):
        """测试会话有效性检查 - 会话已过期"""
        # 设置mock
        mock_session = Mock()
        mock_session.is_active = True
        mock_session.is_expired.return_value = True
        mock_session_class.query.filter_by.return_value.first.return_value = mock_session
        
        # 执行测试
        result = self.auth_service.is_session_valid('expired_token')
        
        # 验证结果
        self.assertFalse(result)
    
    @patch('app.services.auth_service.UserSession')
    def test_is_session_valid_not_found(self, mock_session_class):
        """测试会话有效性检查 - 会话不存在"""
        # 设置mock
        mock_session_class.query.filter_by.return_value.first.return_value = None
        
        # 执行测试
        result = self.auth_service.is_session_valid('nonexistent_token')
        
        # 验证结果
        self.assertFalse(result)


if __name__ == '__main__':
    # 运行测试
    unittest.main()