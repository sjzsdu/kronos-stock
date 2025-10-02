# -*- coding: utf-8 -*-
"""
密码验证单元测试
测试密码加密和验证服务的功能
"""

import pytest
import unittest
import bcrypt
from unittest.mock import Mock, patch

from app.services.password_service import PasswordService


class TestPasswordService(unittest.TestCase):
    """密码验证服务测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.password_service = PasswordService()
    
    @patch('app.services.password_service.bcrypt.gensalt')
    @patch('app.services.password_service.bcrypt.hashpw')
    def test_hash_password_success(self, mock_hashpw, mock_gensalt):
        """测试密码哈希化成功"""
        # 设置mock
        mock_salt = b'$2b$12$mockSaltValue'
        mock_hash = b'$2b$12$mockHashedPassword'
        mock_gensalt.return_value = mock_salt
        mock_hashpw.return_value = mock_hash
        
        # 执行测试
        password = 'TestPassword123!'
        hashed = self.password_service.hash_password(password)
        
        # 验证结果
        self.assertEqual(hashed, mock_hash.decode('utf-8'))
        mock_gensalt.assert_called_once_with(rounds=12)
        mock_hashpw.assert_called_once_with(password.encode('utf-8'), mock_salt)
    
    @patch('app.services.password_service.bcrypt.checkpw')
    def test_verify_password_success(self, mock_checkpw):
        """测试密码验证成功"""
        # 设置mock
        mock_checkpw.return_value = True
        
        # 执行测试
        password = 'TestPassword123!'
        hashed = '$2b$12$mockHashedPassword'
        result = self.password_service.verify_password(password, hashed)
        
        # 验证结果
        self.assertTrue(result)
        mock_checkpw.assert_called_once_with(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    
    @patch('app.services.password_service.bcrypt.checkpw')
    def test_verify_password_failure(self, mock_checkpw):
        """测试密码验证失败"""
        # 设置mock
        mock_checkpw.return_value = False
        
        # 执行测试
        password = 'WrongPassword'
        hashed = '$2b$12$mockHashedPassword'
        result = self.password_service.verify_password(password, hashed)
        
        # 验证结果
        self.assertFalse(result)
        mock_checkpw.assert_called_once_with(
            password.encode('utf-8'),
            hashed.encode('utf-8')
        )
    
    @patch('app.services.password_service.bcrypt.checkpw')
    def test_verify_password_exception(self, mock_checkpw):
        """测试密码验证异常处理"""
        # 设置mock
        mock_checkpw.side_effect = ValueError('Invalid hash format')
        
        # 执行测试
        password = 'TestPassword123!'
        hashed = 'invalid_hash'
        result = self.password_service.verify_password(password, hashed)
        
        # 验证结果
        self.assertFalse(result)
    
    def test_validate_password_strength_success(self):
        """测试密码强度验证成功"""
        # 测试强密码
        strong_passwords = [
            'Password123!',
            'MyStr0ng@Pass',
            'C0mplex#Pwd1',
            'Secure&Pass2023!'
        ]
        
        for password in strong_passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertTrue(result['valid'], f"密码 '{password}' 应该是有效的")
            self.assertEqual(len(result['errors']), 0)
    
    def test_validate_password_strength_too_short(self):
        """测试密码强度验证 - 长度不足"""
        short_passwords = ['', '123', 'short', 'Pass1!']
        
        for password in short_passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertFalse(result['valid'])
            self.assertIn('密码长度至少8位', result['errors'])
    
    def test_validate_password_strength_no_uppercase(self):
        """测试密码强度验证 - 缺少大写字母"""
        passwords = ['password123!', 'lowercase@123', 'noupperca5e#']
        
        for password in passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertFalse(result['valid'])
            self.assertIn('密码必须包含大写字母', result['errors'])
    
    def test_validate_password_strength_no_lowercase(self):
        """测试密码强度验证 - 缺少小写字母"""
        passwords = ['PASSWORD123!', 'UPPERCASE@123', 'NOLOWERCA5E#']
        
        for password in passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertFalse(result['valid'])
            self.assertIn('密码必须包含小写字母', result['errors'])
    
    def test_validate_password_strength_no_digits(self):
        """测试密码强度验证 - 缺少数字"""
        passwords = ['Password!', 'NoDigits@', 'Letters#Only']
        
        for password in passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertFalse(result['valid'])
            self.assertIn('密码必须包含数字', result['errors'])
    
    def test_validate_password_strength_no_special_chars(self):
        """测试密码强度验证 - 缺少特殊字符"""
        passwords = ['Password123', 'NoSpecial123', 'OnlyLetters123']
        
        for password in passwords:
            result = self.password_service.validate_password_strength(password)
            self.assertFalse(result['valid'])
            self.assertIn('密码必须包含特殊字符', result['errors'])
    
    def test_validate_password_strength_multiple_errors(self):
        """测试密码强度验证 - 多个错误"""
        password = 'weak'  # 太短，缺少大写、数字、特殊字符
        
        result = self.password_service.validate_password_strength(password)
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 1)
        self.assertIn('密码长度至少8位', result['errors'])
        self.assertIn('密码必须包含大写字母', result['errors'])
        self.assertIn('密码必须包含数字', result['errors'])
        self.assertIn('密码必须包含特殊字符', result['errors'])
    
    def test_validate_password_strength_empty(self):
        """测试密码强度验证 - 空密码"""
        result = self.password_service.validate_password_strength('')
        
        self.assertFalse(result['valid'])
        self.assertIn('密码不能为空', result['errors'])
    
    def test_validate_password_strength_none(self):
        """测试密码强度验证 - None密码"""
        result = self.password_service.validate_password_strength(None)
        
        self.assertFalse(result['valid'])
        self.assertIn('密码不能为空', result['errors'])
    
    def test_generate_random_password_default_length(self):
        """测试生成随机密码 - 默认长度"""
        password = self.password_service.generate_random_password()
        
        self.assertIsInstance(password, str)
        self.assertEqual(len(password), 12)  # 默认长度
        
        # 验证生成的密码符合强度要求
        validation = self.password_service.validate_password_strength(password)
        self.assertTrue(validation['valid'])
    
    def test_generate_random_password_custom_length(self):
        """测试生成随机密码 - 自定义长度"""
        lengths = [8, 16, 20, 32]
        
        for length in lengths:
            password = self.password_service.generate_random_password(length=length)
            
            self.assertIsInstance(password, str)
            self.assertEqual(len(password), length)
            
            # 验证生成的密码符合强度要求
            validation = self.password_service.validate_password_strength(password)
            self.assertTrue(validation['valid'])
    
    def test_generate_random_password_uniqueness(self):
        """测试生成随机密码的唯一性"""
        passwords = set()
        
        # 生成100个密码，应该都是不同的
        for _ in range(100):
            password = self.password_service.generate_random_password()
            passwords.add(password)
        
        # 验证生成的密码都是唯一的
        self.assertEqual(len(passwords), 100)
    
    def test_check_password_complexity_success(self):
        """测试密码复杂度检查成功"""
        complex_passwords = [
            'Aa1!Bb2@Cc3#',
            'MyVeryStr0ng&P@ssw0rd!',
            '2023$ecure#Pa55w0rd'
        ]
        
        for password in complex_passwords:
            result = self.password_service.check_password_complexity(password)
            self.assertTrue(result['is_complex'])
            self.assertGreaterEqual(result['score'], 4)  # 满分5分，至少4分
    
    def test_check_password_complexity_simple(self):
        """测试密码复杂度检查 - 简单密码"""
        simple_passwords = [
            'password',
            '12345678',
            'abcdefgh',
            'ABCDEFGH'
        ]
        
        for password in simple_passwords:
            result = self.password_service.check_password_complexity(password)
            self.assertFalse(result['is_complex'])
            self.assertLess(result['score'], 3)  # 复杂度得分低于3
    
    def test_is_common_password_true(self):
        """测试常见密码检查 - 是常见密码"""
        common_passwords = [
            'password',
            '123456789',
            'qwerty123',
            'admin123',
            'password123'
        ]
        
        for password in common_passwords:
            result = self.password_service.is_common_password(password)
            self.assertTrue(result, f"'{password}' 应该被识别为常见密码")
    
    def test_is_common_password_false(self):
        """测试常见密码检查 - 不是常见密码"""
        uncommon_passwords = [
            'MyVeryUn1que@P4ssw0rd!',
            'C0mplex&Random#2023',
            'Unique$Pass#789'
        ]
        
        for password in uncommon_passwords:
            result = self.password_service.is_common_password(password)
            self.assertFalse(result, f"'{password}' 不应该被识别为常见密码")
    
    def test_get_password_strength_score_weak(self):
        """测试密码强度评分 - 弱密码"""
        weak_passwords = [
            'abc',
            '123',
            'password'
        ]
        
        for password in weak_passwords:
            score = self.password_service.get_password_strength_score(password)
            self.assertLessEqual(score, 2, f"'{password}' 的强度评分应该 <= 2")
    
    def test_get_password_strength_score_medium(self):
        """测试密码强度评分 - 中等密码"""
        medium_passwords = [
            'Password123',
            'MyPass456',
            'User12345'
        ]
        
        for password in medium_passwords:
            score = self.password_service.get_password_strength_score(password)
            self.assertGreaterEqual(score, 2, f"'{password}' 的强度评分应该 >= 2")
            self.assertLessEqual(score, 4, f"'{password}' 的强度评分应该 <= 4")
    
    def test_get_password_strength_score_strong(self):
        """测试密码强度评分 - 强密码"""
        strong_passwords = [
            'MyStr0ng@P4ssw0rd!',
            'C0mplex&Secure#2023',
            'V3ry$ecure#Pa55w0rd!'
        ]
        
        for password in strong_passwords:
            score = self.password_service.get_password_strength_score(password)
            self.assertGreaterEqual(score, 4, f"'{password}' 的强度评分应该 >= 4")


if __name__ == '__main__':
    # 运行测试
    unittest.main()