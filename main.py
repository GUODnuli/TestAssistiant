from fastapi import FastAPI, HTTPException, Depends, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Union, Dict, Any
from datetime import datetime
import traceback
from services.test_case_service import TestCaseConversionService
from services.langchain_service import LangChainService
from services.test_case_management_service import TestCaseManagementService
from config import Config
import tempfile
import subprocess
import os
import time
import logging
import sys

# 配置日志，确保输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 初始化logger
logger = logging.getLogger(__name__)
app = FastAPI(title="AI测试用例转换服务", version="1.0.0")

# 添加CORS中间件以支持跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该指定具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录以提供Allure报告访问
app.mount("/allure-results", StaticFiles(directory="allure-results"), name="allure-results")
app.mount("/allure-report", StaticFiles(directory="allure-report"), name="allure-report")
# 挂载静态文件目录以提供前端页面访问
app.mount("/static", StaticFiles(directory=".", html=True), name="static")
# 挂载results目录以提供hrp测试报告访问
app.mount("/results", StaticFiles(directory="results"), name="results")

# 初始化服务
test_case_service = TestCaseConversionService()
langchain_service = LangChainService()
test_case_management_service = TestCaseManagementService()

class SeparateTestPointsRequest(BaseModel):
    test_cases_content: str

class SeparateTestPointsResponse(BaseModel):
    success: bool
    separated_test_points: List[Dict[str, Any]]
    grouped_test_points: Dict[str, List[Dict[str, Any]]]
    total_points: int
    error: Optional[str] = None

class BatchExecuteTestsRequest(BaseModel):
    test_points: List[Dict[str, Any]]
    group_name: Optional[str] = None

class BatchExecuteTestsResponse(BaseModel):
    success: bool
    group_name: Optional[str]
    execution_results: List[Dict[str, Any]]
    total_executed: int
    error: Optional[str] = None

class IntegrateReportsRequest(BaseModel):
    reports: List[Dict[str, Any]]

class IntegrateReportsResponse(BaseModel):
    success: bool
    integrated_report: Dict[str, Any]
    formatted_report: str
    error: Optional[str] = None

class ReportInfo(BaseModel):
    """报告信息模型"""
    report_id: str
    report_path: str
    report_url: str
    created_at: float
    last_modified: float

class ReportsListResponse(BaseModel):
    """报告列表响应模型"""
    success: bool
    reports: List[ReportInfo]
    total: int
    error: Optional[str] = None

class LatestReportResponse(BaseModel):
    """最新报告响应模型"""
    success: bool
    latest_report: Optional[ReportInfo] = None
    error: Optional[str] = None

class TestCaseRequest(BaseModel):
    test_case_description: str
    template_type: Optional[str] = "pytest"
    parser_prompt_template: Optional[str] = None
    generator_prompt_template: Optional[str] = None
    generation_type: Optional[str] = "script"

class BatchTestCaseRequest(BaseModel):
    test_cases: List[str]
    template_type: Optional[str] = "pytest"
    parser_prompt_template: Optional[str] = None
    generator_prompt_template: Optional[str] = None

class TestExecutionRequest(BaseModel):
    script_content: str

class TestCaseResponse(BaseModel):
    status: str
    generated_script: Optional[str] = None
    generated_test_cases: Optional[Union[str, List[dict]]] = None
    generated_test_data: Optional[str] = None
    metadata: dict

class BatchTestCaseResponse(BaseModel):
    status: str
    results: List[dict]

class TestExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    report_path: Optional[str] = None

class AIAnalysisRequest(BaseModel):
    test_report_path: str
    execution_result: TestExecutionResponse

class AIAnalysisResponse(BaseModel):
    success: bool
    analysis: str
    error: Optional[str] = None

class StructuredAIAnalysisResponse(BaseModel):
    """结构化AI分析结果响应模型"""
    success: bool
    # 各部分分析结果
    first_part: str = ""  # 第一部分
    second_part: str = ""  # 第二部分
    third_part: str = ""  # 第三部分
    summary: str = ""  # 总结
    error: Optional[str] = None

@app.post("/api/v1/convert-test-case", response_model=TestCaseResponse)
async def convert_test_case(request: TestCaseRequest):
    """转换单个测试用例"""
    try:
        result = test_case_service.convert_single_case(
            test_case_description=request.test_case_description,
            parser_prompt_template=request.parser_prompt_template,
            generator_prompt_template=request.generator_prompt_template,
            generation_type=request.generation_type
        )
        
        # 检查是否有错误
        if result.get("status") == "error":
            raise HTTPException(status_code=500, detail=f"处理测试用例时出错: {result.get('error')}")
        
        return TestCaseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理测试用例时出错: {str(e)}")

