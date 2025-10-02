# -*- coding: utf-8 -*-
"""
登录性能测试脚本
测试用户认证和会话管理的性能表现
"""

import time
import statistics
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

import requests
from requests.sessions import Session


class LoginPerformanceTester:
    """登录性能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化性能测试器
        
        Args:
            base_url: 应用基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        self.errors = []
    
    def create_test_user(self, session: Session, username: str, email: str, password: str) -> bool:
        """
        创建测试用户
        
        Args:
            session: HTTP会话
            username: 用户名
            email: 邮箱
            password: 密码
            
        Returns:
            是否创建成功
        """
        try:
            # 获取注册页面的CSRF token
            register_url = f"{self.base_url}/auth/register"
            response = session.get(register_url)
            
            if response.status_code != 200:
                return False
            
            # 注册用户
            register_data = {
                'username': username,
                'email': email,
                'password': password,
                'confirm_password': password
            }
            
            response = session.post(register_url, data=register_data)
            
            # 检查是否注册成功（可能返回重定向或成功页面）
            return response.status_code in [200, 302]
            
        except Exception as e:
            print(f"创建测试用户失败: {str(e)}")
            return False
    
    def test_single_login(self, username: str, password: str, test_id: int = 0) -> Dict[str, Any]:
        """
        测试单次登录性能
        
        Args:
            username: 用户名
            password: 密码
            test_id: 测试ID
            
        Returns:
            测试结果字典
        """
        session = Session()
        result = {
            'test_id': test_id,
            'username': username,
            'start_time': time.time(),
            'success': False,
            'response_time': 0,
            'status_code': 0,
            'error': None,
            'steps': {}
        }
        
        try:
            # 步骤1: 获取登录页面
            step1_start = time.time()
            login_page_url = f"{self.base_url}/auth/login"
            response = session.get(login_page_url)
            step1_time = time.time() - step1_start
            
            result['steps']['get_login_page'] = {
                'time': step1_time,
                'status_code': response.status_code
            }
            
            if response.status_code != 200:
                result['error'] = f"获取登录页面失败: {response.status_code}"
                return result
            
            # 步骤2: 提交登录表单
            step2_start = time.time()
            login_data = {
                'username': username,
                'password': password
            }
            
            response = session.post(login_page_url, data=login_data)
            step2_time = time.time() - step2_start
            
            result['steps']['submit_login'] = {
                'time': step2_time,
                'status_code': response.status_code
            }
            
            # 步骤3: 验证登录状态（访问需要认证的页面）
            step3_start = time.time()
            dashboard_url = f"{self.base_url}/user/dashboard"
            response = session.get(dashboard_url)
            step3_time = time.time() - step3_start
            
            result['steps']['verify_auth'] = {
                'time': step3_time,
                'status_code': response.status_code
            }
            
            # 判断登录是否成功
            if response.status_code == 200:
                result['success'] = True
            elif response.status_code == 302:
                # 检查重定向目标
                location = response.headers.get('Location', '')
                if 'login' not in location.lower():
                    result['success'] = True
            
            result['status_code'] = response.status_code
            result['response_time'] = time.time() - result['start_time']
            
        except Exception as e:
            result['error'] = str(e)
            result['response_time'] = time.time() - result['start_time']
        
        finally:
            session.close()
        
        return result
    
    def test_concurrent_logins(self, test_users: List[Dict[str, str]], max_workers: int = 10) -> List[Dict[str, Any]]:
        """
        测试并发登录性能
        
        Args:
            test_users: 测试用户列表 [{'username': '...', 'password': '...'}]
            max_workers: 最大并发数
            
        Returns:
            测试结果列表
        """
        print(f"开始并发登录测试，用户数: {len(test_users)}, 并发数: {max_workers}")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有测试任务
            future_to_test = {
                executor.submit(
                    self.test_single_login,
                    user['username'],
                    user['password'],
                    i
                ): i for i, user in enumerate(test_users)
            }
            
            # 收集结果
            for future in as_completed(future_to_test):
                test_id = future_to_test[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    status = "✅" if result['success'] else "❌"
                    print(f"{status} 测试 {test_id}: {result['username']}, "
                          f"响应时间: {result['response_time']:.3f}s")
                    
                except Exception as exc:
                    error_result = {
                        'test_id': test_id,
                        'success': False,
                        'error': str(exc),
                        'response_time': 0
                    }
                    results.append(error_result)
                    print(f"❌ 测试 {test_id} 执行异常: {exc}")
        
        return results
    
    def analyze_performance_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析性能测试结果
        
        Args:
            results: 测试结果列表
            
        Returns:
            性能分析报告
        """
        if not results:
            return {'error': '没有测试结果'}
        
        # 过滤成功的测试
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]
        
        response_times = [r['response_time'] for r in successful_tests]
        
        analysis = {
            'test_summary': {
                'total_tests': len(results),
                'successful_tests': len(successful_tests),
                'failed_tests': len(failed_tests),
                'success_rate': len(successful_tests) / len(results) if results else 0
            },
            'performance_metrics': {},
            'step_analysis': {},
            'errors': [r['error'] for r in failed_tests if r.get('error')]
        }
        
        if response_times:
            analysis['performance_metrics'] = {
                'min_response_time': min(response_times),
                'max_response_time': max(response_times),
                'avg_response_time': statistics.mean(response_times),
                'median_response_time': statistics.median(response_times),
                'std_deviation': statistics.stdev(response_times) if len(response_times) > 1 else 0,
                'p95_response_time': self._percentile(response_times, 95),
                'p99_response_time': self._percentile(response_times, 99)
            }
            
            # 分析各步骤性能
            step_names = ['get_login_page', 'submit_login', 'verify_auth']
            for step_name in step_names:
                step_times = []
                for result in successful_tests:
                    if 'steps' in result and step_name in result['steps']:
                        step_times.append(result['steps'][step_name]['time'])
                
                if step_times:
                    analysis['step_analysis'][step_name] = {
                        'min_time': min(step_times),
                        'max_time': max(step_times),
                        'avg_time': statistics.mean(step_times),
                        'median_time': statistics.median(step_times)
                    }
        
        return analysis
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def generate_performance_report(self, analysis: Dict[str, Any]) -> str:
        """
        生成性能测试报告
        
        Args:
            analysis: 性能分析结果
            
        Returns:
            格式化的报告字符串
        """
        if 'error' in analysis:
            return f"❌ 报告生成失败: {analysis['error']}"
        
        summary = analysis['test_summary']
        metrics = analysis.get('performance_metrics', {})
        steps = analysis.get('step_analysis', {})
        errors = analysis.get('errors', [])
        
        report = []
        report.append("=" * 60)
        report.append("🚀 登录性能测试报告")
        report.append("=" * 60)
        report.append(f"📊 测试概况:")
        report.append(f"   总测试数: {summary['total_tests']}")
        report.append(f"   成功测试: {summary['successful_tests']}")
        report.append(f"   失败测试: {summary['failed_tests']}")
        report.append(f"   成功率: {summary['success_rate']:.1%}")
        report.append("")
        
        if metrics:
            report.append("⏱️ 响应时间统计:")
            report.append(f"   最小响应时间: {metrics['min_response_time']:.3f}s")
            report.append(f"   最大响应时间: {metrics['max_response_time']:.3f}s")
            report.append(f"   平均响应时间: {metrics['avg_response_time']:.3f}s")
            report.append(f"   中位数响应时间: {metrics['median_response_time']:.3f}s")
            report.append(f"   95%分位响应时间: {metrics['p95_response_time']:.3f}s")
            report.append(f"   99%分位响应时间: {metrics['p99_response_time']:.3f}s")
            report.append(f"   标准差: {metrics['std_deviation']:.3f}s")
            report.append("")
            
            # 性能评估
            avg_time = metrics['avg_response_time']
            if avg_time < 1.0:
                performance_grade = "🟢 优秀"
            elif avg_time < 2.0:
                performance_grade = "🟡 良好"
            elif avg_time < 3.0:
                performance_grade = "🟠 一般"
            else:
                performance_grade = "🔴 需要优化"
            
            report.append(f"📈 性能评级: {performance_grade}")
            report.append("")
        
        if steps:
            report.append("🔍 步骤性能分析:")
            step_names = {
                'get_login_page': '获取登录页面',
                'submit_login': '提交登录请求',
                'verify_auth': '验证认证状态'
            }
            
            for step_key, step_data in steps.items():
                step_name = step_names.get(step_key, step_key)
                report.append(f"   {step_name}:")
                report.append(f"     平均时间: {step_data['avg_time']:.3f}s")
                report.append(f"     最小时间: {step_data['min_time']:.3f}s")
                report.append(f"     最大时间: {step_data['max_time']:.3f}s")
            report.append("")
        
        if errors:
            report.append("❌ 错误信息:")
            for i, error in enumerate(errors[:5], 1):  # 只显示前5个错误
                report.append(f"   {i}. {error}")
            if len(errors) > 5:
                report.append(f"   ... 还有 {len(errors) - 5} 个错误")
            report.append("")
        
        report.append("📝 建议:")
        if metrics:
            avg_time = metrics['avg_response_time']
            if avg_time > 2.0:
                report.append("   - 响应时间超过2秒，建议检查数据库查询和缓存策略")
                report.append("   - 考虑优化认证中间件和用户查询逻辑")
            if summary['success_rate'] < 0.95:
                report.append("   - 成功率低于95%，建议检查错误日志和系统稳定性")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_comprehensive_test(self, num_users: int = 20, max_workers: int = 5) -> str:
        """
        运行综合性能测试
        
        Args:
            num_users: 测试用户数量
            max_workers: 最大并发数
            
        Returns:
            测试报告
        """
        print(f"🚀 开始登录性能测试 (用户数: {num_users}, 并发数: {max_workers})")
        
        # 生成测试用户
        test_users = []
        for i in range(num_users):
            test_users.append({
                'username': f'test_user_{i}_{int(time.time())}',
                'password': 'TestPassword123!'
            })
        
        # 创建测试用户（可选，如果系统支持）
        print("📝 准备测试用户...")
        session = Session()
        created_users = 0
        for user in test_users:
            if self.create_test_user(session, user['username'], 
                                   f"{user['username']}@test.com", user['password']):
                created_users += 1
        session.close()
        
        if created_users > 0:
            print(f"✅ 成功创建 {created_users} 个测试用户")
        else:
            print("ℹ️ 使用现有用户进行测试")
        
        # 执行并发登录测试
        test_start_time = time.time()
        results = self.test_concurrent_logins(test_users, max_workers)
        test_duration = time.time() - test_start_time
        
        print(f"⏱️ 测试完成，总耗时: {test_duration:.2f}s")
        
        # 分析结果
        analysis = self.analyze_performance_results(results)
        analysis['test_duration'] = test_duration
        analysis['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成报告
        report = self.generate_performance_report(analysis)
        
        return report


def main():
    """主函数，运行性能测试"""
    tester = LoginPerformanceTester()
    
    # 运行综合测试
    report = tester.run_comprehensive_test(
        num_users=10,  # 测试10个用户
        max_workers=3   # 最大并发3个
    )
    
    print(report)
    
    # 保存报告到文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"login_performance_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存到: {report_file}")


if __name__ == "__main__":
    main()