# -*- coding: utf-8 -*-
"""
密码服务
处理密码加密、验证、强度检查等功能
"""

import re
import bcrypt
from typing import Dict, Any, List


class PasswordService:
    """密码管理服务类"""
    
    def __init__(self):
        """初始化密码服务"""
        self.min_length = 8
        self.max_length = 128
        self.rounds = 12  # bcrypt加密轮次
        
        # 常见弱密码列表
        self.weak_passwords = {
            'password', '123456', '12345678', 'qwerty', 'abc123',
            'password123', 'admin', 'letmein', 'welcome', 'monkey',
            '1234567890', 'password1', '123123', 'qwertyuiop'
        }
    
    def hash_password(self, password: str) -> str:
        """
        使用bcrypt加密密码
        
        Args:
            password: 原始密码
            
        Returns:
            str: 加密后的密码哈希
        """
        # 将密码编码为bytes
        password_bytes = password.encode('utf-8')
        
        # 生成盐值并加密
        salt = bcrypt.gensalt(rounds=self.rounds)
        password_hash = bcrypt.hashpw(password_bytes, salt)
        
        # 返回字符串格式的哈希
        return password_hash.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        验证密码是否正确
        
        Args:
            password: 用户输入的密码
            password_hash: 数据库中存储的密码哈希
            
        Returns:
            bool: 密码是否匹配
        """
        try:
            # 将密码和哈希编码为bytes
            password_bytes = password.encode('utf-8')
            hash_bytes = password_hash.encode('utf-8')
            
            # 使用bcrypt验证密码
            return bcrypt.checkpw(password_bytes, hash_bytes)
            
        except (ValueError, TypeError):
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """
        验证密码强度
        
        Args:
            password: 要验证的密码
            
        Returns:
            Dict: 验证结果，包含valid字段和errors列表
        """
        errors = []
        
        # 检查密码长度
        if len(password) < self.min_length:
            errors.append(f'密码长度至少需要{self.min_length}位')
        
        if len(password) > self.max_length:
            errors.append(f'密码长度不能超过{self.max_length}位')
        
        # 检查是否包含常见弱密码
        if password.lower() in self.weak_passwords:
            errors.append('不能使用常见弱密码')
        
        # 检查字符类型要求
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        char_type_count = sum([has_upper, has_lower, has_digit, has_special])
        
        if char_type_count < 3:
            errors.append('密码必须包含大写字母、小写字母、数字和特殊字符中的至少3种')
        
        # 检查重复字符
        if self._has_repeated_chars(password):
            errors.append('密码不能包含连续重复的字符')
        
        # 检查连续字符
        if self._has_sequential_chars(password):
            errors.append('密码不能包含连续的字符序列')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength_score': self._calculate_strength_score(password, has_upper, has_lower, has_digit, has_special),
            'requirements': {
                'has_upper_case': has_upper,
                'has_lower_case': has_lower,
                'has_digits': has_digit,
                'has_special_chars': has_special,
                'min_length': len(password) >= self.min_length,
                'not_common': password.lower() not in self.weak_passwords
            }
        }
    
    def generate_strong_password(self, length: int = 12) -> str:
        """
        生成强密码
        
        Args:
            length: 密码长度，默认12位
            
        Returns:
            str: 生成的强密码
        """
        import secrets
        import string
        
        if length < self.min_length:
            length = self.min_length
        
        # 确保包含各种字符类型
        chars = []
        chars.append(secrets.choice(string.ascii_uppercase))  # 大写字母
        chars.append(secrets.choice(string.ascii_lowercase))  # 小写字母  
        chars.append(secrets.choice(string.digits))           # 数字
        chars.append(secrets.choice('!@#$%^&*'))             # 特殊字符
        
        # 填充剩余长度
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*'
        for _ in range(length - 4):
            chars.append(secrets.choice(all_chars))
        
        # 随机排列字符
        secrets.SystemRandom().shuffle(chars)
        
        return ''.join(chars)
    
    def _has_repeated_chars(self, password: str, max_repeat: int = 2) -> bool:
        """检查是否有重复字符"""
        for i in range(len(password) - max_repeat):
            if len(set(password[i:i+max_repeat+1])) == 1:
                return True
        return False
    
    def _has_sequential_chars(self, password: str, max_sequence: int = 3) -> bool:
        """检查是否有连续字符序列"""
        sequences = [
            'abcdefghijklmnopqrstuvwxyz',
            'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 
            '0123456789'
        ]
        
        for sequence in sequences:
            for i in range(len(sequence) - max_sequence + 1):
                seq = sequence[i:i+max_sequence]
                if seq in password or seq[::-1] in password:
                    return True
        return False
    
    def _calculate_strength_score(self, password: str, has_upper: bool, 
                                has_lower: bool, has_digit: bool, 
                                has_special: bool) -> int:
        """计算密码强度分数 (0-100)"""
        score = 0
        
        # 长度分数 (最多30分)
        score += min(30, len(password) * 2)
        
        # 字符类型分数 (每种类型15分，最多60分)
        if has_upper:
            score += 15
        if has_lower:
            score += 15
        if has_digit:
            score += 15
        if has_special:
            score += 15
        
        # 复杂性分数 (最多10分)
        unique_chars = len(set(password))
        score += min(10, unique_chars)
        
        return min(100, score)
    
    def check_password_history(self, password: str, password_history: List[str]) -> bool:
        """
        检查密码是否在历史密码中使用过
        
        Args:
            password: 新密码
            password_history: 历史密码哈希列表
            
        Returns:
            bool: True表示密码已被使用过
        """
        for old_hash in password_history:
            if self.verify_password(password, old_hash):
                return True
        return False
    
    def is_password_expired(self, last_changed_date, max_age_days: int = 90) -> bool:
        """
        检查密码是否已过期
        
        Args:
            last_changed_date: 密码最后修改日期
            max_age_days: 密码最大有效天数
            
        Returns:
            bool: True表示密码已过期
        """
        from datetime import datetime, timezone, timedelta
        
        if not last_changed_date:
            return True
        
        if last_changed_date.tzinfo is None:
            last_changed_date = last_changed_date.replace(tzinfo=timezone.utc)
        
        expiry_date = last_changed_date + timedelta(days=max_age_days)
        return datetime.now(timezone.utc) > expiry_date