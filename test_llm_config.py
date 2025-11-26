#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试不同LLM提供商配置的脚本
"""

import os
import sys
from config import Config
from services.langchain_service import LangChainService

def test_openai_config():
    """测试OpenAI配置"""
    print("测试OpenAI配置...")
    os.environ["MODEL_PROVIDER"] = "openai"
    os.environ["OPENAI_API_KEY"] = "test-key"
    
    config = Config()
    print(f"MODEL_PROVIDER: {config.MODEL_PROVIDER}")
    print(f"OPENAI_API_KEY: {config.OPENAI_API_KEY}")
    
    try:
        service = LangChainService()
        print("OpenAI配置测试成功")
    except Exception as e:
        print(f"OpenAI配置测试失败: {e}")

def test_azure_config():
    """测试Azure OpenAI配置"""
    print("\n测试Azure OpenAI配置...")
    os.environ["MODEL_PROVIDER"] = "azure"
    os.environ["AZURE_OPENAI_API_KEY"] = "test-azure-key"
    os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com/"
    os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = "test-deployment"
    
    config = Config()
    print(f"MODEL_PROVIDER: {config.MODEL_PROVIDER}")
    print(f"AZURE_OPENAI_API_KEY: {config.AZURE_OPENAI_API_KEY}")
    print(f"AZURE_OPENAI_ENDPOINT: {config.AZURE_OPENAI_ENDPOINT}")
    print(f"AZURE_OPENAI_DEPLOYMENT_NAME: {config.AZURE_OPENAI_DEPLOYMENT_NAME}")
    
    try:
        service = LangChainService()
        print("Azure OpenAI配置测试成功")
    except Exception as e:
        print(f"Azure OpenAI配置测试失败: {e}")

def test_custom_config():
    """测试自定义API端点配置"""
    print("\n测试自定义API端点配置...")
    os.environ["MODEL_PROVIDER"] = "custom"
    os.environ["OPENAI_API_KEY"] = "test-custom-key"
    os.environ["OPENAI_API_BASE"] = "https://custom-api.example.com/v1"
    
    config = Config()
    print(f"MODEL_PROVIDER: {config.MODEL_PROVIDER}")
    print(f"OPENAI_API_KEY: {config.OPENAI_API_KEY}")
    print(f"OPENAI_API_BASE: {config.OPENAI_API_BASE}")
    
    try:
        service = LangChainService()
        print("自定义API端点配置测试成功")
    except Exception as e:
        print(f"自定义API端点配置测试失败: {e}")

def main():
    """主函数"""
    print("开始测试不同LLM提供商的配置...")
    
    # 保存原始环境变量
    original_provider = os.environ.get("MODEL_PROVIDER")
    original_openai_key = os.environ.get("OPENAI_API_KEY")
    original_azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
    original_azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    original_azure_deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME")
    original_api_base = os.environ.get("OPENAI_API_BASE")
    
    try:
        test_openai_config()
        test_azure_config()
        test_custom_config()
    finally:
        # 恢复原始环境变量
        if original_provider is not None:
            os.environ["MODEL_PROVIDER"] = original_provider
        if original_openai_key is not None:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        if original_azure_key is not None:
            os.environ["AZURE_OPENAI_API_KEY"] = original_azure_key
        if original_azure_endpoint is not None:
            os.environ["AZURE_OPENAI_ENDPOINT"] = original_azure_endpoint
        if original_azure_deployment is not None:
            os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"] = original_azure_deployment
        if original_api_base is not None:
            os.environ["OPENAI_API_BASE"] = original_api_base
    
    print("\n所有测试完成!")

if __name__ == "__main__":
    main()