"""
UI组件配置PUT API合约测试

测试UI组件配置PUT端点的API合约兼容性。
测试组件配置的创建和更新功能。
"""
import pytest
import requests
import json
from typing import Dict, Any
from tests.ui.components import UIComponentTestBase


class TestUIComponentsPutContract(UIComponentTestBase):
    """UI组件配置PUT API合约测试类"""
    
    BASE_URL = "http://localhost:5001/api"
    
    def setup_method(self):
        """设置测试环境"""
        super().setup_method()
        self.endpoint = f"{self.BASE_URL}/ui/components"
    
    @pytest.mark.contract
    def test_put_component_config_create_success(self):
        """测试成功创建组件配置"""
        component_name = "test_button_create"
        url = f"{self.endpoint}/{component_name}"
        
        # 合约定义的请求数据
        request_data = {
            "component_type": "button",
            "config_data": {
                "theme": "primary",
                "size": "medium",
                "disabled": False
            },
            "user_id": 1,
            "is_active": True
        }
        
        response = requests.put(url, json=request_data)
        
        # 合约要求：201状态码（创建成功）
        assert response.status_code == 201, f"期望状态码201，实际 {response.status_code}"
        
        # 合约要求：返回JSON格式
        assert response.headers.get('Content-Type') == 'application/json'
        
        # 验证响应结构
        data = response.json()
        self._assert_component_config_response_schema(data)
        
        # 验证数据正确保存
        assert data['component_name'] == component_name
        assert data['component_type'] == request_data['component_type']
        assert data['config_data'] == request_data['config_data']
    
    @pytest.mark.contract
    def test_put_component_config_update_success(self):
        """测试成功更新组件配置"""
        component_name = "test_button_update"
        url = f"{self.endpoint}/{component_name}"
        
        # 首先创建配置
        create_data = {
            "component_type": "button",
            "config_data": {"theme": "primary"},
            "user_id": 1
        }
        requests.put(url, json=create_data)
        
        # 然后更新配置
        update_data = {
            "component_type": "button",
            "config_data": {"theme": "secondary", "size": "large"},
            "user_id": 1,
            "is_active": True
        }
        
        response = requests.put(url, json=update_data)
        
        # 合约要求：200状态码（更新成功）
        assert response.status_code == 200, f"期望状态码200，实际 {response.status_code}"
        
        data = response.json()
        self._assert_component_config_response_schema(data)
        
        # 验证更新后的数据
        assert data['config_data'] == update_data['config_data']
    
    @pytest.mark.contract
    def test_put_component_config_global(self):
        """测试创建全局组件配置（无user_id）"""
        component_name = "global_navigation"
        url = f"{self.endpoint}/{component_name}"
        
        request_data = {
            "component_type": "navigation",
            "config_data": {
                "style": "horizontal",
                "items": ["home", "dashboard", "settings"]
            },
            "is_active": True
        }
        
        response = requests.put(url, json=request_data)
        
        assert response.status_code in [200, 201]
        
        data = response.json()
        self._assert_component_config_response_schema(data)
        
        # 全局配置应该没有user_id或user_id为null
        assert data.get('user_id') is None
    
    @pytest.mark.contract
    def test_put_component_config_invalid_data(self):
        """测试无效数据验证"""
        component_name = "test_invalid"
        url = f"{self.endpoint}/{component_name}"
        
        invalid_requests = [
            # 缺少必需字段
            {},
            {"component_type": "button"},
            {"config_data": {}},
            
            # 无效字段类型
            {
                "component_type": 123,  # 应该是字符串
                "config_data": {}
            },
            {
                "component_type": "button",
                "config_data": "invalid"  # 应该是对象
            },
            
            # 无效字段值
            {
                "component_type": "invalid_type",  # 不在允许列表中
                "config_data": {}
            },
            {
                "component_type": "button",
                "config_data": {},
                "user_id": -1  # 无效用户ID
            }
        ]
        
        for invalid_data in invalid_requests:
            response = requests.put(url, json=invalid_data)
            
            # 合约要求：400状态码
            assert response.status_code == 400, f"无效数据应返回400: {invalid_data}"
            
            # 验证错误响应格式
            error_data = response.json()
            self._assert_error_response_schema(error_data)
    
    @pytest.mark.contract
    def test_put_component_config_invalid_name(self):
        """测试无效组件名称"""
        invalid_names = [
            "invalid name",  # 包含空格
            "invalid@name",  # 包含特殊字符
            "a" * 101,  # 超过长度限制
        ]
        
        request_data = {
            "component_type": "button",
            "config_data": {"theme": "primary"}
        }
        
        for invalid_name in invalid_names:
            url = f"{self.endpoint}/{invalid_name}"
            response = requests.put(url, json=request_data)
            
            # 合约要求：400或422状态码
            assert response.status_code in [400, 422]
    
    @pytest.mark.contract
    def test_put_component_config_large_config_data(self):
        """测试大型配置数据限制"""
        component_name = "test_large_config"
        url = f"{self.endpoint}/{component_name}"
        
        # 创建大于10KB的配置数据
        large_config = {"data": "x" * 15000}  # 超过10KB限制
        
        request_data = {
            "component_type": "card",
            "config_data": large_config
        }
        
        response = requests.put(url, json=request_data)
        
        # 合约要求：413状态码（数据过大）或400
        assert response.status_code in [400, 413]
    
    def _assert_component_config_response_schema(self, data: Dict[str, Any]):
        """断言ComponentConfigResponse schema合规性"""
        # 必需字段
        required_fields = ['id', 'component_name', 'component_type', 'config_data']
        for field in required_fields:
            assert field in data, f"响应缺少必需字段: {field}"
        
        # 字段类型验证
        assert isinstance(data['id'], int)
        assert isinstance(data['component_name'], str)
        assert isinstance(data['component_type'], str)
        assert isinstance(data['config_data'], dict)
        
        # 可选字段验证
        if 'user_id' in data:
            assert data['user_id'] is None or isinstance(data['user_id'], int)
        
        if 'created_at' in data:
            assert isinstance(data['created_at'], str)
        
        if 'updated_at' in data:
            assert isinstance(data['updated_at'], str)
    
    def _assert_error_response_schema(self, data: Dict[str, Any]):
        """断言ErrorResponse schema合规性"""
        assert 'error' in data
        assert 'message' in data
        assert isinstance(data['error'], str)
        assert isinstance(data['message'], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])