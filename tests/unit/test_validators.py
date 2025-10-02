# -*- coding: utf-8 -*-
"""
验证器单元测试
测试用户输入验证和清理功能
"""

import pytest
import unittest
from datetime import datetime, date

from app.utils.validators import (
    EmailValidator,
    PasswordValidator,
    UsernameValidator,
    PhoneValidator,
    InputSanitizer,
    FormValidator
)


class TestEmailValidator(unittest.TestCase):
    """邮箱验证器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.validator = EmailValidator()
    
    def test_valid_emails(self):
        """测试有效邮箱"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.com',
            'user+tag@example.org',
            'firstname.lastname@domain.co.uk',
            'user123@test-domain.com',
            'a@b.co'
        ]
        
        for email in valid_emails:
            result = self.validator.validate(email)
            self.assertTrue(result['valid'], f"邮箱 '{email}' 应该是有效的")
            self.assertEqual(len(result['errors']), 0)
    
    def test_invalid_emails(self):
        """测试无效邮箱"""
        invalid_emails = [
            '',
            'invalid',
            'test@',
            '@example.com',
            'test..email@example.com',
            'test@example',
            'test@.com',
            'test space@example.com',
            'test@example..com'
        ]
        
        for email in invalid_emails:
            result = self.validator.validate(email)
            self.assertFalse(result['valid'], f"邮箱 '{email}' 应该是无效的")
            self.assertGreater(len(result['errors']), 0)
    
    def test_email_length_limits(self):
        """测试邮箱长度限制"""
        # 测试过长邮箱
        long_email = 'a' * 250 + '@example.com'
        result = self.validator.validate(long_email)
        self.assertFalse(result['valid'])
        self.assertIn('邮箱长度不能超过254个字符', result['errors'])
    
    def test_normalize_email(self):
        """测试邮箱标准化"""
        test_cases = [
            ('Test@EXAMPLE.COM', 'test@example.com'),
            ('USER@Domain.ORG', 'user@domain.org'),
            ('  spaced@example.com  ', 'spaced@example.com')
        ]
        
        for input_email, expected in test_cases:
            normalized = self.validator.normalize(input_email)
            self.assertEqual(normalized, expected)


class TestPasswordValidator(unittest.TestCase):
    """密码验证器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.validator = PasswordValidator()
    
    def test_strong_passwords(self):
        """测试强密码"""
        strong_passwords = [
            'Password123!',
            'MyStr0ng@Pass',
            'C0mplex#Pwd2023',
            'Secure&Password1!'
        ]
        
        for password in strong_passwords:
            result = self.validator.validate(password)
            self.assertTrue(result['valid'], f"密码 '{password}' 应该是有效的")
            self.assertEqual(len(result['errors']), 0)
    
    def test_weak_passwords(self):
        """测试弱密码"""
        weak_passwords = [
            '',
            '123',
            'short',
            'password',
            'PASSWORD',
            '12345678',
            'Password',
            'Password123'
        ]
        
        for password in weak_passwords:
            result = self.validator.validate(password)
            self.assertFalse(result['valid'], f"密码 '{password}' 应该是无效的")
            self.assertGreater(len(result['errors']), 0)
    
    def test_password_length_requirements(self):
        """测试密码长度要求"""
        # 太短
        short_password = 'Aa1!'
        result = self.validator.validate(short_password)
        self.assertFalse(result['valid'])
        self.assertIn('密码长度至少8位', result['errors'])
        
        # 太长
        long_password = 'A' * 129 + 'a1!'
        result = self.validator.validate(long_password)
        self.assertFalse(result['valid'])
        self.assertIn('密码长度不能超过128位', result['errors'])
    
    def test_password_complexity_requirements(self):
        """测试密码复杂度要求"""
        # 缺少大写字母
        no_upper = 'password123!'
        result = self.validator.validate(no_upper)
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含大写字母', result['errors'])
        
        # 缺少小写字母
        no_lower = 'PASSWORD123!'
        result = self.validator.validate(no_lower)
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含小写字母', result['errors'])
        
        # 缺少数字
        no_digit = 'Password!'
        result = self.validator.validate(no_digit)
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含数字', result['errors'])
        
        # 缺少特殊字符
        no_special = 'Password123'
        result = self.validator.validate(no_special)
        self.assertFalse(result['valid'])
        self.assertIn('密码必须包含特殊字符', result['errors'])
    
    def test_common_password_detection(self):
        """测试常见密码检测"""
        common_passwords = [
            'password',
            '123456789',
            'qwerty123'
        ]
        
        for password in common_passwords:
            result = self.validator.validate(password)
            # 即使格式正确，常见密码也应该被拒绝
            if result['valid']:  # 如果通过了格式检查
                self.assertIn('密码过于常见', result['warnings'])


class TestUsernameValidator(unittest.TestCase):
    """用户名验证器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.validator = UsernameValidator()
    
    def test_valid_usernames(self):
        """测试有效用户名"""
        valid_usernames = [
            'user123',
            'test_user',
            'my-username',
            'User.Name',
            'username1',
            'abcdef'
        ]
        
        for username in valid_usernames:
            result = self.validator.validate(username)
            self.assertTrue(result['valid'], f"用户名 '{username}' 应该是有效的")
            self.assertEqual(len(result['errors']), 0)
    
    def test_invalid_usernames(self):
        """测试无效用户名"""
        invalid_usernames = [
            '',
            'ab',  # 太短
            'a' * 51,  # 太长
            'user name',  # 空格
            'user@name',  # 特殊字符
            'user#name',
            '123',  # 纯数字
            '-username',  # 以符号开头
            'username-',  # 以符号结尾
            '.username',
            'username.'
        ]
        
        for username in invalid_usernames:
            result = self.validator.validate(username)
            self.assertFalse(result['valid'], f"用户名 '{username}' 应该是无效的")
            self.assertGreater(len(result['errors']), 0)
    
    def test_username_length_limits(self):
        """测试用户名长度限制"""
        # 太短
        short_username = 'ab'
        result = self.validator.validate(short_username)
        self.assertFalse(result['valid'])
        self.assertIn('用户名长度必须在3-50个字符之间', result['errors'])
        
        # 太长
        long_username = 'a' * 51
        result = self.validator.validate(long_username)
        self.assertFalse(result['valid'])
        self.assertIn('用户名长度必须在3-50个字符之间', result['errors'])
    
    def test_username_character_restrictions(self):
        """测试用户名字符限制"""
        # 包含非法字符
        invalid_chars = ['user@name', 'user#name', 'user name', 'user%name']
        
        for username in invalid_chars:
            result = self.validator.validate(username)
            self.assertFalse(result['valid'])
            self.assertIn('用户名只能包含字母、数字、下划线、连字符和点号', result['errors'])
    
    def test_reserved_usernames(self):
        """测试保留用户名"""
        reserved_usernames = [
            'admin',
            'root',
            'administrator',
            'system',
            'api',
            'www'
        ]
        
        for username in reserved_usernames:
            result = self.validator.validate(username)
            self.assertFalse(result['valid'])
            self.assertIn('用户名为系统保留', result['errors'])