@app.post("/api/v1/batch-convert", response_model=BatchTestCaseResponse)
async def batch_convert(request: BatchTestCaseRequest):
    """批量转换测试用例"""
    try:
        result = test_case_service.convert_batch_cases(
            test_cases=request.test_cases,
            parser_prompt_template=request.parser_prompt_template,
            generator_prompt_template=request.generator_prompt_template
        )
        return BatchTestCaseResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理测试用例时出错: {str(e)}")

@app.post("/api/v1/execute-test", response_model=TestExecutionResponse)
async def execute_test_script(request: TestExecutionRequest):
    """执行测试脚本并生成HTML报告"""
    # 确保reports目录存在
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    # 测试数据目录
    testcases_dir = "demo/testcases"
    
    try:
        # 遍历目录下所有.yml文件
        yml_files = []
        for filename in os.listdir(testcases_dir):
            if filename.endswith('.yml'):
                yml_files.append(os.path.join(testcases_dir, filename))
        
        if not yml_files:
            raise HTTPException(status_code=404, detail="在demo/testcases/目录下未找到.yml文件")
        
        # 使用指定路径的hrp工具执行测试并生成HTML报告
        hrp_path = "C:\\Users\\62411\\Project\\LLMProjects\\TestAssistiant\\hrp-v4.3.5-windows-amd64\\hrp.exe"
        
        # 构建命令，将所有yml文件作为参数
        cmd = [hrp_path, 'run'] + yml_files + ['--gen-html-report']
        
        logger.info(f"执行命令: {' '.join(cmd)}")
        
        # 执行命令，指定编码为utf-8以避免中文乱码问题
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, encoding='utf-8')
        
        # 查找生成的HTML报告路径
        report_path = None
        # hrp工具默认将HTML报告生成在results目录下，按照时间戳命名的子目录中
        results_dir = "results"
        if os.path.exists(results_dir):
            # 获取最新的报告目录（按修改时间排序）
            subdirs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
            if subdirs:
                latest_dir = max(subdirs, key=lambda x: os.path.getmtime(os.path.join(results_dir, x)))
                report_path = os.path.join("results", latest_dir, "report.html")
                
        # 返回执行结果
        # 即使测试失败，只要hrp命令本身执行成功，我们也认为执行成功
        return TestExecutionResponse(
            success=True,
            output=result.stdout,
            error=result.stderr if result.stderr else None,
            report_path=report_path
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="测试执行超时")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试执行失败: {str(e)}")


@app.post("/api/v1/analyze-results", response_model=AIAnalysisResponse)
async def analyze_test_results(request: AIAnalysisRequest):
    """分析测试结果"""
    try:
        # 读取测试报告内容
        test_report_content = ""
        if request.test_report_path and os.path.exists(request.test_report_path):
            with open(request.test_report_path, 'r', encoding='utf-8') as f:
                test_report_content = f.read()
        
        # 调用LangChain服务进行分析
        analysis = langchain_service.analyze_test_results(
            test_report=test_report_content,
            execution_result=request.execution_result
        )
        
        return AIAnalysisResponse(
            success=True,
            analysis=analysis,
            error=None
        )
    except Exception as e:
        return AIAnalysisResponse(
            success=False,
            analysis="",
            error=str(e)
        )

@app.post("/api/v1/analyze-results-structured", response_model=StructuredAIAnalysisResponse)
async def analyze_test_results_structured(request: AIAnalysisRequest):
    """分析测试结果并返回结构化数据"""
    try:
        # 读取测试报告内容
        test_report_content = ""
        if request.test_report_path and os.path.exists(request.test_report_path):
            with open(request.test_report_path, 'r', encoding='utf-8') as f:
                test_report_content = f.read()
        
        # 调用LangChain服务进行分析
        analysis = langchain_service.analyze_test_results(
            test_report=test_report_content,
            execution_result=request.execution_result
        )
        
        # 解析分析结果
        parsed_result = parse_ai_analysis_result(analysis)
        
        # 缓存AI分析报告到根路径的MD文件
        cache_ai_analysis_report(parsed_result)
        
        return StructuredAIAnalysisResponse(
            success=True,
            first_part=parsed_result["first_part"],
            second_part=parsed_result["second_part"],
            third_part=parsed_result["third_part"],
            summary=parsed_result["summary"],
            error=None
        )
    except Exception as e:
        return StructuredAIAnalysisResponse(
            success=False,
            first_part="",
            second_part="",
            third_part="",
            summary="",
            error=str(e)
        )

