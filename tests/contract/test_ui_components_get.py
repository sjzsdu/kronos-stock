"""
UI组件配置GET API合约测试

测试UI组件配置GET端点的API合约兼容性。
这个测试必须先失败，然后通过实现API端点来使其通过。
"""
import pytest
import requests
import json
from typing import Dict, Any
from tests.ui.components import UIComponentTestBase


class TestUIComponentsGetContract(UIComponentTestBase):
    """UI组件配置GET API合约测试类"""
    
    BASE_URL = "http://localhost:5001/api"
    
    def setup_method(self):
        """设置测试环境"""
        super().setup_method()
        self.endpoint = f"{self.BASE_URL}/ui/components"
    
    @pytest.mark.contract
    def test_get_component_config_success(self):
        """测试成功获取组件配置 - 合约验证"""
        # 这个测试现在会失败，因为端点还未实现
        component_name = "login_form"
        url = f"{self.endpoint}/{component_name}"
        
        # 发送GET请求
        response = requests.get(url)
        
        # 合约要求：状态码200
        assert response.status_code == 200, f"期望状态码200，实际 {response.status_code}"
        
        # 合约要求：返回JSON格式
        assert response.headers.get('Content-Type') == 'application/json'
        
        # 合约要求：响应结构符合ComponentConfigResponse schema
        data = response.json()
        self._assert_component_config_response_schema(data)
    
    @pytest.mark.contract
    def test_get_component_config_with_user_id(self):
        """测试带用户ID的组件配置获取"""
        component_name = "dashboard_card"
        user_id = 1
        url = f"{self.endpoint}/{component_name}?user_id={user_id}"
        
        response = requests.get(url)
        
        # 合约验证
        assert response.status_code == 200
        assert response.headers.get('Content-Type') == 'application/json'
        
        data = response.json()
        self._assert_component_config_response_schema(data)
        
        # 验证返回的配置包含用户特定数据
        assert data.get('user_id') == user_id or data.get('user_id') is None
    
    @pytest.mark.contract
    def test_get_component_config_not_found(self):
        """测试组件配置不存在的情况"""
        component_name = "non_existent_component"
        url = f"{self.endpoint}/{component_name}"
        
        response = requests.get(url)
        
        # 合约要求：404状态码
        assert response.status_code == 404
        assert response.headers.get('Content-Type') == 'application/json'
        
        data = response.json()
        self._assert_error_response_schema(data)
    
    @pytest.mark.contract  
    def test_get_component_config_invalid_name(self):
        """测试无效组件名称"""
        invalid_names = [
            "invalid name with spaces",
            "invalid@name",
            "a" * 101,  # 超过长度限制
            ""
        ]
        
        for invalid_name in invalid_names:
            url = f"{self.endpoint}/{invalid_name}"
            response = requests.get(url)
            
            # 合约要求：400或422状态码
            assert response.status_code in [400, 422], f"无效名称 {invalid_name} 应返回400或422"
    
    @pytest.mark.contract
    def test_get_component_config_invalid_user_id(self):
        """测试无效用户ID"""
        component_name = "test_component"
        invalid_user_ids = [0, -1, "invalid", 999999999]
        
        for invalid_user_id in invalid_user_ids:
            url = f"{self.endpoint}/{component_name}?user_id={invalid_user_id}"
            response = requests.get(url)
            
            # 合约要求：400状态码或忽略无效参数返回200
            assert response.status_code in [200, 400, 422]
    
    def _assert_component_config_response_schema(self, data: Dict[str, Any]):
        """断言ComponentConfigResponse schema合规性"""
        # 必需字段
        required_fields = ['id', 'component_name', 'component_type', 'config_data']
        for field in required_fields:
            assert field in data, f"响应缺少必需字段: {field}"
        
        # 字段类型验证
        assert isinstance(data['id'], int), "id必须是整数"
        assert isinstance(data['component_name'], str), "component_name必须是字符串"
        assert isinstance(data['component_type'], str), "component_type必须是字符串"
        assert isinstance(data['config_data'], dict), "config_data必须是对象"
        
        # 可选字段验证
        if 'user_id' in data:
            assert data['user_id'] is None or isinstance(data['user_id'], int)
        
        if 'is_active' in data:
            assert isinstance(data['is_active'], bool)
        
        if 'version' in data:
            assert isinstance(data['version'], int)
        
        # 业务规则验证
        valid_component_types = ['form', 'button', 'card', 'navigation', 'modal', 'notification']
        assert data['component_type'] in valid_component_types, f"component_type必须是有效值: {valid_component_types}"
    
    def _assert_error_response_schema(self, data: Dict[str, Any]):
        """断言ErrorResponse schema合规性"""
        # 必需字段
        assert 'error' in data, "错误响应必须包含error字段"
        assert 'message' in data, "错误响应必须包含message字段"
        
        # 字段类型验证
        assert isinstance(data['error'], str), "error必须是字符串"
        assert isinstance(data['message'], str), "message必须是字符串"
        
        # 可选字段验证
        if 'code' in data:
            assert isinstance(data['code'], (str, int))


# 测试运行配置
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])