#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(__file__))

from app import create_app
from app.models.prediction import PredictionRecord
import json

def main():
    app = create_app('development')  # Specify config explicitly
    with app.app_context():
        # Check all prediction records
        records = PredictionRecord.query.all()
        print(f'总共有 {len(records)} 条预测记录')
        
        for record in records:
            print(f'\n记录 {record.id}:')
            print(f'  股票代码: {record.stock_code}')
            print(f'  状态: {record.status}')
            print(f'  模型类型: {record.model_type}')
            print(f'  预测天数: {record.prediction_days}')
            print(f'  创建时间: {record.created_at}')
            
            if record.prediction_data:
                try:
                    data = json.loads(record.prediction_data)
                    print(f'  预测数据键: {list(data.keys()) if isinstance(data, dict) else "非字典类型"}')
                    
                    if isinstance(data, dict):
                        if 'prediction_results' in data:
                            print(f'  预测结果数量: {len(data["prediction_results"])}')
                            if data['prediction_results']:
                                print(f'  第一个预测结果: {data["prediction_results"][0]}')
                        if 'prediction_summary' in data:
                            summary = data['prediction_summary']
                            print(f'  预测摘要: 当前价格 {summary.get("current_price")}, 目标价格 {summary.get("target_price")}')
                except json.JSONDecodeError as e:
                    print(f'  JSON解析错误: {e}')
            else:
                print('  无预测数据')
            
            if record.error_message:
                print(f'  错误信息: {record.error_message}')

if __name__ == '__main__':
    main()