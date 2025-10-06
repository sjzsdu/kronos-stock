"""
UI组件测试基础工具类

为UI组件测试提供通用的测试辅助函数和断言方法。
"""
import pytest
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
import json


class UIComponentTestBase:
    """UI组件测试基类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.soup = None
        self.response_data = None
    
    def parse_html_response(self, html_content: str) -> BeautifulSoup:
        """解析HTML响应内容"""
        self.soup = BeautifulSoup(html_content, 'html.parser')
        return self.soup
    
    def assert_semantic_css_class(self, element, expected_class: str):
        """断言元素包含语义化CSS类"""
        assert element is not None, f"元素不存在"
        classes = element.get('class', [])
        assert expected_class in classes, f"元素缺少语义化CSS类: {expected_class}, 实际类: {classes}"
    
    def assert_no_tailwind_atomic_class(self, element):
        """断言元素不包含TailwindCSS原子类"""
        classes = element.get('class', [])
        # 检查常见的TailwindCSS原子类模式
        atomic_patterns = [
            'px-', 'py-', 'bg-', 'text-', 'border-', 'rounded-', 
            'flex', 'grid', 'items-', 'justify-', 'w-', 'h-'
        ]
        
        for class_name in classes:
            for pattern in atomic_patterns:
                if pattern in class_name and not self._is_semantic_class(class_name):
                    pytest.fail(f"发现TailwindCSS原子类: {class_name}, 应使用语义化CSS类")
    
    def _is_semantic_class(self, class_name: str) -> bool:
        """判断是否为语义化CSS类"""
        semantic_prefixes = [
            'form-', 'btn-', 'card-', 'nav-', 'modal-', 
            'alert-', 'layout-', 'sidebar-', 'dropdown-'
        ]
        return any(class_name.startswith(prefix) for prefix in semantic_prefixes)
    
    def assert_component_structure(self, element, expected_structure: Dict[str, Any]):
        """断言组件结构符合预期"""
        if 'tag' in expected_structure:
            assert element.name == expected_structure['tag']
        
        if 'classes' in expected_structure:
            for css_class in expected_structure['classes']:
                self.assert_semantic_css_class(element, css_class)
        
        if 'children' in expected_structure:
            children = element.find_all(recursive=False)
            assert len(children) >= len(expected_structure['children'])
    
    def assert_htmx_attributes(self, element, expected_attrs: Dict[str, str]):
        """断言HTMX属性正确设置"""
        for attr, expected_value in expected_attrs.items():
            actual_value = element.get(attr)
            assert actual_value == expected_value, f"HTMX属性 {attr} 不匹配: 期望 {expected_value}, 实际 {actual_value}"


class PerformanceTestBase:
    """性能测试基类"""
    
    def setup_method(self):
        """测试方法设置"""
        self.metrics = {}
    
    def record_metric(self, name: str, value: float, unit: str = 'ms'):
        """记录性能指标"""
        self.metrics[name] = {'value': value, 'unit': unit}
    
    def assert_performance_threshold(self, metric_name: str, threshold: float):
        """断言性能指标满足阈值要求"""
        assert metric_name in self.metrics, f"性能指标 {metric_name} 未记录"
        value = self.metrics[metric_name]['value']
        assert value <= threshold, f"性能指标 {metric_name} 超过阈值: {value} > {threshold}"
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能测试摘要"""
        return {
            'metrics_count': len(self.metrics),
            'metrics': self.metrics,
            'total_time': sum(m['value'] for m in self.metrics.values() if m['unit'] == 'ms')
        }


# 测试装饰器
def semantic_css_required(func):
    """要求使用语义化CSS的测试装饰器"""
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        # 在这里可以添加额外的语义化CSS验证逻辑
        return result
    return wrapper


def performance_test(threshold_ms: float = 1000):
    """性能测试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            duration = (end_time - start_time) * 1000  # 转换为毫秒
            
            assert duration <= threshold_ms, f"测试执行时间超过阈值: {duration:.2f}ms > {threshold_ms}ms"
            return result
        return wrapper
    return decorator