@app.post("/api/v1/separate-test-points", response_model=SeparateTestPointsResponse)
async def separate_test_points(request: SeparateTestPointsRequest):
    """将测试用例内容分离为独立的测试要点"""
    try:
        # 分离测试要点
        separated_points = test_case_management_service.separate_test_points(request.test_cases_content)
        
        # 按逻辑分组
        grouped_points = test_case_management_service.group_test_cases_by_logic(separated_points)
        
        return SeparateTestPointsResponse(
            success=True,
            separated_test_points=separated_points,
            grouped_test_points=grouped_points,
            total_points=len(separated_points)
        )
    except Exception as e:
        return SeparateTestPointsResponse(
            success=False,
            separated_test_points=[],
            grouped_test_points={},
            total_points=0,
            error=str(e)
        )

@app.post("/api/v1/batch-execute-tests", response_model=BatchExecuteTestsResponse)
async def batch_execute_tests(request: BatchExecuteTestsRequest):
    """批量执行测试用例"""
    execution_results = []
    
    try:
        for test_point in request.test_points:
            # 记录开始时间
            start_time = time.time()
            
            # 为每个测试要点生成测试脚本
            script_result = test_case_service.convert_single_case(
                test_case_description=test_point.get("content", ""),
                generation_type="script"
            )
            
            if script_result.get("status") != "success":
                # 生成脚本失败
                execution_result = {
                    "test_case_id": test_point.get("id", "unknown"),
                    "test_case_title": test_point.get("title", "未知测试用例"),
                    "success": False,
                    "output": "",
                    "error": f"生成测试脚本失败: {script_result.get('error', '未知错误')}",
                    "execution_time": time.time() - start_time,
                    "timestamp": time.time()
                }
            else:
                # 执行测试脚本
                script_content = script_result.get("generated_script", "")
                execute_request = TestExecutionRequest(script_content=script_content)
                
                try:
                    # 调用现有的执行测试接口
                    execute_response = await execute_test_script(execute_request)
                    execution_result = {
                        "test_case_id": test_point.get("id", "unknown"),
                        "test_case_title": test_point.get("title", "未知测试用例"),
                        "success": execute_response.success,
                        "output": execute_response.output,
                        "error": execute_response.error,
                        "execution_time": time.time() - start_time,
                        "timestamp": time.time()
                    }
                except Exception as e:
                    execution_result = {
                        "test_case_id": test_point.get("id", "unknown"),
                        "test_case_title": test_point.get("title", "未知测试用例"),
                        "success": False,
                        "output": "",
                        "error": f"执行测试失败: {str(e)}",
                        "execution_time": time.time() - start_time,
                        "timestamp": time.time()
                    }
            
            execution_results.append(execution_result)
        
        return BatchExecuteTestsResponse(
            success=True,
            group_name=request.group_name,
            execution_results=execution_results,
            total_executed=len(execution_results)
        )
    except Exception as e:
        return BatchExecuteTestsResponse(
            success=False,
            group_name=request.group_name,
            execution_results=[],
            total_executed=0,
            error=str(e)
        )

@app.post("/api/v1/integrate-reports", response_model=IntegrateReportsResponse)
async def integrate_test_reports(request: IntegrateReportsRequest):
    """整合多个测试报告为统一报告"""
    try:
        # 整合报告
        integrated_report = test_case_management_service.integrate_test_reports(request.reports)
        
        # 格式化报告用于显示
        formatted_report = test_case_management_service.format_report_for_display(integrated_report)
        
        return IntegrateReportsResponse(
            success=True,
            integrated_report=integrated_report,
            formatted_report=formatted_report
        )
    except Exception as e:
        return IntegrateReportsResponse(
            success=False,
            integrated_report={},
            formatted_report="",
            error=str(e)
        )

def create_report_info(report_dir):
    """创建报告信息对象"""
    report_id = report_dir
    report_path = os.path.join("results", report_dir, "report.html")
    report_url = f"/results/{report_dir}/report.html"
    
    # 获取创建时间和修改时间
    dir_path = os.path.join("results", report_dir)
    if os.path.exists(dir_path):
        stat_info = os.stat(dir_path)
        created_at = stat_info.st_ctime
        last_modified = stat_info.st_mtime
    else:
        created_at = 0
        last_modified = 0
    
    return ReportInfo(
        report_id=report_id,
        report_path=report_path,
        report_url=report_url,
        created_at=created_at,
        last_modified=last_modified
    )

