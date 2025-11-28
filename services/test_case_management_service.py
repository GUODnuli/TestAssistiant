import re
import json
import uuid
import time
from typing import List, Dict, Any

class TestCaseManagementService:
    """
    测试案例管理服务，负责测试要点分离、逻辑分组和报告整合
    """
    
    def separate_test_points(self, test_cases_content: str) -> List[Dict[str, Any]]:
        """
        将测试用例内容分离为独立的测试要点
        
        Args:
            test_cases_content: 测试用例内容字符串
            
        Returns:
            分离后的测试要点列表
        """
        # 清理输入内容
        content = test_cases_content.strip()
        
        # 如果是JSON格式，先解析JSON
        if content.startswith('{') and content.endswith('}'):
            try:
                data = json.loads(content)
                if isinstance(data, dict) and 'test_cases' in data:
                    content = data['test_cases']
                elif isinstance(data, str):
                    content = data
            except json.JSONDecodeError:
                pass
        
        # 分离测试要点
        test_points = []
        
        # 使用正则表达式匹配测试要点
        # 匹配数字开头的要点，如 "1. 用户登录系统" 或 "1、用户登录系统"
        pattern = r'(?:^|\n)\s*(\d+)[\.\、]\s*(.+?)(?=\n\d+[\.\、]|\n?$)'
        matches = re.findall(pattern, content, re.DOTALL)
        
        if matches:
            for i, (number, point) in enumerate(matches):
                test_points.append({
                    "id": f"TP{str(uuid.uuid4())[:8]}",
                    "index": int(number),
                    "content": point.strip(),
                    "title": f"测试要点 {number}"
                })
        else:
            # 如果没有找到编号的要点，按句子分割
            sentences = re.split(r'[。\n]+', content)
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    test_points.append({
                        "id": f"TP{str(uuid.uuid4())[:8]}",
                        "index": i + 1,
                        "content": sentence.strip(),
                        "title": f"测试要点 {i + 1}"
                    })
        
        return test_points
    
    def group_test_cases_by_logic(self, test_points: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        按逻辑关系对测试要点进行分组（每5个要点为一组）
        
        Args:
            test_points: 测试要点列表
            
        Returns:
            分组后的测试要点字典
        """
        grouped_points = {}
        
        # 每5个测试要点为一组
        group_size = 5
        for i in range(0, len(test_points), group_size):
            group_number = i // group_size + 1
            group_name = f"测试组 {group_number}"
            grouped_points[group_name] = test_points[i:i + group_size]
        
        return grouped_points
    
    def integrate_test_reports(self, reports: List[Any]) -> Dict[str, Any]:
        """
        整合多个测试报告为统一报告
        
        Args:
            reports: 测试报告列表
            
        Returns:
            整合后的报告字典
        """
        if not reports:
            return {
                "summary": {
                    "total_cases": 0,
                    "passed_cases": 0,
                    "failed_cases": 0,
                    "pass_rate": "0%",
                    "total_execution_time": 0
                },
                "details": [],
                "timestamp": time.time()
            }
        
        # 计算汇总信息
        total_cases = 0
        passed_cases = 0
        total_time = 0
        all_details = []
        
        for report in reports:
            if isinstance(report, dict):
                # 处理单个测试执行结果
                total_cases += 1
                if report.get("success", False):
                    passed_cases += 1
                total_time += report.get("execution_time", 0)
                all_details.append(report)
            elif isinstance(report, list):
                # 处理批量执行结果列表
                for execution_result in report:
                    if isinstance(execution_result, dict):
                        total_cases += 1
                        if execution_result.get("success", False):
                            passed_cases += 1
                        total_time += execution_result.get("execution_time", 0)
                        all_details.append(execution_result)
        
        # 计算通过率
        pass_rate = "0%"
        if total_cases > 0:
            pass_rate = f"{int((passed_cases / total_cases) * 100)}%"
        
        return {
            "summary": {
                "total_cases": total_cases,
                "passed_cases": passed_cases,
                "failed_cases": total_cases - passed_cases,
                "pass_rate": pass_rate,
                "total_execution_time": round(total_time, 2)
            },
            "details": all_details,
            "timestamp": time.time()
        }
    
    def format_report_for_display(self, integrated_report: Dict[str, Any]) -> str:
        """
        格式化整合后的报告为易读的字符串格式
        
        Args:
            integrated_report: 整合后的报告字典
            
        Returns:
            格式化的报告字符串
        """
        if not integrated_report:
            return "无测试报告数据"
        
        summary = integrated_report.get("summary", {})
        details = integrated_report.get("details", [])
        timestamp = integrated_report.get("timestamp", 0)
        
        # 格式化时间戳
        formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
        
        # 构建报告字符串
        report_lines = []
        report_lines.append("========================================")
        report_lines.append(f"          测试报告汇总          ")
        report_lines.append("========================================")
        report_lines.append(f"生成时间: {formatted_time}")
        report_lines.append(f"总测试用例数: {summary.get('total_cases', 0)}")
        report_lines.append(f"通过测试数: {summary.get('passed_cases', 0)}")
        report_lines.append(f"失败测试数: {summary.get('failed_cases', 0)}")
        report_lines.append(f"通过率: {summary.get('pass_rate', '0%')}")
        report_lines.append(f"总执行时间: {summary.get('total_execution_time', 0):.2f} 秒")
        report_lines.append("========================================")
        report_lines.append("\n详细测试结果:")
        report_lines.append("----------------------------------------")
        
        # 添加详细结果
        for i, detail in enumerate(details, 1):
            test_id = detail.get('test_case_id', 'unknown')
            test_title = detail.get('test_case_title', '未知测试用例')
            success = detail.get('success', False)
            status = "✅ 通过" if success else "❌ 失败"
            execution_time = detail.get('execution_time', 0)
            error = detail.get('error', '')
            
            report_lines.append(f"\n[{i}] 测试用例: {test_title}")
            report_lines.append(f"  ID: {test_id}")
            report_lines.append(f"  状态: {status}")
            report_lines.append(f"  执行时间: {execution_time:.2f} 秒")
            
            if not success and error:
                report_lines.append(f"  错误信息:")
                # 格式化错误信息，每行前添加缩进
                error_lines = error.split('\n')
                for line in error_lines:
                    report_lines.append(f"    {line}")
        
        report_lines.append("\n========================================")
        report_lines.append("            报告结束            ")
        report_lines.append("========================================")
        
        return '\n'.join(report_lines)