# -*- coding: utf-8 -*-
"""
仪表板性能测试脚本
测试用户仪表板页面加载速度和组件响应性能
"""

import time
import statistics
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

import requests
from requests.sessions import Session
from bs4 import BeautifulSoup


class DashboardPerformanceTester:
    """仪表板性能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5001"):
        """
        初始化性能测试器
        
        Args:
            base_url: 应用基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.test_results = []
        self.errors = []
    
    def login_user(self, session: Session, username: str, password: str) -> bool:
        """
        用户登录
        
        Args:
            session: HTTP会话
            username: 用户名
            password: 密码
            
        Returns:
            是否登录成功
        """
        try:
            # 获取登录页面
            login_url = f"{self.base_url}/auth/login"
            response = session.get(login_url)
            
            if response.status_code != 200:
                return False
            
            # 提交登录表单
            login_data = {
                'username': username,
                'password': password
            }
            
            response = session.post(login_url, data=login_data)
            
            # 验证登录状态
            if response.status_code in [200, 302]:
                # 尝试访问需要认证的页面来确认登录成功
                dashboard_url = f"{self.base_url}/user/dashboard"
                test_response = session.get(dashboard_url)
                return test_response.status_code == 200
            
            return False
            
        except Exception as e:
            print(f"用户登录失败: {str(e)}")
            return False
    
    def test_dashboard_loading(self, username: str, password: str, test_id: int = 0) -> Dict[str, Any]:
        """
        测试仪表板页面加载性能
        
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
            'total_time': 0,
            'error': None,
            'steps': {},
            'page_metrics': {},
            'component_metrics': {}
        }
        
        try:
            # 步骤1: 用户登录
            step1_start = time.time()
            login_success = self.login_user(session, username, password)
            step1_time = time.time() - step1_start
            
            result['steps']['login'] = {
                'time': step1_time,
                'success': login_success
            }
            
            if not login_success:
                result['error'] = "用户登录失败"
                return result
            
            # 步骤2: 加载仪表板页面
            step2_start = time.time()
            dashboard_url = f"{self.base_url}/user/dashboard"
            response = session.get(dashboard_url)
            step2_time = time.time() - step2_start
            
            result['steps']['load_dashboard'] = {
                'time': step2_time,
                'status_code': response.status_code,
                'content_length': len(response.content) if response.content else 0
            }
            
            if response.status_code != 200:
                result['error'] = f"仪表板页面加载失败: {response.status_code}"
                return result
            
            # 步骤3: 解析页面内容
            step3_start = time.time()
            page_metrics = self._analyze_page_content(response.text)
            step3_time = time.time() - step3_start
            
            result['steps']['parse_content'] = {
                'time': step3_time
            }
            result['page_metrics'] = page_metrics
            
            # 步骤4: 测试关键组件加载
            step4_start = time.time()
            component_metrics = self._test_dashboard_components(session)
            step4_time = time.time() - step4_start
            
            result['steps']['load_components'] = {
                'time': step4_time
            }
            result['component_metrics'] = component_metrics
            
            # 步骤5: 测试HTMX组件响应
            step5_start = time.time()
            htmx_metrics = self._test_htmx_components(session)
            step5_time = time.time() - step5_start
            
            result['steps']['test_htmx'] = {
                'time': step5_time
            }
            result['htmx_metrics'] = htmx_metrics
            
            result['success'] = True
            result['total_time'] = time.time() - result['start_time']
            
        except Exception as e:
            result['error'] = str(e)
            result['total_time'] = time.time() - result['start_time']
        
        finally:
            session.close()
        
        return result
    
    def _analyze_page_content(self, html_content: str) -> Dict[str, Any]:
        """
        分析页面内容
        
        Args:
            html_content: HTML内容
            
        Returns:
            页面指标字典
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 统计页面元素
            metrics = {
                'html_size': len(html_content),
                'total_elements': len(soup.find_all()),
                'div_count': len(soup.find_all('div')),
                'script_count': len(soup.find_all('script')),
                'style_count': len(soup.find_all('style')),
                'link_count': len(soup.find_all('link')),
                'img_count': len(soup.find_all('img')),
                'form_count': len(soup.find_all('form')),
                'table_count': len(soup.find_all('table'))
            }
            
            # 检查关键组件是否存在
            key_components = {
                'navigation': bool(soup.find('nav') or soup.find(class_='navigation')),
                'sidebar': bool(soup.find(class_='sidebar')),
                'main_content': bool(soup.find('main') or soup.find(class_='main-content')),
                'user_info': bool(soup.find(class_='user-info')),
                'charts': bool(soup.find(class_='chart') or soup.find('canvas')),
                'watchlist': bool(soup.find(class_='watchlist')),
                'prediction_history': bool(soup.find(class_='prediction-history'))
            }
            
            metrics['components'] = key_components
            metrics['component_count'] = sum(key_components.values())
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def _test_dashboard_components(self, session: Session) -> Dict[str, Any]:
        """
        测试仪表板关键组件加载
        
        Args:
            session: HTTP会话
            
        Returns:
            组件性能指标
        """
        components = {
            'user_profile': '/api/user/profile',
            'watchlist': '/api/user/watchlist',
            'prediction_history': '/api/user/predictions',
            'market_overview': '/api/market/overview'
        }
        
        metrics = {}
        
        for component_name, endpoint in components.items():
            try:
                start_time = time.time()
                url = f"{self.base_url}{endpoint}"
                response = session.get(url)
                load_time = time.time() - start_time
                
                metrics[component_name] = {
                    'load_time': load_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'response_size': len(response.content) if response.content else 0
                }
                
                # 如果是JSON响应，解析内容
                if response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        json_data = response.json()
                        if isinstance(json_data, dict):
                            metrics[component_name]['data_keys'] = list(json_data.keys())
                        elif isinstance(json_data, list):
                            metrics[component_name]['data_count'] = len(json_data)
                    except:
                        pass
                
            except Exception as e:
                metrics[component_name] = {
                    'load_time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        return metrics
    
    def _test_htmx_components(self, session: Session) -> Dict[str, Any]:
        """
        测试HTMX组件响应性能
        
        Args:
            session: HTTP会话
            
        Returns:
            HTMX组件性能指标
        """
        htmx_endpoints = {
            'auth_status': '/auth/status',
            'user_menu': '/user/menu',
            'notification_count': '/user/notifications/count'
        }
        
        metrics = {}
        
        # 设置HTMX请求头
        htmx_headers = {
            'HX-Request': 'true',
            'HX-Current-URL': f"{self.base_url}/user/dashboard"
        }
        
        for component_name, endpoint in htmx_endpoints.items():
            try:
                start_time = time.time()
                url = f"{self.base_url}{endpoint}"
                response = session.get(url, headers=htmx_headers)
                response_time = time.time() - start_time
                
                metrics[component_name] = {
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'success': response.status_code == 200,
                    'content_length': len(response.content) if response.content else 0
                }
                
            except Exception as e:
                metrics[component_name] = {
                    'response_time': 0,
                    'success': False,
                    'error': str(e)
                }
        
        return metrics
    
    def test_concurrent_dashboard_access(self, test_users: List[Dict[str, str]], 
                                       max_workers: int = 5) -> List[Dict[str, Any]]:
        """
        测试并发仪表板访问性能
        
        Args:
            test_users: 测试用户列表
            max_workers: 最大并发数
            
        Returns:
            测试结果列表
        """
        print(f"开始并发仪表板测试，用户数: {len(test_users)}, 并发数: {max_workers}")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有测试任务
            future_to_test = {
                executor.submit(
                    self.test_dashboard_loading,
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
                          f"总时间: {result['total_time']:.3f}s")
                    
                except Exception as exc:
                    error_result = {
                        'test_id': test_id,
                        'success': False,
                        'error': str(exc),
                        'total_time': 0
                    }
                    results.append(error_result)
                    print(f"❌ 测试 {test_id} 执行异常: {exc}")
        
        return results
    
    def analyze_dashboard_performance(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析仪表板性能测试结果
        
        Args:
            results: 测试结果列表
            
        Returns:
            性能分析报告
        """
        if not results:
            return {'error': '没有测试结果'}
        
        successful_tests = [r for r in results if r['success']]
        failed_tests = [r for r in results if not r['success']]
        
        total_times = [r['total_time'] for r in successful_tests]
        
        analysis = {
            'test_summary': {
                'total_tests': len(results),
                'successful_tests': len(successful_tests),
                'failed_tests': len(failed_tests),
                'success_rate': len(successful_tests) / len(results) if results else 0
            },
            'performance_metrics': {},
            'step_analysis': {},
            'component_analysis': {},
            'page_analysis': {},
            'errors': [r['error'] for r in failed_tests if r.get('error')]
        }
        
        if total_times:
            analysis['performance_metrics'] = {
                'min_total_time': min(total_times),
                'max_total_time': max(total_times),
                'avg_total_time': statistics.mean(total_times),
                'median_total_time': statistics.median(total_times),
                'std_deviation': statistics.stdev(total_times) if len(total_times) > 1 else 0,
                'p95_total_time': self._percentile(total_times, 95),
                'p99_total_time': self._percentile(total_times, 99)
            }
            
            # 分析各步骤性能
            step_names = ['login', 'load_dashboard', 'parse_content', 'load_components', 'test_htmx']
            for step_name in step_names:
                step_times = []
                for result in successful_tests:
                    if 'steps' in result and step_name in result['steps']:
                        step_data = result['steps'][step_name]
                        if 'time' in step_data:
                            step_times.append(step_data['time'])
                
                if step_times:
                    analysis['step_analysis'][step_name] = {
                        'min_time': min(step_times),
                        'max_time': max(step_times),
                        'avg_time': statistics.mean(step_times),
                        'median_time': statistics.median(step_times)
                    }
            
            # 分析组件性能
            component_names = ['user_profile', 'watchlist', 'prediction_history', 'market_overview']
            for component_name in component_names:
                component_times = []
                for result in successful_tests:
                    if 'component_metrics' in result and component_name in result['component_metrics']:
                        component_data = result['component_metrics'][component_name]
                        if 'load_time' in component_data and component_data.get('success', False):
                            component_times.append(component_data['load_time'])
                
                if component_times:
                    analysis['component_analysis'][component_name] = {
                        'min_time': min(component_times),
                        'max_time': max(component_times),
                        'avg_time': statistics.mean(component_times),
                        'success_rate': len(component_times) / len(successful_tests)
                    }
            
            # 分析页面指标
            page_sizes = []
            component_counts = []
            
            for result in successful_tests:
                if 'page_metrics' in result:
                    page_data = result['page_metrics']
                    if 'html_size' in page_data:
                        page_sizes.append(page_data['html_size'])
                    if 'component_count' in page_data:
                        component_counts.append(page_data['component_count'])
            
            if page_sizes:
                analysis['page_analysis']['html_size'] = {
                    'min_size': min(page_sizes),
                    'max_size': max(page_sizes),
                    'avg_size': statistics.mean(page_sizes)
                }
            
            if component_counts:
                analysis['page_analysis']['component_count'] = {
                    'min_count': min(component_counts),
                    'max_count': max(component_counts),
                    'avg_count': statistics.mean(component_counts)
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
    
    def generate_dashboard_report(self, analysis: Dict[str, Any]) -> str:
        """
        生成仪表板性能测试报告
        
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
        components = analysis.get('component_analysis', {})
        page_info = analysis.get('page_analysis', {})
        errors = analysis.get('errors', [])
        
        report = []
        report.append("=" * 60)
        report.append("📊 仪表板性能测试报告")
        report.append("=" * 60)
        report.append(f"📈 测试概况:")
        report.append(f"   总测试数: {summary['total_tests']}")
        report.append(f"   成功测试: {summary['successful_tests']}")
        report.append(f"   失败测试: {summary['failed_tests']}")
        report.append(f"   成功率: {summary['success_rate']:.1%}")
        report.append("")
        
        if metrics:
            report.append("⏱️ 整体加载性能:")
            report.append(f"   最小加载时间: {metrics['min_total_time']:.3f}s")
            report.append(f"   最大加载时间: {metrics['max_total_time']:.3f}s")
            report.append(f"   平均加载时间: {metrics['avg_total_time']:.3f}s")
            report.append(f"   中位数加载时间: {metrics['median_total_time']:.3f}s")
            report.append(f"   95%分位加载时间: {metrics['p95_total_time']:.3f}s")
            report.append(f"   99%分位加载时间: {metrics['p99_total_time']:.3f}s")
            report.append("")
            
            # 性能评估
            avg_time = metrics['avg_total_time']
            if avg_time < 2.0:
                performance_grade = "🟢 优秀"
            elif avg_time < 3.0:
                performance_grade = "🟡 良好"
            elif avg_time < 5.0:
                performance_grade = "🟠 一般"
            else:
                performance_grade = "🔴 需要优化"
            
            report.append(f"📈 性能评级: {performance_grade}")
            report.append("")
        
        if steps:
            report.append("🔍 步骤性能分析:")
            step_names = {
                'login': '用户登录',
                'load_dashboard': '加载仪表板页面',
                'parse_content': '解析页面内容',
                'load_components': '加载组件数据',
                'test_htmx': 'HTMX组件测试'
            }
            
            for step_key, step_data in steps.items():
                step_name = step_names.get(step_key, step_key)
                report.append(f"   {step_name}:")
                report.append(f"     平均时间: {step_data['avg_time']:.3f}s")
                report.append(f"     最小时间: {step_data['min_time']:.3f}s")
                report.append(f"     最大时间: {step_data['max_time']:.3f}s")
            report.append("")
        
        if components:
            report.append("🧩 组件性能分析:")
            component_names = {
                'user_profile': '用户档案',
                'watchlist': '关注列表',
                'prediction_history': '预测历史',
                'market_overview': '市场概览'
            }
            
            for comp_key, comp_data in components.items():
                comp_name = component_names.get(comp_key, comp_key)
                report.append(f"   {comp_name}:")
                report.append(f"     平均加载时间: {comp_data['avg_time']:.3f}s")
                report.append(f"     成功率: {comp_data['success_rate']:.1%}")
            report.append("")
        
        if page_info:
            report.append("📄 页面信息分析:")
            if 'html_size' in page_info:
                size_info = page_info['html_size']
                report.append(f"   HTML大小:")
                report.append(f"     平均大小: {size_info['avg_size']/1024:.1f}KB")
                report.append(f"     最小大小: {size_info['min_size']/1024:.1f}KB")
                report.append(f"     最大大小: {size_info['max_size']/1024:.1f}KB")
            
            if 'component_count' in page_info:
                comp_info = page_info['component_count']
                report.append(f"   页面组件:")
                report.append(f"     平均组件数: {comp_info['avg_count']:.1f}")
            report.append("")
        
        if errors:
            report.append("❌ 错误信息:")
            for i, error in enumerate(errors[:3], 1):  # 只显示前3个错误
                report.append(f"   {i}. {error}")
            if len(errors) > 3:
                report.append(f"   ... 还有 {len(errors) - 3} 个错误")
            report.append("")
        
        report.append("📝 优化建议:")
        if metrics:
            avg_time = metrics['avg_total_time']
            if avg_time > 3.0:
                report.append("   - 总加载时间超过3秒，建议优化:")
                report.append("     • 启用页面组件懒加载")
                report.append("     • 优化数据库查询和缓存策略")
                report.append("     • 压缩静态资源文件")
            
            if summary['success_rate'] < 0.95:
                report.append("   - 成功率低于95%，建议:")
                report.append("     • 检查网络连接稳定性")
                report.append("     • 优化错误处理机制")
        
        if components:
            slow_components = [name for name, data in components.items() 
                             if data['avg_time'] > 1.0]
            if slow_components:
                report.append(f"   - 慢组件优化 ({', '.join(slow_components)}):")
                report.append("     • 实现组件级缓存")
                report.append("     • 异步加载非关键组件")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_comprehensive_dashboard_test(self, test_users: List[Dict[str, str]], 
                                       max_workers: int = 3) -> str:
        """
        运行综合仪表板性能测试
        
        Args:
            test_users: 测试用户列表
            max_workers: 最大并发数
            
        Returns:
            测试报告
        """
        print(f"🚀 开始仪表板性能测试 (用户数: {len(test_users)}, 并发数: {max_workers})")
        
        # 执行并发测试
        test_start_time = time.time()
        results = self.test_concurrent_dashboard_access(test_users, max_workers)
        test_duration = time.time() - test_start_time
        
        print(f"⏱️ 测试完成，总耗时: {test_duration:.2f}s")
        
        # 分析结果
        analysis = self.analyze_dashboard_performance(results)
        analysis['test_duration'] = test_duration
        analysis['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 生成报告
        report = self.generate_dashboard_report(analysis)
        
        return report


def main():
    """主函数，运行仪表板性能测试"""
    tester = DashboardPerformanceTester()
    
    # 使用测试用户（需要确保这些用户存在）
    test_users = [
        {'username': 'test_user_1', 'password': 'TestPassword123!'},
        {'username': 'test_user_2', 'password': 'TestPassword123!'},
        {'username': 'test_user_3', 'password': 'TestPassword123!'},
        {'username': 'test_user_4', 'password': 'TestPassword123!'},
        {'username': 'test_user_5', 'password': 'TestPassword123!'},
    ]
    
    # 运行综合测试
    report = tester.run_comprehensive_dashboard_test(
        test_users=test_users,
        max_workers=3
    )
    
    print(report)
    
    # 保存报告到文件
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"dashboard_performance_report_{timestamp}.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 报告已保存到: {report_file}")


if __name__ == "__main__":
    main()