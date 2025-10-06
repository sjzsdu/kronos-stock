#!/bin/bash

# CSS语义化类使用检查脚本
# 用于验证模板文件中是否正确使用语义化CSS类而非直接TailwindCSS类

set -e

TEMPLATE_DIR="${1:-app/templates}"
REPORT_FILE="css-audit-report.txt"

echo "🎨 CSS语义化类使用审查"
echo "=========================="
echo "检查目录: $TEMPLATE_DIR"
echo "报告文件: $REPORT_FILE"
echo ""

# 清空报告文件
> "$REPORT_FILE"

# 定义需要检查的TailwindCSS模式和建议
check_patterns() {
    local file="$1"
    local violations=0
    
    # 检查表单相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*border[^"]*rounded[^"]*px-[0-9]+[^"]*py-[0-9]+' "$file" 2>/dev/null; then
        echo "❌ $file: 发现表单输入样式模式 - 应使用 .form-input 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查按钮相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*bg-blue[^"]*text-white[^"]*px-[0-9]+[^"]*py-[0-9]+' "$file" 2>/dev/null; then
        echo "❌ $file: 发现按钮样式模式 - 应使用 .btn-primary 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查卡片相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*bg-white[^"]*rounded[^"]*shadow' "$file" 2>/dev/null; then
        echo "❌ $file: 发现卡片样式模式 - 应使用 .card 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查布局相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*flex[^"]*items-center[^"]*justify' "$file" 2>/dev/null; then
        echo "❌ $file: 发现布局样式模式 - 应使用语义化布局类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查模态框相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*fixed[^"]*inset-0[^"]*flex' "$file" 2>/dev/null; then
        echo "❌ $file: 发现模态框样式模式 - 应使用 .modal 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查成功提示相关的直接TailwindCSS使用
    if grep -q -E 'class="[^"]*bg-green[^"]*border-green[^"]*text-green' "$file" 2>/dev/null; then
        echo "❌ $file: 发现成功提示样式模式 - 应使用 .alert-success 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    # 检查错误提示相关的直接TailwindCSS使用  
    if grep -q -E 'class="[^"]*bg-red[^"]*border-red[^"]*text-red' "$file" 2>/dev/null; then
        echo "❌ $file: 发现错误提示样式模式 - 应使用 .alert-error 类" >> "$REPORT_FILE"
        violations=$((violations + 1))
    fi
    
    return $violations
}

# 定义推荐的语义化类
SEMANTIC_CLASSES=(
    "form-input" "form-textarea" "form-select" "form-error"
    "btn-primary" "btn-secondary" "btn-danger" "btn-ghost"
    "card" "card-header" "card-body" "card-footer"
    "nav" "nav-item" "nav-subitem" "sidebar"
    "modal" "modal-backdrop" "modal-dialog"
    "alert" "alert-success" "alert-error" "alert-warning"
    "layout" "layout-header" "layout-sidebar" "layout-main"
)

echo "检查进度:"



# 检查语义化类的使用情况
check_semantic_usage() {
    local file="$1"
    local semantic_count=0
    
    for class in "${SEMANTIC_CLASSES[@]}"; do
        if grep -q "class=\"[^\"]*$class" "$file" 2>/dev/null; then
            semantic_count=$((semantic_count + 1))
        fi
    done
    
    echo "$semantic_count"
}

total_files=0
violation_files=0
total_violations=0
total_semantic_usage=0

# 扫描所有HTML模板文件
while IFS= read -r -d '' file; do
    total_files=$((total_files + 1))
    
    # 显示进度
    if [ $((total_files % 10)) -eq 0 ]; then
        printf "."
    fi
    
    # 检查违规模式
    check_patterns "$file"
    file_violations=$?
    
    if [ $file_violations -gt 0 ]; then
        violation_files=$((violation_files + 1))
        total_violations=$((total_violations + file_violations))
    fi
    
    # 统计语义化类使用情况
    semantic_usage=$(check_semantic_usage "$file")
    total_semantic_usage=$((total_semantic_usage + semantic_usage))
    
    if [ $semantic_usage -gt 0 ]; then
        echo "✅ $file: 使用了 $semantic_usage 个语义化CSS类" >> "$REPORT_FILE"
    fi
    
done < <(find "$TEMPLATE_DIR" -name "*.html" -print0 2>/dev/null || true)

echo ""
echo ""
echo "📊 审查结果汇总"
echo "================"
echo "总文件数: $total_files"
echo "违规文件数: $violation_files"
echo "总违规数: $total_violations"
echo "语义化类使用总数: $total_semantic_usage"
echo ""

if [ $total_violations -gt 0 ]; then
    echo "⚠️  发现 $total_violations 个CSS使用问题，请查看 $REPORT_FILE"
    echo ""
    echo "常见修复建议:"
    echo "============="
    echo "1. 表单输入: class=\"border rounded px-4 py-2\" → class=\"form-input\""
    echo "2. 主要按钮: class=\"bg-blue-500 text-white px-4 py-2\" → class=\"btn-primary\""
    echo "3. 卡片容器: class=\"bg-white rounded shadow\" → class=\"card\""
    echo "4. 成功提示: class=\"bg-green-100 text-green-800\" → class=\"alert-success\""
    echo "5. 错误提示: class=\"bg-red-100 text-red-800\" → class=\"alert-error\""
    echo ""
    exit 1
else
    echo "✅ 所有模板文件都正确使用了语义化CSS类!"
    echo "💡 语义化类使用情况良好 ($total_semantic_usage 处使用)"
fi

echo ""
echo "详细报告已保存到: $REPORT_FILE"