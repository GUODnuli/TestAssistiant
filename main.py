from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Union
from services.test_case_service import TestCaseConversionService
from services.langchain_service import LangChainService
import tempfile
import subprocess
import os

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
    """执行测试脚本并生成Allure报告"""
    # 创建临时文件来保存测试脚本
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(request.script_content)
        temp_script_path = f.name
    
    # 确保allure-results目录存在
    allure_results_dir = "allure-results"
    os.makedirs(allure_results_dir, exist_ok=True)
    
    try:
        # 执行测试脚本并生成Allure结果
        # 注意：在生产环境中，您可能需要更安全的执行方式
        result = subprocess.run(
            ['python3', '-m', 'pytest', temp_script_path, '-v', f'--alluredir={allure_results_dir}'],
            capture_output=True,
            text=True,
            timeout=30  # 30秒超时
        )
        
        # 删除临时文件
        os.unlink(temp_script_path)
        
        # 返回执行结果
        # 即使测试失败，只要pytest命令本身执行成功，我们也认为执行成功
        return TestExecutionResponse(
            success=True,  # pytest命令执行成功
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

@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # 由于端口8000被占用，使用8001端口
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8001,
        reload=True
    )