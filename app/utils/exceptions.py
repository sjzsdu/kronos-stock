"""
自定义异常类

为UI系统增强功能提供专用异常处理。
"""


class UIServiceError(Exception):
    """UI服务基础异常类"""
    pass


class ValidationError(UIServiceError):
    """数据验证错误"""
    pass


class NotFoundError(UIServiceError):
    """资源未找到错误"""
    pass


class CacheError(UIServiceError):
    """缓存操作错误"""
    pass


class PerformanceError(UIServiceError):
    """性能监控错误"""
    pass


class ConfigurationError(UIServiceError):
    """配置错误"""
    pass


class RenderError(UIServiceError):
    """组件渲染错误"""
    pass


class TemplateError(RenderError):
    """模板错误"""
    pass


class ComponentError(UIServiceError):
    """组件相关错误"""
    pass