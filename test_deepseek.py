#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试DeepSeek API配置的脚本
"""

import os
import sys
from config import Config

def test_deepseek_config():
    """测试DeepSeek配置"""
    print("测试DeepSeek API配置...")
    
    # 设置环境变量模拟DeepSeek配置
    os.environ["MODEL_PROVIDER"] = "custom"
    os.environ["OPENAI_API_KEY"] = "sk-9ceeb7a2324c461d9f8a45a6c95b13b5"
    os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
    
    # 重新加载配置
    import importlib
    importlib.reload(sys.modules['config'])
    from config import Config
    
    config = Config()
    print(f"MODEL_PROVIDER: {config.MODEL_PROVIDER}")
    print(f"OPENAI_API_KEY: {config.OPENAI_API_KEY}")
    print(f"OPENAI_API_BASE: {config.OPENAI_API_BASE}")
    
    # 测试基本配置是否正确加载
    assert config.MODEL_PROVIDER == "custom", f"期望MODEL_PROVIDER为'custom'，实际为'{config.MODEL_PROVIDER}'"
    assert config.OPENAI_API_KEY == "sk-9ceeb7a2324c461d9f8a45a6c95b13b5", f"API密钥不匹配"
    assert config.OPENAI_API_BASE == "https://api.deepseek.com/v1", f"API基础URL不匹配"
    
    print("DeepSeek配置测试通过!")

def main():
    """主函数"""
    print("开始测试DeepSeek API配置...")
    
    # 保存原始环境变量
    original_provider = os.environ.get("MODEL_PROVIDER")
    original_openai_key = os.environ.get("OPENAI_API_KEY")
    original_api_base = os.environ.get("OPENAI_API_BASE")
    
    try:
        test_deepseek_config()
    except Exception as e:
        print(f"DeepSeek配置测试失败: {e}")
        sys.exit(1)
    finally:
        # 恢复原始环境变量
        if original_provider is not None:
            os.environ["MODEL_PROVIDER"] = original_provider
        if original_openai_key is not None:
            os.environ["OPENAI_API_KEY"] = original_openai_key
        if original_api_base is not None:
            os.environ["OPENAI_API_BASE"] = original_api_base
    
    print("所有测试完成!")

if __name__ == "__main__":
    main()