class TestPhoneValidator(unittest.TestCase):
    """手机号验证器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.validator = PhoneValidator()
    
    def test_valid_china_phone_numbers(self):
        """测试有效的中国手机号"""
        valid_phones = [
            '13812345678',
            '15987654321',
            '18012345678',
            '17712345678',
            '19912345678'
        ]
        
        for phone in valid_phones:
            result = self.validator.validate(phone)
            self.assertTrue(result['valid'], f"手机号 '{phone}' 应该是有效的")
            self.assertEqual(len(result['errors']), 0)
    
    def test_invalid_phone_numbers(self):
        """测试无效手机号"""
        invalid_phones = [
            '',
            '1234567890',  # 不是11位
            '12345678901',  # 不是以1开头
            '21234567890',  # 不是有效前缀
            '1381234567',   # 位数不够
            '138123456789', # 位数过多
            '13a12345678',  # 包含字母
            '138-1234-5678' # 包含特殊字符
        ]
        
        for phone in invalid_phones:
            result = self.validator.validate(phone)
            self.assertFalse(result['valid'], f"手机号 '{phone}' 应该是无效的")
            self.assertGreater(len(result['errors']), 0)
    
    def test_phone_formatting(self):
        """测试手机号格式化"""
        test_cases = [
            ('138 1234 5678', '13812345678'),
            ('138-1234-5678', '13812345678'),
            ('+86 138 1234 5678', '13812345678'),
            ('  13812345678  ', '13812345678')
        ]
        
        for input_phone, expected in test_cases:
            formatted = self.validator.format(input_phone)
            self.assertEqual(formatted, expected)


class TestInputSanitizer(unittest.TestCase):
    """输入清理器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.sanitizer = InputSanitizer()
    
    def test_sanitize_html(self):
        """测试HTML清理"""
        test_cases = [
            ('<script>alert("xss")</script>', ''),
            ('<b>Bold text</b>', 'Bold text'),
            ('Normal text', 'Normal text'),
            ('<img src="x" onerror="alert(1)">', ''),
            ('Text with <strong>emphasis</strong>', 'Text with emphasis')
        ]
        
        for input_html, expected in test_cases:
            sanitized = self.sanitizer.sanitize_html(input_html)
            self.assertEqual(sanitized, expected)
    
    def test_sanitize_sql(self):
        """测试SQL注入清理"""
        test_cases = [
            ("'; DROP TABLE users; --", "&#x27;; DROP TABLE users; --"),
            ("normal text", "normal text"),
            ("user'name", "user&#x27;name"),
            ('SELECT * FROM users', 'SELECT * FROM users')
        ]
        
        for input_sql, expected in test_cases:
            sanitized = self.sanitizer.sanitize_sql(input_sql)
            self.assertEqual(sanitized, expected)
    
    def test_clean_whitespace(self):
        """测试空白字符清理"""
        test_cases = [
            ('  leading spaces', 'leading spaces'),
            ('trailing spaces  ', 'trailing spaces'),
            ('  both ends  ', 'both ends'),
            ('multiple   spaces', 'multiple spaces'),
            ('line\nbreaks\n', 'line breaks'),
            ('tabs\tand\tspaces', 'tabs and spaces')
        ]
        
        for input_text, expected in test_cases:
            cleaned = self.sanitizer.clean_whitespace(input_text)
            self.assertEqual(cleaned, expected)
    
    def test_remove_control_characters(self):
        """测试控制字符移除"""
        # 包含控制字符的文本
        control_chars = '\x00\x01\x02\x03'
        text_with_control = f'Normal{control_chars}text'
        
        cleaned = self.sanitizer.remove_control_characters(text_with_control)
        self.assertEqual(cleaned, 'Normaltext')
    
    def test_validate_file_name(self):
        """测试文件名验证"""
        valid_names = ['document.pdf', 'image.jpg', 'data_file.csv']
        invalid_names = ['../../../etc/passwd', 'file<script>.txt', 'con.txt']
        
        for name in valid_names:
            result = self.sanitizer.validate_file_name(name)
            self.assertTrue(result['valid'])
        
        for name in invalid_names:
            result = self.sanitizer.validate_file_name(name)
            self.assertFalse(result['valid'])


