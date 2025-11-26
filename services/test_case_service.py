from typing import Dict, List
from services.langchain_service import LangChainService
import os

class TestCaseConversionService:
    def __init__(self):
        self.langchain_service = LangChainService()
        
    def extract_test_cases_from_excel(self, file_path: str) -> Dict:
        """从Excel文件中提取测试用例"""
        try:
            if not os.path.exists(file_path):
                return {
                    "status": "error",
                    "message": f"文件不存在: {file_path}"
                }
            
            # 调用LangChain服务提取Excel文件中的测试用例
            extracted_content = self.langchain_service.extract_test_cases_from_excel(file_path)
            
            return {
                "status": "success",
                "extracted_content": extracted_content
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"提取测试用例时出错: {str(e)}"
            }

    def convert_single_case(self, test_case_description: str, 
                           parser_prompt_template: str = None, generator_prompt_template: str = None,
                           generation_type: str = "script") -> Dict:
        """转换单个测试要点为自动化测试脚本或测试要点"""
            
        # 根据生成类型调用相应的函数
        if generation_type == "script":
            # 生成自动化测试脚本
            generated_content = self.langchain_service.generate_test_script(
                test_case=test_case_description,
                prompt_template=generator_prompt_template
            )
        else:
            # 生成测试用例
            generated_content = self.langchain_service.generate_test_cases_from_rules(
                requirements=test_case_description
            )
        
        # 根据生成类型返回不同的字段名
        result = {
            "status": "success",
            "metadata": {
                "input_content": test_case_description
            }
        }
        
        if generation_type == "test_cases":
            result["generated_test_cases"] = generated_content
        else:
            result["generated_script"] = generated_content
            
        return result

    def convert_batch_cases(self, test_cases: List[str],
                           parser_prompt_template: str = None, generator_prompt_template: str = None) -> Dict:
        """批量转换测试用例为自动化测试脚本"""
        results = []
        for test_case in test_cases:
            result = self.convert_single_case(
                test_case_description=test_case,
                parser_prompt_template=parser_prompt_template,
                generator_prompt_template=generator_prompt_template,
                generation_type="test_cases"
            )
            results.append({
                "input_content": test_case,
                "generated_test_cases": result["generated_test_cases"]
            })
            
        return {
            "status": "success",
            "results": results
        }