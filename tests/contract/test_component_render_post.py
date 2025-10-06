"""
组件渲染POST API合约测试

测试组件渲染POST端点的API合约兼容性。
测试动态组件渲染和缓存功能。
"""
import pytest
import requests
import json
from typing import Dict, Any
from tests.ui.components import UIComponentTestBase


class TestComponentRenderPostContract(UIComponentTestBase):
    """组件渲染POST API合约测试类"""
    
    BASE_URL = "http://localhost:5001/api"
    
    def setup_method(self):
        """设置测试环境"""
        super().setup_method()
        self.endpoint = f"{self.BASE_URL}/ui/render"
    
    @pytest.mark.contract
    def test_render_component_success(self):
        """测试成功渲染组件"""
        request_data = {
            "component_name": "user_card",
            "component_type": "card",
            "template_path": "components/user_card.html",
            "render_data": {
                "user": {
                    "name": "张三",
                    "email": "zhangsan@example.com",
                    "avatar_url": "/static/images/default_avatar.png"
                },
                "show_actions": True
            },
            "cache_ttl": 300  # 5分钟缓存
        }
        
        response = requests.post(self.endpoint, json=request_data)
        
        # 合约要求：200状态码
        assert response.status_code == 200, f"期望状态码200，实际 {response.status_code}"
        
        # 合约要求：返回JSON格式
        assert response.headers.get('Content-Type') == 'application/json'
        
        # 验证响应结构
        data = response.json()
        self._assert_render_response_schema(data)
        
        # 验证渲染结果
        assert 'rendered_html' in data
        assert len(data['rendered_html']) > 0
        
        # 验证缓存信息
        if 'cache_info' in data:
            assert 'cache_key' in data['cache_info']
            assert 'cached' in data['cache_info']
    
    @pytest.mark.contract
    def test_render_component_with_cache_hit(self):
        """测试缓存命中的组件渲染"""
        request_data = {
            "component_name": "navigation_menu",
            "component_type": "navigation", 
            "template_path": "components/navigation_menu.html",
            "render_data": {
                "menu_items": [
                    {"name": "首页", "url": "/"},
                    {"name": "仪表板", "url": "/dashboard"}
                ]
            },
            "cache_ttl": 600
        }
        
        # 第一次渲染 - 创建缓存
        first_response = requests.post(self.endpoint, json=request_data)
        assert first_response.status_code == 200
        
        # 第二次渲染 - 应该命中缓存
        second_response = requests.post(self.endpoint, json=request_data)
        assert second_response.status_code == 200
        
        second_data = second_response.json()
        self._assert_render_response_schema(second_data)
        
        # 验证缓存命中
        if 'cache_info' in second_data:
            assert second_data['cache_info'].get('cached') == True
    
    @pytest.mark.contract
    def test_render_component_no_cache(self):
        """测试不使用缓存的组件渲染"""
        request_data = {
            "component_name": "live_chart",
            "component_type": "chart",
            "template_path": "components/live_chart.html",
            "render_data": {
                "chart_data": [1, 2, 3, 4, 5],
                "timestamp": "2025-10-05T12:00:00Z"
            },
            "use_cache": False
        }
        
        response = requests.post(self.endpoint, json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        self._assert_render_response_schema(data)
        
        # 验证不使用缓存
        if 'cache_info' in data:
            assert data['cache_info'].get('cached') == False
    
    @pytest.mark.contract
    def test_render_component_invalid_template(self):
        """测试无效模板路径"""
        request_data = {
            "component_name": "test_component",
            "component_type": "card",
            "template_path": "non_existent_template.html",
            "render_data": {}
        }
        
        response = requests.post(self.endpoint, json=request_data)
        
        # 合约要求：404状态码（模板不存在）
        assert response.status_code == 404
        
        error_data = response.json()
        self._assert_error_response_schema(error_data)
        assert "template" in error_data['message'].lower()
    
    @pytest.mark.contract
    def test_render_component_template_error(self):
        """测试模板渲染错误"""
        request_data = {
            "component_name": "error_component", 
            "component_type": "card",
            "template_path": "components/invalid_syntax.html",  # 假设有语法错误的模板
            "render_data": {
                "invalid_reference": "{{ undefined_variable }}"
            }
        }
        
        response = requests.post(self.endpoint, json=request_data)
        
        # 合约要求：500状态码（服务器内部错误）或422（模板错误）
        assert response.status_code in [422, 500]
        
        error_data = response.json()
        self._assert_error_response_schema(error_data)
    
    @pytest.mark.contract
    def test_render_component_invalid_request_data(self):
        """测试无效请求数据"""
        invalid_requests = [
            # 缺少必需字段
            {},
            {"component_name": "test"},
            {"component_type": "card"},
            {"template_path": "test.html"},
            
            # 无效字段类型
            {
                "component_name": 123,  # 应该是字符串
                "component_type": "card",
                "template_path": "test.html",
                "render_data": {}
            },
            {
                "component_name": "test",
                "component_type": "card",
                "template_path": "test.html",
                "render_data": "invalid"  # 应该是对象
            },
            
            # 无效字段值
            {
                "component_name": "",  # 空字符串
                "component_type": "card",
                "template_path": "test.html", 
                "render_data": {}
            },
            {
                "component_name": "test",
                "component_type": "invalid_type",  # 无效组件类型
                "template_path": "test.html",
                "render_data": {}
            }
        ]
        
        for invalid_data in invalid_requests:
            response = requests.post(self.endpoint, json=invalid_data)
            
            # 合约要求：400状态码
            assert response.status_code == 400, f"无效数据应返回400: {invalid_data}"
            
            error_data = response.json()
            self._assert_error_response_schema(error_data)
    
    @pytest.mark.contract
    def test_render_component_performance(self):
        """测试组件渲染性能要求"""
        request_data = {
            "component_name": "complex_table",
            "component_type": "table",
            "template_path": "components/data_table.html",
            "render_data": {
                "rows": [{"id": i, "name": f"Item {i}"} for i in range(100)],
                "columns": ["id", "name"],
                "pagination": {"page": 1, "size": 20}
            }
        }
        
        import time
        start_time = time.time()
        
        response = requests.post(self.endpoint, json=request_data)
        
        end_time = time.time()
        render_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        # 合约要求：渲染时间小于500ms
        assert render_time < 500, f"渲染时间过长: {render_time:.2f}ms > 500ms"
        
        assert response.status_code == 200
    
    def _assert_render_response_schema(self, data: Dict[str, Any]):
        """断言渲染响应schema合规性"""
        # 必需字段
        required_fields = ['rendered_html', 'component_name', 'render_time_ms']
        for field in required_fields:
            assert field in data, f"响应缺少必需字段: {field}"
        
        # 字段类型验证
        assert isinstance(data['rendered_html'], str)
        assert isinstance(data['component_name'], str)
        assert isinstance(data['render_time_ms'], (int, float))
        
        # 可选字段验证
        if 'cache_info' in data:
            cache_info = data['cache_info']
            assert isinstance(cache_info, dict)
            if 'cache_key' in cache_info:
                assert isinstance(cache_info['cache_key'], str)
            if 'cached' in cache_info:
                assert isinstance(cache_info['cached'], bool)
    
    def _assert_error_response_schema(self, data: Dict[str, Any]):
        """断言错误响应schema合规性"""
        assert 'error' in data
        assert 'message' in data
        assert isinstance(data['error'], str)
        assert isinstance(data['message'], str)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])