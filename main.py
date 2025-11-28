from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union, Dict, Any
from services.test_case_service import TestCaseConversionService
from services.langchain_service import LangChainService
from services.test_case_management_service import TestCaseManagementService
from config import Config
import tempfile
import subprocess
import os
import time

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
    metadata: dict

class BatchTestCaseResponse(BaseModel):
    status: str
    results: List[dict]

class TestExecutionResponse(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None

class AIAnalysisRequest(BaseModel):
    test_case: str
    execution_result: TestExecutionResponse

class AIAnalysisResponse(BaseModel):
    success: bool
    analysis: str
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
    # 创建临时文件来保存测试脚本
    # 根据script_content内容判断是YAML还是Python文件
    if request.script_content.strip().startswith('name:') or 'teststeps:' in request.script_content:
        # YAML格式
        suffix = '.yml'
    else:
        # Python格式
        suffix = '.py'
    
    with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
        f.write(request.script_content)
        temp_script_path = f.name
    
    # 确保reports目录存在
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    
    try:
        # 使用指定路径的hrp工具执行测试并生成HTML报告
        hrp_path = "/Users/Zhuanz/001-TRAE/AI-langchain-1030/hrp-v4.3.5-darwin-amd64/hrp"
        
        # 根据文件后缀选择执行命令
        if suffix == '.yml':
            # 对于YAML文件，使用hrp run命令
            cmd = [hrp_path, 'run', temp_script_path, '--gen-html-report']
        else:
            # 对于Python文件，使用hrp pytest命令
            cmd = [hrp_path, 'pytest', temp_script_path, '--gen-html-report']
        
        # 执行命令
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60  # 60秒超时
        )
        
        # 删除临时文件
        os.unlink(temp_script_path)
        
        # 返回执行结果
        # 即使测试失败，只要hrp命令本身执行成功，我们也认为执行成功
        return TestExecutionResponse(
            success=True,
            output=result.stdout,
            error=result.stderr if result.stderr else None
        )
    except subprocess.TimeoutExpired:
        # 删除临时文件
        os.unlink(temp_script_path)
        raise HTTPException(status_code=408, detail="测试执行超时")
    except Exception as e:
        # 删除临时文件
        if os.path.exists(temp_script_path):
            os.unlink(temp_script_path)
        raise HTTPException(status_code=500, detail=f"测试执行失败: {str(e)}")


@app.post("/api/v1/analyze-results", response_model=AIAnalysisResponse)
async def analyze_test_results(request: AIAnalysisRequest):
    """分析测试结果"""
    try:
        # 调用LangChain服务进行分析
        analysis = langchain_service.analyze_test_results(
            test_case=request.test_case,
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

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # 从配置文件中获取主机和端口信息
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )