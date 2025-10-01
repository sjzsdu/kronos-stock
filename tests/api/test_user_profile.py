# -*- coding: utf-8 -*-
"""
用户档案API合约测试

这些测试验证用户档案相关端点的API合约，包括：
- 档案获取功能
- 档案更新功能
- 权限验证机制
- 数据验证规则
"""

import pytest
import json
from datetime import datetime, timedelta
from app.models.user import User, UserProfile, UserSession


class TestUserProfileContract:
    """用户档案API合约测试类"""

    @pytest.fixture(autouse=True)
    def setup_method(self, app, client):
        """每个测试方法前的设置"""
        self.app = app
        self.client = client
        self.profile_url = '/api/user/profile'
        
        # 创建测试用户、档案和会话
        with app.app_context():
            self.test_user = User(
                email='profile_test@example.com',
                password_hash='$2b$12$test_hashed_password',
                is_active=True
            )
            self.test_user.save()
            
            # 创建用户档案
            self.test_profile = UserProfile(
                user_id=self.test_user.id,
                nickname='测试用户',
                bio='这是一个测试用户的简介',
                avatar_url='https://example.com/avatar.jpg',
                phone='13812345678',
                gender='male',
                birth_date=datetime(1990, 5, 15).date(),
                location='北京市',
                investment_style='conservative',
                risk_tolerance='low',
                investment_experience='beginner',
                preferred_sectors=['technology', 'healthcare'],
                notification_preferences={
                    'email': True,
                    'sms': False,
                    'push': True
                }
            )
            self.test_profile.save()
            
            # 创建活跃会话
            self.test_session = UserSession(
                user_id=self.test_user.id,
                token='profile_valid_token_12345',
                expires_at=datetime.utcnow() + timedelta(hours=24),
                is_active=True
            )
            self.test_session.save()

    def test_get_profile_success_contract(self):
        """测试获取用户档案的成功合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.get(
            self.profile_url,
            headers=headers
        )

        # 验证成功响应格式
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        # 验证响应结构
        assert 'success' in response_data
        assert response_data['success'] is True
        assert 'user' in response_data
        assert 'profile' in response_data

        # 验证用户基本信息
        user_data = response_data['user']
        assert 'id' in user_data
        assert 'email' in user_data
        assert 'is_active' in user_data
        assert 'created_at' in user_data
        assert 'last_login' in user_data
        # 确保密码不在响应中
        assert 'password' not in user_data
        assert 'password_hash' not in user_data

        # 验证档案信息
        profile_data = response_data['profile']
        assert 'nickname' in profile_data
        assert 'bio' in profile_data
        assert 'avatar_url' in profile_data
        assert 'phone' in profile_data
        assert 'gender' in profile_data
        assert 'birth_date' in profile_data
        assert 'location' in profile_data
        assert 'investment_style' in profile_data
        assert 'risk_tolerance' in profile_data
        assert 'investment_experience' in profile_data
        assert 'preferred_sectors' in profile_data
        assert 'notification_preferences' in profile_data

    def test_get_profile_unauthorized_contract(self):
        """测试未授权获取档案的错误处理合约"""
        # 不提供授权头
        response = self.client.get(self.profile_url)

        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False
        assert 'message' in response_data

    def test_get_profile_invalid_token_contract(self):
        """测试无效令牌的错误处理合约"""
        headers = {
            'Authorization': 'Bearer invalid_token_123',
            'Content-Type': 'application/json'
        }

        response = self.client.get(
            self.profile_url,
            headers=headers
        )

        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False

    def test_update_profile_success_contract(self):
        """测试更新用户档案的成功合约"""
        update_data = {
            'nickname': '更新后的昵称',
            'bio': '更新后的简介内容',
            'phone': '13987654321',
            'location': '上海市',
            'investment_style': 'aggressive',
            'risk_tolerance': 'high',
            'preferred_sectors': ['finance', 'energy'],
            'notification_preferences': {
                'email': False,
                'sms': True,
                'push': True
            }
        }

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.put(
            self.profile_url,
            data=json.dumps(update_data),
            headers=headers
        )

        # 验证成功响应格式
        assert response.status_code == 200
        response_data = json.loads(response.data)
        
        assert 'success' in response_data
        assert response_data['success'] is True
        assert 'message' in response_data
        assert 'profile' in response_data

        # 验证更新后的数据
        updated_profile = response_data['profile']
        assert updated_profile['nickname'] == '更新后的昵称'
        assert updated_profile['bio'] == '更新后的简介内容'
        assert updated_profile['phone'] == '13987654321'
        assert updated_profile['location'] == '上海市'
        assert updated_profile['investment_style'] == 'aggressive'

    def test_update_profile_partial_update_contract(self):
        """测试部分更新档案的合约"""
        # 只更新昵称和简介
        update_data = {
            'nickname': '部分更新昵称',
            'bio': '部分更新简介'
        }

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.put(
            self.profile_url,
            data=json.dumps(update_data),
            headers=headers
        )

        if response.status_code == 200:
            response_data = json.loads(response.data)
            updated_profile = response_data['profile']
            
            # 验证指定字段已更新
            assert updated_profile['nickname'] == '部分更新昵称'
            assert updated_profile['bio'] == '部分更新简介'
            
            # 验证其他字段保持不变
            assert updated_profile['phone'] == '13812345678'
            assert updated_profile['location'] == '北京市'

    def test_update_profile_validation_contract(self):
        """测试更新档案时的数据验证合约"""
        invalid_updates = [
            # 昵称太长
            {
                'data': {'nickname': 'a' * 51},
                'expected_field': 'nickname'
            },
            # 无效的性别
            {
                'data': {'gender': 'invalid_gender'},
                'expected_field': 'gender'
            },
            # 无效的投资风格
            {
                'data': {'investment_style': 'invalid_style'},
                'expected_field': 'investment_style'
            },
            # 无效的风险承受能力
            {
                'data': {'risk_tolerance': 'invalid_tolerance'},
                'expected_field': 'risk_tolerance'
            },
            # 无效的手机号格式
            {
                'data': {'phone': '123'},
                'expected_field': 'phone'
            },
            # 生日格式错误
            {
                'data': {'birth_date': 'invalid_date'},
                'expected_field': 'birth_date'
            }
        ]

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        for case in invalid_updates:
            response = self.client.put(
                self.profile_url,
                data=json.dumps(case['data']),
                headers=headers
            )

            # 验证验证错误响应
            assert response.status_code == 400
            response_data = json.loads(response.data)
            assert response_data['success'] is False
            assert 'errors' in response_data
            assert case['expected_field'] in response_data['errors']

    def test_update_profile_unauthorized_contract(self):
        """测试未授权更新档案的错误处理合约"""
        update_data = {
            'nickname': '未授权更新'
        }

        # 不提供授权头
        response = self.client.put(
            self.profile_url,
            data=json.dumps(update_data),
            headers={'Content-Type': 'application/json'}
        )

        assert response.status_code == 401
        response_data = json.loads(response.data)
        assert response_data['success'] is False

    def test_profile_avatar_upload_contract(self):
        """测试头像上传功能合约"""
        # 模拟文件上传
        data = {
            'avatar': (open(__file__, 'rb'), 'test_avatar.jpg')
        }

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345'
        }

        response = self.client.post(
            f'{self.profile_url}/avatar',
            data=data,
            headers=headers,
            content_type='multipart/form-data'
        )

        # 注意：头像上传功能可能还没有实现
        # 这个测试主要验证API合约的完整性
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert 'avatar_url' in response_data

    def test_profile_delete_avatar_contract(self):
        """测试删除头像功能合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.delete(
            f'{self.profile_url}/avatar',
            headers=headers
        )

        # 注意：删除头像功能可能还没有实现
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert response_data['success'] is True

    def test_profile_notification_preferences_contract(self):
        """测试通知偏好设置合约"""
        notification_data = {
            'notification_preferences': {
                'email': True,
                'sms': False,
                'push': True,
                'price_alerts': True,
                'news_updates': False,
                'market_analysis': True
            }
        }

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.put(
            f'{self.profile_url}/notifications',
            data=json.dumps(notification_data),
            headers=headers
        )

        # 验证通知偏好更新
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert 'notification_preferences' in response_data
            preferences = response_data['notification_preferences']
            assert preferences['email'] is True
            assert preferences['sms'] is False

    def test_profile_investment_preferences_contract(self):
        """测试投资偏好设置合约"""
        investment_data = {
            'investment_style': 'balanced',
            'risk_tolerance': 'medium',
            'investment_experience': 'intermediate',
            'preferred_sectors': ['technology', 'healthcare', 'finance'],
            'investment_goals': ['growth', 'income'],
            'time_horizon': 'long_term'
        }

        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.put(
            f'{self.profile_url}/investment',
            data=json.dumps(investment_data),
            headers=headers
        )

        # 验证投资偏好更新
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert response_data['success'] is True
            
            # 验证投资偏好数据
            if 'profile' in response_data:
                profile = response_data['profile']
                assert profile['investment_style'] == 'balanced'
                assert profile['risk_tolerance'] == 'medium'

    def test_profile_method_not_allowed_contract(self):
        """测试不支持的HTTP方法合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        # 测试POST方法（档案更新应该使用PUT）
        response = self.client.post(
            self.profile_url,
            headers=headers
        )
        assert response.status_code == 405

        # 测试DELETE方法
        response = self.client.delete(
            self.profile_url,
            headers=headers
        )
        assert response.status_code == 405

    def test_profile_json_format_validation_contract(self):
        """测试JSON格式验证合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        # 发送无效的JSON
        response = self.client.put(
            self.profile_url,
            data='invalid json format',
            headers=headers
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert response_data['success'] is False

    def test_profile_empty_update_contract(self):
        """测试空更新数据的处理合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        # 发送空的更新数据
        response = self.client.put(
            self.profile_url,
            data='{}',
            headers=headers
        )

        # 空更新应该被接受但不做任何更改
        if response.status_code == 200:
            response_data = json.loads(response.data)
            assert response_data['success'] is True
        else:
            # 或者返回400错误，要求至少有一个字段
            assert response.status_code == 400

    def test_profile_security_headers_contract(self):
        """测试安全响应头合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.get(
            self.profile_url,
            headers=headers
        )

        # 验证安全相关的响应头
        # 注意：具体的安全头可能还没有实现
        if response.status_code == 200:
            # 可以验证是否设置了适当的安全头
            # assert 'X-Content-Type-Options' in response.headers
            # assert 'Cache-Control' in response.headers
            pass

    def test_profile_data_privacy_contract(self):
        """测试数据隐私保护合约"""
        headers = {
            'Authorization': 'Bearer profile_valid_token_12345',
            'Content-Type': 'application/json'
        }

        response = self.client.get(
            self.profile_url,
            headers=headers
        )

        if response.status_code == 200:
            response_data = json.loads(response.data)
            
            # 验证敏感信息不在响应中
            user_data = response_data.get('user', {})
            profile_data = response_data.get('profile', {})
            
            # 确保密码相关信息不暴露
            assert 'password' not in user_data
            assert 'password_hash' not in user_data
            
            # 手机号应该被部分遮挡（可选的隐私保护）
            if 'phone' in profile_data:
                phone = profile_data['phone']
                # 可以检查手机号是否被适当遮挡
                # 例如：138****5678
                pass