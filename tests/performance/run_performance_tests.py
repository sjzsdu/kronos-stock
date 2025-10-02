#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试运行脚本
集成所有性能测试，生成综合性能报告
"""

import sys
import os
import time
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.performance.login_performance_test import LoginPerformanceTester
from tests.performance.dashboard_performance_test import DashboardPerformanceTester


class PerformanceTestRunner:
    """性能测试运行器"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化性能测试运行器
        
        Args:
            base_url: 应用基础URL
        """
        self.base_url = base_url
        self.results_dir = project_root / "tests" / "performance" / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def create_test_users(self, count: int = 10) -> list:
        """
        生成测试用户列表
        
        Args:
            count: 用户数量
            
        Returns:
            测试用户列表
        """
        timestamp = int(time.time())
        test_users = []
        
        for i in range(count):
            test_users.append({
                'username': f'perf_test_user_{i}_{timestamp}',
                'password': 'PerformanceTest123!',
                'email': f'perf_test_{i}_{timestamp}@test.com'
            })
        
        return test_users
    
    def run_login_performance_test(self, test_users: list, max_workers: int = 5) -> dict:
        """
        运行登录性能测试
        
        Args:
            test_users: 测试用户列表
            max_workers: 最大并发数
            
        Returns:
            测试结果字典
        """
        print("🔐 开始登录性能测试...")
        
        tester = LoginPerformanceTester(self.base_url)
        
        # 运行测试
        start_time = time.time()
        results = tester.test_concurrent_logins(test_users, max_workers)
        test_duration = time.time() - start_time
        
        # 分析结果
        analysis = tester.analyze_performance_results(results)
        analysis['test_duration'] = test_duration
        analysis['test_type'] = 'login_performance'
        analysis['timestamp'] = datetime.now().isoformat()
        
        return {
            'test_name': '登录性能测试',
            'results': results,
            'analysis': analysis,
            'report': tester.generate_performance_report(analysis)
        }
    
    def run_dashboard_performance_test(self, test_users: list, max_workers: int = 3) -> dict:
        """
        运行仪表板性能测试
        
        Args:
            test_users: 测试用户列表
            max_workers: 最大并发数
            
        Returns:
            测试结果字典
        """
        print("📊 开始仪表板性能测试...")
        
        tester = DashboardPerformanceTester(self.base_url)
        
        # 运行测试
        start_time = time.time()
        results = tester.test_concurrent_dashboard_access(test_users, max_workers)
        test_duration = time.time() - start_time
        
        # 分析结果
        analysis = tester.analyze_dashboard_performance(results)
        analysis['test_duration'] = test_duration
        analysis['test_type'] = 'dashboard_performance'
        analysis['timestamp'] = datetime.now().isoformat()
        
        return {
            'test_name': '仪表板性能测试',
            'results': results,
            'analysis': analysis,
            'report': tester.generate_dashboard_report(analysis)
        }
    
    def check_server_availability(self) -> bool:
        """
        检查服务器是否可用
        
        Returns:
            服务器是否可用
        """
        try:
            import requests
            response = requests.get(f"{self.base_url}/", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def run_comprehensive_performance_test(self, 
                                         user_count: int = 8, 
                                         login_workers: int = 4, 
                                         dashboard_workers: int = 2) -> dict:
        """
        运行综合性能测试
        
        Args:
            user_count: 测试用户数量
            login_workers: 登录测试并发数
            dashboard_workers: 仪表板测试并发数
            
        Returns:
            综合测试结果
        """
        comprehensive_result = {
            'test_start_time': datetime.now().isoformat(),
            'test_config': {
                'user_count': user_count,
                'login_workers': login_workers,
                'dashboard_workers': dashboard_workers,
                'base_url': self.base_url
            },
            'tests': {},
            'summary': {},
            'recommendations': []
        }
        
        print("🚀 开始综合性能测试")
        print(f"配置: {user_count}个用户, 登录并发{login_workers}, 仪表板并发{dashboard_workers}")
        print("=" * 60)
        
        # 检查服务器可用性
        if not self.check_server_availability():
            print(f"❌ 服务器不可用: {self.base_url}")
            return {'error': '服务器连接失败'}
        
        print(f"✅ 服务器连接正常: {self.base_url}")
        
        # 生成测试用户
        test_users = self.create_test_users(user_count)
        print(f"📝 已生成 {len(test_users)} 个测试用户")
        
        total_start_time = time.time()
        
        # 运行登录性能测试
        try:
            login_test = self.run_login_performance_test(test_users, login_workers)
            comprehensive_result['tests']['login'] = login_test
            print("✅ 登录性能测试完成")
        except Exception as e:
            print(f"❌ 登录性能测试失败: {str(e)}")
            comprehensive_result['tests']['login'] = {'error': str(e)}
        
        print("-" * 40)
        
        # 运行仪表板性能测试
        try:
            dashboard_test = self.run_dashboard_performance_test(test_users, dashboard_workers)
            comprehensive_result['tests']['dashboard'] = dashboard_test
            print("✅ 仪表板性能测试完成")
        except Exception as e:
            print(f"❌ 仪表板性能测试失败: {str(e)}")
            comprehensive_result['tests']['dashboard'] = {'error': str(e)}
        
        total_duration = time.time() - total_start_time
        comprehensive_result['total_duration'] = total_duration
        comprehensive_result['test_end_time'] = datetime.now().isoformat()
        
        # 生成综合分析
        comprehensive_result['summary'] = self._generate_comprehensive_summary(comprehensive_result)
        comprehensive_result['recommendations'] = self._generate_recommendations(comprehensive_result)
        
        print("=" * 60)
        print(f"🎉 综合性能测试完成，总耗时: {total_duration:.2f}s")
        
        return comprehensive_result
    
    def _generate_comprehensive_summary(self, test_results: dict) -> dict:
        """
        生成综合测试摘要
        
        Args:
            test_results: 测试结果
            
        Returns:
            摘要信息
        """
        summary = {
            'overall_success': True,
            'performance_grades': {},
            'key_metrics': {}
        }
        
        # 登录测试摘要
        if 'login' in test_results['tests'] and 'analysis' in test_results['tests']['login']:
            login_analysis = test_results['tests']['login']['analysis']
            if 'performance_metrics' in login_analysis:
                login_metrics = login_analysis['performance_metrics']
                avg_login_time = login_metrics.get('avg_response_time', 0)
                
                if avg_login_time < 1.0:
                    login_grade = "优秀"
                elif avg_login_time < 2.0:
                    login_grade = "良好"
                elif avg_login_time < 3.0:
                    login_grade = "一般"
                else:
                    login_grade = "需要优化"
                
                summary['performance_grades']['login'] = login_grade
                summary['key_metrics']['avg_login_time'] = avg_login_time
                summary['key_metrics']['login_success_rate'] = login_analysis['test_summary']['success_rate']
        
        # 仪表板测试摘要
        if 'dashboard' in test_results['tests'] and 'analysis' in test_results['tests']['dashboard']:
            dashboard_analysis = test_results['tests']['dashboard']['analysis']
            if 'performance_metrics' in dashboard_analysis:
                dashboard_metrics = dashboard_analysis['performance_metrics']
                avg_dashboard_time = dashboard_metrics.get('avg_total_time', 0)
                
                if avg_dashboard_time < 2.0:
                    dashboard_grade = "优秀"
                elif avg_dashboard_time < 3.0:
                    dashboard_grade = "良好"
                elif avg_dashboard_time < 5.0:
                    dashboard_grade = "一般"
                else:
                    dashboard_grade = "需要优化"
                
                summary['performance_grades']['dashboard'] = dashboard_grade
                summary['key_metrics']['avg_dashboard_time'] = avg_dashboard_time
                summary['key_metrics']['dashboard_success_rate'] = dashboard_analysis['test_summary']['success_rate']
        
        # 判断整体性能
        grades = list(summary['performance_grades'].values())
        if all(grade in ["优秀", "良好"] for grade in grades):
            summary['overall_grade'] = "优秀"
        elif any(grade == "需要优化" for grade in grades):
            summary['overall_grade'] = "需要优化"
        else:
            summary['overall_grade'] = "一般"
        
        return summary
    
    def _generate_recommendations(self, test_results: dict) -> list:
        """
        生成优化建议
        
        Args:
            test_results: 测试结果
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 基于登录测试的建议
        if 'login' in test_results['tests'] and 'analysis' in test_results['tests']['login']:
            login_analysis = test_results['tests']['login']['analysis']
            if 'performance_metrics' in login_analysis:
                avg_time = login_analysis['performance_metrics'].get('avg_response_time', 0)
                success_rate = login_analysis['test_summary'].get('success_rate', 0)
                
                if avg_time > 2.0:
                    recommendations.append("登录响应时间较慢，建议优化用户认证中间件和数据库查询")
                
                if success_rate < 0.95:
                    recommendations.append("登录成功率偏低，建议检查用户认证流程的稳定性")
        
        # 基于仪表板测试的建议
        if 'dashboard' in test_results['tests'] and 'analysis' in test_results['tests']['dashboard']:
            dashboard_analysis = test_results['tests']['dashboard']['analysis']
            if 'performance_metrics' in dashboard_analysis:
                avg_time = dashboard_analysis['performance_metrics'].get('avg_total_time', 0)
                success_rate = dashboard_analysis['test_summary'].get('success_rate', 0)
                
                if avg_time > 3.0:
                    recommendations.append("仪表板加载时间较长，建议启用页面组件缓存和懒加载")
                
                if success_rate < 0.95:
                    recommendations.append("仪表板加载成功率偏低，建议优化组件错误处理")
        
        # 通用建议
        if not recommendations:
            recommendations.append("系统性能表现良好，建议继续监控和定期测试")
        else:
            recommendations.append("建议启用用户数据缓存服务以进一步提升性能")
            recommendations.append("考虑在生产环境中使用Redis作为缓存后端")
        
        return recommendations
    
    def save_test_results(self, test_results: dict) -> str:
        """
        保存测试结果到文件
        
        Args:
            test_results: 测试结果
            
        Returns:
            保存的文件路径
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 保存JSON结果
        json_file = self.results_dir / f"performance_test_{timestamp}.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2)
        
        # 生成可读报告
        report_file = self.results_dir / f"performance_report_{timestamp}.txt"
        report_content = self._generate_readable_report(test_results)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"📄 测试结果已保存:")
        print(f"   JSON格式: {json_file}")
        print(f"   报告格式: {report_file}")
        
        return str(report_file)
    
    def _generate_readable_report(self, test_results: dict) -> str:
        """
        生成可读的测试报告
        
        Args:
            test_results: 测试结果
            
        Returns:
            格式化的报告字符串
        """
        report = []
        report.append("=" * 80)
        report.append("🚀 Kronos Stock 系统性能测试综合报告")
        report.append("=" * 80)
        
        # 测试配置
        config = test_results.get('test_config', {})
        report.append(f"📋 测试配置:")
        report.append(f"   测试时间: {test_results.get('test_start_time', 'N/A')}")
        report.append(f"   服务器地址: {config.get('base_url', 'N/A')}")
        report.append(f"   测试用户数: {config.get('user_count', 'N/A')}")
        report.append(f"   登录并发数: {config.get('login_workers', 'N/A')}")
        report.append(f"   仪表板并发数: {config.get('dashboard_workers', 'N/A')}")
        report.append(f"   总测试时长: {test_results.get('total_duration', 0):.2f}s")
        report.append("")
        
        # 综合摘要
        summary = test_results.get('summary', {})
        report.append(f"📊 综合摘要:")
        report.append(f"   整体性能评级: {summary.get('overall_grade', 'N/A')}")
        
        grades = summary.get('performance_grades', {})
        if grades:
            report.append(f"   登录性能: {grades.get('login', 'N/A')}")
            report.append(f"   仪表板性能: {grades.get('dashboard', 'N/A')}")
        
        metrics = summary.get('key_metrics', {})
        if metrics:
            report.append(f"   平均登录时间: {metrics.get('avg_login_time', 0):.3f}s")
            report.append(f"   平均仪表板加载时间: {metrics.get('avg_dashboard_time', 0):.3f}s")
            report.append(f"   登录成功率: {metrics.get('login_success_rate', 0):.1%}")
            report.append(f"   仪表板成功率: {metrics.get('dashboard_success_rate', 0):.1%}")
        report.append("")
        
        # 详细测试报告
        tests = test_results.get('tests', {})
        
        if 'login' in tests and 'report' in tests['login']:
            report.append("🔐 登录性能详细报告:")
            report.append("-" * 60)
            report.append(tests['login']['report'])
            report.append("")
        
        if 'dashboard' in tests and 'report' in tests['dashboard']:
            report.append("📊 仪表板性能详细报告:")
            report.append("-" * 60)
            report.append(tests['dashboard']['report'])
            report.append("")
        
        # 优化建议
        recommendations = test_results.get('recommendations', [])
        if recommendations:
            report.append("💡 优化建议:")
            for i, rec in enumerate(recommendations, 1):
                report.append(f"   {i}. {rec}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kronos Stock 性能测试运行器')
    parser.add_argument('--url', default='http://localhost:5001', 
                       help='应用服务器URL (默认: http://localhost:5001)')
    parser.add_argument('--users', type=int, default=8, 
                       help='测试用户数量 (默认: 8)')
    parser.add_argument('--login-workers', type=int, default=4, 
                       help='登录测试并发数 (默认: 4)')
    parser.add_argument('--dashboard-workers', type=int, default=2, 
                       help='仪表板测试并发数 (默认: 2)')
    
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = PerformanceTestRunner(args.url)
    
    # 运行综合测试
    results = runner.run_comprehensive_performance_test(
        user_count=args.users,
        login_workers=args.login_workers,
        dashboard_workers=args.dashboard_workers
    )
    
    # 保存结果
    if 'error' not in results:
        runner.save_test_results(results)
    else:
        print(f"❌ 测试失败: {results['error']}")


if __name__ == "__main__":
    main()