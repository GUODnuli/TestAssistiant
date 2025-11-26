import os
from typing import Optional
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

class Config:
    # OpenAI配置
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    
    # Azure OpenAI配置
    AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    # Qwen模型配置
    QWEN_API_KEY: str = os.getenv("QWEN_API_KEY", "sk-27d4a0ea78a84a6f92b02d84521e32c7")
    ALIYUN_BASE_URL: str = os.getenv("ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    QWEN3_MAX: str = os.getenv("QWEN3_MAX", "qwen3-max")
    
    # 服务配置
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8002"))
    BACKEND_SERVICE_URL: str = os.getenv("BACKEND_SERVICE_URL", "http://localhost:8002")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LangChain配置
    LANGCHAIN_TRACING_V2: bool = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    LANGCHAIN_ENDPOINT: str = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    LANGCHAIN_API_KEY: str = os.getenv("LANGCHAIN_API_KEY", "")
    LANGCHAIN_PROJECT: str = os.getenv("LANGCHAIN_PROJECT", "default")
    
    # 模型配置
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    MODEL_TEMPERATURE: float = float(os.getenv("MODEL_TEMPERATURE", "0.7"))
    
    # 模型提供商选择
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "openai")  # openai, azure, custom, or qwen