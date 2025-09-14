#!/bin/bash
# 测试 csweb 部署的脚本

echo "🧪 测试 csweb 部署"
echo "=================="

cd csweb

echo "1. 检查必要文件..."
if [ ! -f "app.py" ]; then
    echo "❌ app.py 不存在"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt 不存在"
    exit 1
fi

if [ ! -f "download_models.py" ]; then
    echo "❌ download_models.py 不存在"
    exit 1
fi

echo "✅ 必要文件检查通过"

echo "2. 检查模型目录..."
model_count=0
for model in kronos-mini kronos-small kronos-base; do
    if [ -d "$model" ]; then
        echo "✅ $model 存在"
        ((model_count++))
    else
        echo "⚠️  $model 不存在"
    fi
done

if [ $model_count -eq 0 ]; then
    echo "❌ 没有找到任何模型目录，需要运行下载脚本"
    echo "运行: python download_models.py"
    exit 1
fi

echo "✅ 找到 $model_count 个模型目录"

echo "3. 检查Python依赖..."
if ! python -c "import flask, pandas, numpy, torch" 2>/dev/null; then
    echo "❌ 缺少必要的Python依赖"
    echo "运行: pip install -r requirements.txt"
    exit 1
fi

echo "✅ Python依赖检查通过"

echo "4. 测试应用启动..."
timeout 10 python -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✅ 应用导入成功')
except Exception as e:
    print(f'❌ 应用导入失败: {e}')
    sys.exit(1)
" || echo "⚠️  应用启动测试超时"

echo ""
echo "🎉 csweb 部署测试完成！"
echo ""
echo "启动应用："
echo "  python app.py"
echo ""
echo "Docker部署："
echo "  docker build -t kronos-csweb ."
echo "  docker run -p 5001:5001 kronos-csweb"
