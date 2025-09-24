# 测试指南

## 📁 测试目录结构

```
tests/
├── conftest.py              # 测试配置和fixtures
├── api/                     # API接口测试
│   └── test_prediction.py   # 预测相关API测试
├── services/                # 服务层测试
│   └── test_services.py     # 股票和预测服务测试
├── models/                  # 模型层测试
│   └── test_prediction.py   # 预测记录模型测试
└── integration/             # 集成测试
    └── test_modal_chart.py  # 模态框和图表集成测试
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
pip install -r requirements-test.txt
```

### 2. 运行测试

```bash
# 运行所有测试
./run_tests.sh

# 或者使用pytest直接运行
pytest

# 运行特定类型的测试
./run_tests.sh unit        # 单元测试
./run_tests.sh api         # API测试
./run_tests.sh integration # 集成测试

# 生成覆盖率报告
./run_tests.sh coverage

# 快速测试（遇到第一个失败就停止）
./run_tests.sh quick

# 详细输出
./run_tests.sh verbose
```

### 3. 运行特定测试

```bash
# 运行特定文件
pytest tests/api/test_prediction.py

# 运行特定测试类
pytest tests/api/test_prediction.py::TestPredictionAPI

# 运行特定测试方法
pytest tests/api/test_prediction.py::TestPredictionAPI::test_get_chart_data_success

# 使用关键字过滤
pytest -k "chart_data"

# 运行标记的测试
pytest -m integration
```

## 🧪 测试类型说明

- **单元测试**: 测试单个函数或类的功能
- **API测试**: 测试HTTP端点的行为
- **集成测试**: 测试多个组件协同工作
- **服务测试**: 测试业务逻辑层

## 📊 查看测试覆盖率

```bash
./run_tests.sh coverage
open htmlcov/index.html  # 在浏览器中查看详细报告
```

## 🔧 添加新测试

1. 在相应目录下创建 `test_*.py` 文件
2. 使用 `conftest.py` 中定义的fixtures
3. 遵循命名规范：`test_*` 函数，`Test*` 类

## 📝 测试最佳实践

- 每个测试应该独立且可重复
- 使用描述性的测试名称
- 利用fixtures管理测试数据
- Mock外部依赖
- 测试边界条件和错误情况