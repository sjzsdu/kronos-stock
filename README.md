# Kronos Stock Prediction System

## 🚀 现代化架构

本项目已升级为现代化的模块化架构，使用 Flask + HTMX 构建。

## 📁 项目结构

```
kronos-stock/
├── run.py                 # 🌟 主启动文件
├── config.py              # 配置管理
├── requirements.txt       # 依赖管理
│
├── app/                   # 应用核心
│   ├── __init__.py       # 应用工厂
│   ├── services/         # 业务逻辑层
│   ├── api/              # RESTful API
│   ├── views/            # HTMX 视图
│   ├── static/           # 静态资源
│   └── templates/        # 模板文件
│
├── model/                # AI模型代码
├── models/               # 预训练模型
└── deploy/               # 部署相关
```

## 🏃‍♂️ 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动应用
```bash
python run.py
```

### 3. 访问界面
- **主页**: http://localhost:5001/
- **仪表盘**: http://localhost:5001/dashboard
- **API**: http://localhost:5001/api/

## 🌟 新架构特性

- ✅ **模块化设计**: 代码组织清晰，易于维护
- ✅ **HTMX交互**: 无刷新页面更新，现代化用户体验
- ✅ **Blueprint架构**: 功能模块独立，便于扩展
- ✅ **服务层模式**: 业务逻辑与路由分离
- ✅ **组件化前端**: 可复用的HTML组件

## 🔧 配置

环境变量：
- `PORT`: 服务端口 (默认: 5001)
- `FLASK_CONFIG`: 配置环境 (development/production/testing)
- `FLASK_ENV`: Flask环境 (development/production)

## 📊 API端点

- `GET /api/models` - 获取可用模型
- `POST /api/models/load` - 加载模型
- `GET /api/stock/data` - 获取股票数据
- `POST /api/predict` - 股票预测

## 🎯 从旧版本迁移

如果您之前使用 `python app.py` 启动，现在请使用：
```bash
python run.py
```

旧版本的大文件已被重构为模块化架构，功能更强大且更易维护。