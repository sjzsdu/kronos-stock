"""
HTMX组件HTML视图GET合约测试

测试HTMX组件HTML视图端点的合约兼容性。
验证返回的HTML内容使用语义化CSS类。
"""
import pytest
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from tests.ui.components import UIComponentTestBase, semantic_css_required


class TestHTMXComponentsGetContract(UIComponentTestBase):
    """HTMX组件HTML视图GET合约测试类"""
    
    BASE_URL = "http://localhost:5001"
    
    def setup_method(self):
        """设置测试环境"""
        super().setup_method()
        self.endpoint = f"{self.BASE_URL}/htmx/components"
    
    @pytest.mark.contract
    @semantic_css_required
    def test_get_button_component_html(self):
        """测试获取按钮组件HTML"""
        url = f"{self.endpoint}/button"
        params = {
            "text": "提交",
            "type": "primary",
            "size": "medium",
            "hx-post": "/api/submit"
        }
        
        response = requests.get(url, params=params)
        
        # 合约要求：200状态码
        assert response.status_code == 200
        
        # 合约要求：返回HTML格式
        assert 'text/html' in response.headers.get('Content-Type', '')
        
        # 解析HTML内容
        soup = self.parse_html_response(response.text)
        
        # 验证按钮结构
        button = soup.find('button')
        assert button is not None, "未找到button元素"
        
        # 验证语义化CSS类使用
        self.assert_semantic_css_class(button, 'btn')
        self.assert_semantic_css_class(button, 'btn-primary')
        self.assert_semantic_css_class(button, 'btn-medium')
        
        # 验证不使用TailwindCSS原子类
        self.assert_no_tailwind_atomic_class(button)
        
        # 验证HTMX属性
        assert button.get('hx-post') == "/api/submit"
        
        # 验证按钮文本
        assert button.get_text().strip() == "提交"
    
    @pytest.mark.contract
    @semantic_css_required
    def test_get_form_input_component_html(self):
        """测试获取表单输入组件HTML"""
        url = f"{self.endpoint}/form-input"
        params = {
            "name": "username",
            "type": "text",
            "placeholder": "请输入用户名",
            "required": "true",
            "label": "用户名"
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        assert 'text/html' in response.headers.get('Content-Type', '')
        
        soup = self.parse_html_response(response.text)
        
        # 验证表单组件结构
        form_group = soup.find(class_='form-group')
        assert form_group is not None, "未找到form-group容器"
        
        # 验证标签
        label = form_group.find('label')
        assert label is not None
        self.assert_semantic_css_class(label, 'form-label')
        assert label.get_text().strip() == "用户名"
        
        # 验证输入框
        input_field = form_group.find('input')
        assert input_field is not None
        self.assert_semantic_css_class(input_field, 'form-input')
        self.assert_no_tailwind_atomic_class(input_field)
        
        # 验证输入框属性
        assert input_field.get('name') == "username"
        assert input_field.get('type') == "text"
        assert input_field.get('placeholder') == "请输入用户名"
        assert input_field.has_attr('required')
    
    @pytest.mark.contract
    @semantic_css_required
    def test_get_card_component_html(self):
        """测试获取卡片组件HTML"""
        url = f"{self.endpoint}/card"
        params = {
            "title": "股票预测结果",
            "content": "基于AI模型的预测数据显示...",
            "has_header": "true",
            "has_footer": "true",
            "actions": "保存,分享"
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        
        soup = self.parse_html_response(response.text)
        
        # 验证卡片结构
        card = soup.find(class_='card')
        assert card is not None, "未找到card容器"
        
        # 验证语义化CSS类
        self.assert_semantic_css_class(card, 'card')
        self.assert_no_tailwind_atomic_class(card)
        
        # 验证卡片头部
        card_header = card.find(class_='card-header')
        assert card_header is not None
        self.assert_semantic_css_class(card_header, 'card-header')
        
        title = card_header.find('h3')
        assert title is not None
        assert title.get_text().strip() == "股票预测结果"
        
        # 验证卡片主体
        card_body = card.find(class_='card-body')
        assert card_body is not None
        self.assert_semantic_css_class(card_body, 'card-body')
        
        # 验证卡片底部
        card_footer = card.find(class_='card-footer')
        assert card_footer is not None
        self.assert_semantic_css_class(card_footer, 'card-footer')
    
    @pytest.mark.contract
    @semantic_css_required
    def test_get_modal_component_html(self):
        """测试获取模态框组件HTML"""
        url = f"{self.endpoint}/modal"
        params = {
            "title": "确认删除",
            "content": "您确定要删除这个预测记录吗？",
            "show_close": "true",
            "buttons": "取消,确认"
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        
        soup = self.parse_html_response(response.text)
        
        # 验证模态框结构
        modal = soup.find(class_='modal')
        assert modal is not None, "未找到modal容器"
        
        # 验证语义化CSS类
        self.assert_semantic_css_class(modal, 'modal')
        self.assert_no_tailwind_atomic_class(modal)
        
        # 验证模态框对话框
        modal_dialog = modal.find(class_='modal-dialog')
        assert modal_dialog is not None
        self.assert_semantic_css_class(modal_dialog, 'modal-dialog')
        
        # 验证模态框内容
        modal_content = modal_dialog.find(class_='modal-content')
        assert modal_content is not None
        self.assert_semantic_css_class(modal_content, 'modal-content')
    
    @pytest.mark.contract
    def test_get_navigation_component_html(self):
        """测试获取导航组件HTML"""
        url = f"{self.endpoint}/navigation"
        params = {
            "items": "首页:/,仪表板:/dashboard,设置:/settings",
            "active_item": "dashboard",
            "style": "horizontal"
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        
        soup = self.parse_html_response(response.text)
        
        # 验证导航结构
        nav = soup.find('nav', class_='nav')
        assert nav is not None, "未找到nav容器"
        
        # 验证语义化CSS类
        self.assert_semantic_css_class(nav, 'nav')
        self.assert_no_tailwind_atomic_class(nav)
        
        # 验证导航项
        nav_items = nav.find_all(class_='nav-item')
        assert len(nav_items) >= 3, "导航项数量不足"
        
        # 验证激活状态
        active_item = nav.find(class_='nav-item-active')
        assert active_item is not None, "未找到激活的导航项"
    
    @pytest.mark.contract
    def test_get_component_invalid_type(self):
        """测试无效组件类型"""
        invalid_types = [
            "non_existent_component",
            "invalid-component",
            "",
            "component_with_very_long_name_that_exceeds_limits"
        ]
        
        for invalid_type in invalid_types:
            url = f"{self.endpoint}/{invalid_type}"
            response = requests.get(url)
            
            # 合约要求：404状态码
            assert response.status_code == 404, f"无效组件类型 {invalid_type} 应返回404"
    
    @pytest.mark.contract
    def test_get_component_missing_required_params(self):
        """测试缺少必需参数"""
        # 按钮组件缺少text参数
        url = f"{self.endpoint}/button"
        params = {"type": "primary"}
        
        response = requests.get(url, params=params)
        
        # 合约要求：400状态码或返回默认内容
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            # 如果返回200，应该有默认内容
            soup = self.parse_html_response(response.text)
            button = soup.find('button')
            assert button is not None
    
    @pytest.mark.contract
    def test_htmx_attributes_injection(self):
        """测试HTMX属性注入"""
        url = f"{self.endpoint}/form"
        params = {
            "action": "/api/users/create",
            "hx-post": "/api/users/create",
            "hx-target": "#result-container",
            "hx-swap": "innerHTML",
            "hx-indicator": "#loading-spinner"
        }
        
        response = requests.get(url, params=params)
        
        assert response.status_code == 200
        
        soup = self.parse_html_response(response.text)
        form = soup.find('form')
        assert form is not None
        
        # 验证HTMX属性正确设置
        expected_attrs = {
            'hx-post': '/api/users/create',
            'hx-target': '#result-container', 
            'hx-swap': 'innerHTML',
            'hx-indicator': '#loading-spinner'
        }
        
        self.assert_htmx_attributes(form, expected_attrs)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])