@app.get("/api/v1/reports", response_model=ReportsListResponse)
async def get_reports_list():
    """获取所有测试报告列表"""
    try:
        results_dir = "results"
        reports = []
        
        if os.path.exists(results_dir):
            # 获取所有报告目录（按修改时间排序）
            subdirs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
            for subdir in sorted(subdirs, key=lambda x: os.path.getmtime(os.path.join(results_dir, x)), reverse=True):
                # 检查report.html是否存在
                report_html_path = os.path.join(results_dir, subdir, "report.html")
                if os.path.exists(report_html_path):
                    reports.append(create_report_info(subdir))
        
        return ReportsListResponse(
            success=True,
            reports=reports,
            total=len(reports)
        )
    except Exception as e:
        return ReportsListResponse(
            success=False,
            reports=[],
            total=0,
            error=str(e)
        )

@app.get("/api/v1/reports/latest", response_model=LatestReportResponse)
async def get_latest_report():
    """获取最新的测试报告"""
    try:
        results_dir = "results"
        
        if os.path.exists(results_dir):
            # 获取所有报告目录（按修改时间排序）
            subdirs = [d for d in os.listdir(results_dir) if os.path.isdir(os.path.join(results_dir, d))]
            if subdirs:
                # 按修改时间降序排序，取第一个作为最新的
                latest_dir = max(subdirs, key=lambda x: os.path.getmtime(os.path.join(results_dir, x)))
                report_html_path = os.path.join(results_dir, latest_dir, "report.html")
                if os.path.exists(report_html_path):
                    return LatestReportResponse(
                        success=True,
                        latest_report=create_report_info(latest_dir)
                    )
        
        # 没有找到报告
        return LatestReportResponse(
            success=False,
            latest_report=None,
            error="没有找到可用的测试报告"
        )
    except Exception as e:
        return LatestReportResponse(
            success=False,
            latest_report=None,
            error=str(e)
        )

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

def cache_ai_analysis_report(parsed_result: dict) -> None:
    """
    缓存AI分析报告到根路径的MD文件
    
    Args:
        parsed_result: 解析后的AI分析结果字典
    """
    try:
        # 构建报告内容
        report_content = f"""# AI测试分析报告

## 第一部分：测试案例分析

{parsed_result.get('first_part', '').replace('：测试案例分析', '').replace(':测试案例分析', '').lstrip()}

## 第二部分：测试结果分析

{parsed_result.get('second_part', '').replace('：测试结果分析', '').replace(':测试结果分析', '').lstrip()}

## 第三部分：指导建议

{parsed_result.get('third_part', '').replace('：指导建议', '').replace(':指导建议', '').lstrip()}

## 总结

{parsed_result.get('summary', '').replace('：总结', '').replace(':总结', '').lstrip()}
"""
        
        # 写入到根路径的analysis_report.md文件
        with open("analysis_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
            
    except Exception as e:
        # 记录错误但不中断主流程
        logger.error(f"缓存AI分析报告时出错: {e}")

def parse_ai_analysis_result(analysis_text: str) -> dict:
    """
    解析AI分析结果，按照指定标识分割内容
    
    Args:
        analysis_text: AI生成的分析文本
        
    Returns:
        dict: 包含各部分分析结果的字典
    """
    # 初始化各部分内容
    result = {
        "first_part": "",
        "second_part": "",
        "third_part": "",
        "summary": ""
    }
    
    # 定义分割标识
    markers = ["第一部分", "第二部分", "第三部分", "总结"]
    
    # 查找各部分位置
    positions = []
    for marker in markers:
        pos = analysis_text.find(marker)
        positions.append((marker, pos))
    
    # 过滤掉未找到的部分
    positions = [(marker, pos) for marker, pos in positions if pos != -1]
    
    # 按位置排序
    positions.sort(key=lambda x: x[1])
    
    # 提取各部分内容
    for i in range(len(positions)):
        marker, start_pos = positions[i]
        # 找到下一个部分的开始位置，如果没有则是文本末尾
        end_pos = positions[i+1][1] if i+1 < len(positions) else len(analysis_text)
        
        # 提取内容（去掉标识本身）
        content = analysis_text[start_pos:end_pos].strip()
        # 移除标识前缀
        if content.startswith(marker):
            content = content[len(marker):].strip()
        
        # 根据标识分配到对应部分
        if marker == "第一部分":
            result["first_part"] = content
        elif marker == "第二部分":
            result["second_part"] = content
        elif marker == "第三部分":
            result["third_part"] = content
        elif marker == "总结":
            result["summary"] = content
    
    return result

if __name__ == "__main__":
    import uvicorn
    
    # 从配置文件中获取主机和端口信息
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False,
    )