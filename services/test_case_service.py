from math import log
from typing import Dict, List
import logging

# 配置日志，确保输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# 初始化logger
logger = logging.getLogger(__name__)
# 修复导入问题，确保使用正确的导入路径
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

    def _serialize_yaml_content(self, content, test_point):
        """序列化YAML内容，确保格式正确"""
        if isinstance(content, dict):
            # 如果是字典，转换为字符串格式
            lines = [f"# 测试用例: {test_point}"]
            for key, value in content.items():
                lines.append(f"{key}: {value}")
            return "\n".join(lines)
        else:
            # 如果是字符串，直接返回
            return str(content)
    
    def convert_single_case(self, test_case_description: str, 
                           parser_prompt_template: str = None, generator_prompt_template: str = None,
                           generation_type: str = "test_cases") -> Dict:
        """转换测试要点为测试用例或生成测试数据文件"""
            
        # 根据生成类型调用相应的函数
        if generation_type == "test_data":
            # 生成测试数据并保存为yml文件
            test_points = self._split_test_points(test_case_description)
            saved_files = []
            serialized_cases = []
            
            # 确保demo/testcases目录存在
            testcases_dir = os.path.join("demo", "testcases")
            if not os.path.exists(testcases_dir):
                os.makedirs(testcases_dir)
            
            # 逐条处理测试要点并生成yml文件
            for i, test_point in enumerate(test_points, 1):
                # 生成测试用例内容
                generated_content = self.langchain_service.generate_test_script(
                    test_case=test_point
                )
                logger.info(f"已生成测试数据 #{i}: {generated_content}")
                
                # 创建文件名
                file_name = f"TC{i:03d}-{self._generate_safe_filename(test_point)}.yml"
                file_path = os.path.join(testcases_dir, file_name)
                
                # 序列化内容
                serialized_content = self._serialize_yaml_content(generated_content, test_point)
                
                # 保存到文件
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(serialized_content)
                    saved_files.append(file_name)
                    
                    # 将序列化后的内容添加到结果中，每个测试用例添加编号
                    serialized_cases.append(f"测试用例{i}:\n{serialized_content}")
                except Exception as e:
                    print(f"保存文件 {file_name} 失败: {str(e)}")
            
            # 组合所有序列化后的测试用例为纯文本
            combined_cases_text = "\n\n".join(serialized_cases)
            
            generated_content = {
                "saved_files": saved_files,
                "total_files": len(saved_files),
                "directory": testcases_dir,
                "serialized_cases": combined_cases_text
            }
        else:
            # 默认生成测试用例
            generated_content = self.langchain_service.generate_test_cases_from_rules(
                requirements=test_case_description
            )
        
        # 根据生成类型返回不同的字段名
        result = {
            "status": "success",
            "metadata": {
                "input_content": test_case_description,
                "generation_type": generation_type
            }
        }
        
        if generation_type == "test_data":
            # 直接返回serialized_cases作为纯文本
            result["generated_test_data"] = combined_cases_text
        else:
            result["generated_test_cases"] = generated_content
            
        return result
    
    def _split_test_points(self, test_points_text: str) -> List[str]:
        """将测试要点文本分割成单个测试要点列表"""
        # 使用标准库字符串操作函数进行分割
        # 1. 去除首尾空白字符
        test_points_text = test_points_text.strip()
        
        # 2. 处理空格分隔的测试场景（根据日志中的格式特征）
        # 从日志看，输入格式可能是："12个月-... 12个月-... 24个月-..."
        # 我们可以按空格分割，然后过滤空字符串
        test_points = [point.strip() for point in test_points_text.split() if point.strip()]
        
        return test_points
    
    def _generate_safe_filename(self, text: str) -> str:
        """生成安全的文件名"""
        # 移除特殊字符，只保留字母、数字、中文和下划线
        import re
        # 保留中文、英文、数字和下划线，其他替换为下划线
        safe_name = re.sub(r'[^\w\u4e00-\u9fa5]+', '_', text)
        # 截取前30个字符
        return safe_name[:30]

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