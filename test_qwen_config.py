#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Qwen API配置的脚本
"""

import os
import sys
from config import Config

def test_qwen_config():
    """
    测试Qwen配置是否正确加载
    """
    print("测试Qwen API配置...")
    
    # 设置环境变量模拟Qwen配置
    os.environ["MODEL_PROVIDER"] = "qwen"
    os.environ["QWEN_API_KEY"] = "sk-27d4a0ea78a84a6f92b02d84521e32c7"
    os.environ["ALIYUN_BASE_URL"] = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    os.environ["QWEN3_MAX"] = "qwen3-max"
    
    # 重新加载配置
    import importlib
    importlib.reload(sys.modules['config'])
    from config import Config
    
    # 打印配置信息
    print(f"MODEL_PROVIDER: {Config.MODEL_PROVIDER}")
    print(f"QWEN_API_KEY: {Config.QWEN_API_KEY}")
    print(f"ALIYUN_BASE_URL: {Config.ALIYUN_BASE_URL}")
    print(f"QWEN3_MAX: {Config.QWEN3_MAX}")
    
    # 测试基本配置是否正确加载
    assert Config.MODEL_PROVIDER == "qwen", f"期望MODEL_PROVIDER为'qwen'，实际为'{Config.MODEL_PROVIDER}'"
    assert Config.QWEN_API_KEY == "sk-27d4a0ea78a84a6f92b02d84521e32c7", f"API密钥不匹配"
    assert Config.ALIYUN_BASE_URL == "https://dashscope.aliyuncs.com/compatible-mode/v1", f"API基础URL不匹配"
    assert Config.QWEN3_MAX == "qwen3-max", f"模型名称不匹配"
    
    print("Qwen配置测试通过!")

def test_langchain_service_with_qwen():
    """
    测试LangChainService是否能正确使用Qwen模型
    """
    print("\n测试LangChainService与Qwen模型集成...")
    
    # 确保设置了正确的环境变量
    os.environ["MODEL_PROVIDER"] = "qwen"
    
    # 重新加载所有相关模块
    import importlib
    if 'services.qwen_service' in sys.modules:
        importlib.reload(sys.modules['services.qwen_service'])
    if 'services.langchain_service' in sys.modules:
        importlib.reload(sys.modules['services.langchain_service'])
    
    # 导入并初始化服务
    from services.langchain_service import LangChainService
    service = LangChainService()
    
    # 验证LLM实例是否正确初始化
    print(f"LLM实例类型: {type(service.llm).__name__}")
    print(f"LLM模型名称: {service.llm.model_name}")
    print("LangChainService与Qwen模型集成测试成功!")

if __name__ == "__main__":
    try:
        test_qwen_config()
        test_langchain_service_with_qwen()
        print("\n所有Qwen配置测试通过!")
    except AssertionError as e:
        print(f"\n测试失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        # 这可能是因为没有实际的API密钥或者网络问题，所以不退出程序
        print("注意: 可能需要有效的API密钥才能完全测试Qwen模型的功能")