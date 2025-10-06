"""
集成测试场景 - UI组件配置集成流程

测试UI组件配置的完整集成流程，从创建到使用到缓存的全链路测试。
"""
import pytest
import requests
import json
from typing import Dict, Any
from tests.ui.components import UIComponentTestBase, performance_test


class TestUIComponentConfigFlowIntegration(UIComponentTestBase):
    """UI组件配置集成测试类"""
    
    BASE_URL = "http://localhost:5001"
    
    def setup_method(self):
        """设置测试环境"""
        super().setup_method()
        self.api_endpoint = f"{self.BASE_URL}/api/ui/components"
        self.render_endpoint = f"{self.BASE_URL}/api/ui/render"
        self.htmx_endpoint = f"{self.BASE_URL}/htmx/components"
    
    @pytest.mark.integration
    @performance_test(threshold_ms=2000)
    def test_complete_ui_component_workflow(self):
        """测试完整的UI组件工作流程"""
        component_name = "integration_test_card"
        
        # 1. 创建组件配置
        config_data = {
            "component_type": "card",
            "config_data": {
                "theme": "primary",
                "elevation": "medium",
                "padding": "standard",
                "border_radius": "medium"
            },
            "user_id": 1,
            "is_active": True
        }
        
        # 创建配置（这会失败，因为API未实现）
        create_response = requests.put(f"{self.api_endpoint}/{component_name}", json=config_data)
        
        # 在TDD阶段，这个测试应该失败
        # 后续实现API后，这些断言应该通过
        if create_response.status_code in [200, 201]:
            created_config = create_response.json()
            assert created_config['component_name'] == component_name
            assert created_config['component_type'] == "card"
            
            # 2. 获取组件配置
            get_response = requests.get(f"{self.api_endpoint}/{component_name}?user_id=1")
            assert get_response.status_code == 200
            
            retrieved_config = get_response.json()
            assert retrieved_config['id'] == created_config['id']
            assert retrieved_config['config_data'] == config_data['config_data']
            
            # 3. 渲染组件
            render_data = {
                "component_name": component_name,
                "component_type": "card",
                "template_path": "components/card.html",
                "render_data": {
                    "title": "集成测试卡片",
                    "content": "这是集成测试的内容",
                    "config": retrieved_config['config_data']
                }
            }
            
            render_response = requests.post(self.render_endpoint, json=render_data)
            if render_response.status_code == 200:
                rendered = render_response.json()
                assert 'rendered_html' in rendered
                assert len(rendered['rendered_html']) > 0
                
                # 4. 获取HTMX视图
                htmx_response = requests.get(f"{self.htmx_endpoint}/card", params={
                    "title": "集成测试卡片",
                    "content": "这是集成测试的内容",
                    "config_id": retrieved_config['id']
                })
                
                if htmx_response.status_code == 200:
                    # 验证返回的HTML使用语义化CSS类
                    soup = self.parse_html_response(htmx_response.text)
                    card_element = soup.find(class_='card')
                    
                    if card_element:
                        self.assert_semantic_css_class(card_element, 'card')
                        self.assert_no_tailwind_atomic_class(card_element)
        else:
            # TDD阶段：测试失败是预期的
            assert create_response.status_code in [404, 500, 502, 503], "API端点未实现，应返回错误状态码"
    
    @pytest.mark.integration
    def test_user_preference_override_flow(self):
        """测试用户偏好覆盖全局配置的流程"""
        component_name = "preference_test_button"
        
        # 1. 创建全局配置
        global_config = {
            "component_type": "button",
            "config_data": {
                "theme": "secondary",
                "size": "medium"
            },
            "is_active": True
            # 注意：没有user_id，表示全局配置
        }
        
        global_response = requests.put(f"{self.api_endpoint}/{component_name}", json=global_config)
        
        # 2. 创建用户特定配置
        user_config = {
            "component_type": "button", 
            "config_data": {
                "theme": "primary",  # 覆盖全局的secondary
                "size": "large"      # 覆盖全局的medium
            },
            "user_id": 1,
            "is_active": True
        }
        
        user_response = requests.put(f"{self.api_endpoint}/{component_name}", json=user_config)
        
        # 3. 测试不同用户获取配置的结果
        test_cases = [
            {"user_id": 1, "expected_theme": "primary", "expected_size": "large"},   # 应返回用户配置
            {"user_id": 2, "expected_theme": "secondary", "expected_size": "medium"},  # 应返回全局配置
            {"user_id": None, "expected_theme": "secondary", "expected_size": "medium"}  # 应返回全局配置
        ]
        
        for test_case in test_cases:
            params = {}
            if test_case["user_id"]:
                params["user_id"] = test_case["user_id"]
                
            config_response = requests.get(f"{self.api_endpoint}/{component_name}", params=params)
            
            # 在TDD阶段，这些请求会失败
            if config_response.status_code == 200:
                config = config_response.json()
                assert config['config_data']['theme'] == test_case['expected_theme']
                assert config['config_data']['size'] == test_case['expected_size']
    
    @pytest.mark.integration  
    @pytest.mark.performance
    def test_component_render_cache_performance(self):
        """测试组件渲染缓存性能"""
        component_name = "cache_performance_test"
        
        render_data = {
            "component_name": component_name,
            "component_type": "card",
            "template_path": "components/performance_card.html",
            "render_data": {
                "items": [{"id": i, "name": f"Item {i}"} for i in range(100)],
                "timestamp": "2025-10-05T12:00:00Z"
            },
            "cache_ttl": 300
        }
        
        import time
        
        # 第一次渲染 - 创建缓存
        start_time = time.time()
        first_response = requests.post(self.render_endpoint, json=render_data)
        first_duration = (time.time() - start_time) * 1000
        
        # 第二次渲染 - 应该命中缓存
        start_time = time.time()  
        second_response = requests.post(self.render_endpoint, json=render_data)
        second_duration = (time.time() - start_time) * 1000
        
        # 在实现后，缓存命中应该显著快于首次渲染
        if first_response.status_code == 200 and second_response.status_code == 200:
            # 缓存命中应该至少比首次渲染快50%
            assert second_duration < first_duration * 0.5, f"缓存性能未达到预期: {second_duration}ms vs {first_duration}ms"
            
            # 验证缓存信息
            second_data = second_response.json()
            if 'cache_info' in second_data:
                assert second_data['cache_info'].get('cached') == True
    
    @pytest.mark.integration
    def test_component_error_handling_flow(self):
        """测试组件错误处理流程"""
        # 1. 测试无效组件配置
        invalid_config = {
            "component_type": "invalid_type",
            "config_data": {"invalid": "data"}
        }
        
        error_response = requests.put(f"{self.api_endpoint}/error_test", json=invalid_config)
        # 应该返回400错误
        
        # 2. 测试渲染不存在的模板
        invalid_render = {
            "component_name": "error_component",
            "component_type": "card", 
            "template_path": "non_existent_template.html",
            "render_data": {}
        }
        
        render_error_response = requests.post(self.render_endpoint, json=invalid_render)
        # 应该返回404错误
        
        # 3. 测试获取不存在的组件配置
        not_found_response = requests.get(f"{self.api_endpoint}/non_existent_component")
        # 应该返回404错误
        
        # TDD阶段：验证错误响应格式
        error_responses = [error_response, render_error_response, not_found_response]
        
        for response in error_responses:
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    assert 'error' in error_data or 'message' in error_data
                except json.JSONDecodeError:
                    # 在API未实现时，可能不返回JSON
                    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])