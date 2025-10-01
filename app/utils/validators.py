# -*- coding: utf-8 -*-
"""
数据验证工具
提供邮箱、密码、用户输入等验证功能
"""

import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
        
    Returns:
        是否有效
    """
    if not email or len(email) > 254:
        return False
    
    # 基本邮箱格式验证 - 不允许连续的点号
    # 检查是否有连续的点号
    if '..' in email:
        return False
    
    # 检查开头和结尾不能是点号
    local_part = email.split('@')[0] if '@' in email else email
    if local_part.startswith('.') or local_part.endswith('.'):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password: str) -> Tuple[bool, str]:
    """
    验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        (是否有效, 错误消息)
    """
    if not password:
        return False, "密码不能为空"
    
    if len(password) < 8:
        return False, "密码至少需要8个字符"
    
    if len(password) > 128:
        return False, "密码不能超过128个字符"
    
    # 检查是否包含数字
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    # 检查是否包含字母
    if not re.search(r'[a-zA-Z]', password):
        return False, "密码必须包含至少一个字母"
    
    # 检查是否包含特殊字符（可选但推荐）
    special_chars = r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\\/~`]'
    if not re.search(special_chars, password):
        return False, "密码建议包含特殊字符以提高安全性"
    
    return True, "密码强度符合要求"


def validate_phone(phone: str) -> bool:
    """
    验证手机号格式（中国大陆）
    
    Args:
        phone: 手机号
        
    Returns:
        是否有效
    """
    if not phone:
        return True  # 手机号可选
    
    # 中国大陆手机号格式
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_stock_code(stock_code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        stock_code: 股票代码
        
    Returns:
        是否有效
    """
    if not stock_code:
        return False
    
    # 6位数字股票代码
    pattern = r'^\d{6}$'
    return bool(re.match(pattern, stock_code))


def validate_username(username: str) -> Tuple[bool, str]:
    """
    验证用户名格式
    
    Args:
        username: 用户名
        
    Returns:
        (是否有效, 错误消息)
    """
    if not username:
        return False, "用户名不能为空"
    
    if len(username) < 2:
        return False, "用户名至少需要2个字符"
    
    if len(username) > 50:
        return False, "用户名不能超过50个字符"
    
    # 只允许字母、数字、中文、下划线、连字符
    pattern = r'^[\w\u4e00-\u9fff\-]+$'
    if not re.match(pattern, username):
        return False, "用户名只能包含字母、数字、中文、下划线和连字符"
    
    return True, "用户名格式正确"


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    清理用户输入
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 去除首尾空白
    text = text.strip()
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    
    # 移除潜在的恶意字符
    dangerous_patterns = [
        r'<script.*?</script>',  # JavaScript
        r'<.*?javascript:.*?>',   # JavaScript链接
        r'on\w+\s*=',            # 事件处理器
    ]
    
    for pattern in dangerous_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text


def validate_investment_experience(experience: str) -> bool:
    """
    验证投资经验值
    
    Args:
        experience: 投资经验
        
    Returns:
        是否有效
    """
    valid_experiences = ['新手', '初级', '中级', '高级', '专业']
    return experience in valid_experiences


def validate_risk_preference(risk_pref: str) -> bool:
    """
    验证风险偏好值
    
    Args:
        risk_pref: 风险偏好
        
    Returns:
        是否有效
    """
    valid_preferences = ['保守型', '稳健型', '平衡型', '积极型', '激进型']
    return risk_pref in valid_preferences


def validate_gender(gender: str) -> bool:
    """
    验证性别值
    
    Args:
        gender: 性别
        
    Returns:
        是否有效
    """
    valid_genders = ['男', '女', '其他', '不愿透露']
    return gender in valid_genders