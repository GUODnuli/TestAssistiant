import os
import json
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from config import Config

class LangChainService:
    def __init__(self):
        # 初始化时加载提示词配置
        self.prompt_configs = self._load_prompt_configs()
        # 根据模型提供商初始化大语言模型
        self.llm = self._initialize_llm()
    
    def _initialize_llm(self):
        """
        根据配置初始化适当的语言模型
        
        Returns:
            初始化好的语言模型实例
        """
        if Config.MODEL_PROVIDER == "qwen":
            # 导入并使用Qwen服务
            from services.qwen_service import QwenService
            qwen_service = QwenService(
                api_key=Config.QWEN_API_KEY,
                base_url=Config.ALIYUN_BASE_URL,
                model=Config.QWEN3_MAX,
                temperature=Config.MODEL_TEMPERATURE
            )
            return qwen_service.get_llm()
        elif Config.MODEL_PROVIDER == "azure":
            # Azure OpenAI配置
            return ChatOpenAI(
                model_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME or Config.MODEL_NAME,
                temperature=Config.MODEL_TEMPERATURE,
                openai_api_key=Config.AZURE_OPENAI_API_KEY,
                openai_api_base=Config.AZURE_OPENAI_ENDPOINT,
                openai_api_version="2023-05-15"  # 根据需要调整版本
            )
        elif Config.MODEL_PROVIDER == "custom":
            # 自定义模型配置
            return ChatOpenAI(
                model_name=Config.MODEL_NAME,
                temperature=Config.MODEL_TEMPERATURE,
                openai_api_key=Config.OPENAI_API_KEY,
                openai_api_base=Config.OPENAI_API_BASE
            )
        else:
            # 默认使用OpenAI配置
            return ChatOpenAI(
                model_name=Config.MODEL_NAME,
                temperature=Config.MODEL_TEMPERATURE,
                openai_api_key=Config.OPENAI_API_KEY,
                openai_api_base=Config.OPENAI_API_BASE
            )
    
    def _load_prompt_configs(self) -> Dict[str, Any]:
        """加载提示词配置"""
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'prompts_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到提示词配置文件 {config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"错误: 提示词配置文件格式不正确 {e}")
            return {}
    
    def create_script_generator_prompt(self) -> PromptTemplate:
        """创建脚本生成提示词模板"""
        config = self.prompt_configs.get('script_generator', {})
        template = config.get('template', '')
        return PromptTemplate.from_template(template)
    
    def create_test_case_generator_prompt(self) -> PromptTemplate:
        """创建测试案例生成提示词模板"""
        config = self.prompt_configs.get('test_case_generator', {})
        template = config.get('template', '')
        return PromptTemplate.from_template(template)
        

    
    def create_ai_analysis_prompt(self) -> PromptTemplate:
        """创建AI分析提示词模板"""
        config = self.prompt_configs.get('ai_analysis', {})
        template = config.get('template', '')
        return PromptTemplate.from_template(template)

    def parse_test_case(self, context: str, input_text: str, prompt_template: str = None) -> str:
        """解析测试用例"""
        # 由于test_case_parser模板已被删除，此方法将不再使用默认模板
        if prompt_template:
            # 使用自定义提示词模板
            prompt = PromptTemplate.from_template(prompt_template)
        else:
            # 如果没有提供自定义模板，则返回错误信息
            return "错误：测试用例解析功能已被移除，请使用自定义提示词模板或test_case_generator模板。"
        # 简化的chain创建方式
        inputs = {"context": context, "input": input_text}
        formatted_prompt = prompt.format(**inputs)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def generate_test_script(self, test_case: str, prompt_template: str = None) -> str:
        """生成测试脚本"""
        if prompt_template:
            # 使用自定义提示词模板
            prompt = PromptTemplate.from_template(prompt_template)
        else:
            # 使用默认提示词模板
            prompt = self.create_script_generator_prompt()
        # 简化的chain创建方式
        inputs = {"factor_combinations": test_case}
        formatted_prompt = prompt.format(**inputs)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def generate_test_cases_from_rules(self, requirements: str) -> str:
        """根据需求生成测试用例"""
        prompt = self.create_test_case_generator_prompt()
        # 简化的chain创建方式
        inputs = {"requirements": requirements}
        formatted_prompt = prompt.format(**inputs)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def analyze_test_results(self, test_case: str, execution_result, prompt_template: str = None) -> str:
        """分析测试结果"""
        if prompt_template:
            # 使用自定义提示词模板
            prompt = PromptTemplate.from_template(prompt_template)
        else:
            # 使用默认提示词模板
            prompt = self.create_ai_analysis_prompt()
        # 简化的chain创建方式
        inputs = {
            "test_case": test_case,
            "success": execution_result.success,
            "output": execution_result.output,
            "error": execution_result.error or ""
        }
        formatted_prompt = prompt.format(**inputs)
        response = self.llm.invoke(formatted_prompt)
        return response.content

    def extract_test_cases_from_excel(self, file_path: str) -> str:
        """从Excel文件中提取测试用例"""
        # 这里应该实现Excel文件解析逻辑
        # 为了简化，我们返回一个模拟结果
        return f"从Excel文件 {file_path} 中提取的测试用例内容"