class TestFormValidator(unittest.TestCase):
    """表单验证器测试类"""
    
    def setUp(self):
        """测试前置设置"""
        self.validator = FormValidator()
    
    def test_validate_registration_form_success(self):
        """测试注册表单验证成功"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'phone': '13812345678',
            'nickname': '测试用户'
        }
        
        result = self.validator.validate_registration_form(form_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_registration_form_password_mismatch(self):
        """测试注册表单验证 - 密码不匹配"""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!',
            'phone': '13812345678'
        }
        
        result = self.validator.validate_registration_form(form_data)
        
        self.assertFalse(result['valid'])
        self.assertIn('confirm_password', result['errors'])
        self.assertIn('密码确认不匹配', result['errors']['confirm_password'])
    
    def test_validate_login_form_success(self):
        """测试登录表单验证成功"""
        form_data = {
            'username': 'testuser',
            'password': 'Password123!'
        }
        
        result = self.validator.validate_login_form(form_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_login_form_missing_fields(self):
        """测试登录表单验证 - 缺少字段"""
        form_data = {
            'username': 'testuser'
            # 缺少password
        }
        
        result = self.validator.validate_login_form(form_data)
        
        self.assertFalse(result['valid'])
        self.assertIn('password', result['errors'])
        self.assertIn('密码不能为空', result['errors']['password'])
    
    def test_validate_profile_form_success(self):
        """测试档案表单验证成功"""
        form_data = {
            'nickname': '新昵称',
            'phone': '13987654321',
            'real_name': '张三',
            'bio': '这是个人简介'
        }
        
        result = self.validator.validate_profile_form(form_data)
        
        self.assertTrue(result['valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_validate_date_field(self):
        """测试日期字段验证"""
        # 有效日期
        valid_dates = ['1990-01-01', '2000-12-31', '1985-06-15']
        
        for date_str in valid_dates:
            result = self.validator.validate_date_field(date_str)
            self.assertTrue(result['valid'])
        
        # 无效日期
        invalid_dates = ['invalid-date', '2000-13-01', '1900-01-32']
        
        for date_str in invalid_dates:
            result = self.validator.validate_date_field(date_str)
            self.assertFalse(result['valid'])
    
    def test_validate_required_fields(self):
        """测试必填字段验证"""
        form_data = {
            'field1': 'value1',
            'field2': '',
            'field3': '   ',
            # field4 missing
        }
        
        required_fields = ['field1', 'field2', 'field3', 'field4']
        errors = self.validator.validate_required_fields(form_data, required_fields)
        
        # field1 应该通过验证
        self.assertNotIn('field1', errors)
        
        # field2, field3, field4 应该报错
        self.assertIn('field2', errors)
        self.assertIn('field3', errors)
        self.assertIn('field4', errors)


if __name__ == '__main__':
    # 运行测试
    unittest.main()