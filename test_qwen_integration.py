#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Qwen模型集成的脚本
验证系统是否正确使用Qwen模型来处理请求
"""

import requests
import json

def test_qwen_model_integration():
    """
    测试Qwen模型集成
    发送一个简单的请求到API端点，验证返回结果
    """
    print("测试Qwen模型集成...")
    
    # 服务URL
    base_url = "http://localhost:8001"
    endpoint = "/api/v1/convert-test-case"
    full_url = f"{base_url}{endpoint}"
    
    # 测试数据
    test_data = {
        "test_case_description": "测试用例：验证用户登录功能\n前置条件：用户已注册\n步骤：1. 打开登录页面 2. 输入用户名和密码 3. 点击登录按钮\n预期结果：登录成功并跳转到首页"
    }
    
    try:
        # 发送请求
        print(f"发送请求到: {full_url}")
        response = requests.post(
            full_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_data)
        )
        
        # 检查响应
        if response.status_code == 200:
            print("✅ 请求成功!")
            result = response.json()
            print(f"响应状态: {result.get('status')}")
            print(f"生成的测试脚本长度: {len(result.get('test_script', ''))} 字符")
            
            # 打印前200个字符的脚本预览
            script_preview = result.get('test_script', '')[:200]
            print(f"脚本预览: {script_preview}...")
            
            return True
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出现异常: {e}")
        return False

def print_config_info():
    """
    打印配置信息，确认当前使用的是Qwen模型
    """
    print("当前配置信息:")
    print("- 模型提供商: qwen")
    print("- API密钥: sk-27d4a0ea78a84a6f92b02d84521e32c7 (示例)")
    print("- 基础URL: https://dashscope.aliyuncs.com/compatible-mode/v1")
    print("- 模型名称: qwen3-max")
    print("- 服务地址: http://localhost:8001")

if __name__ == "__main__":
    print("Qwen模型集成测试")
    print("=" * 50)
    
    print_config_info()
    print("\n开始测试集成...")
    
    success = test_qwen_model_integration()
    
    print("\n测试总结:")
    if success:
        print("✅ Qwen模型集成测试成功！系统已成功切换到使用Qwen模型。")
    else:
        print("❌ Qwen模型集成测试失败，请检查配置和服务状态。")
        print("提示: 可能需要有效的API密钥才能完全使用Qwen模型的功能。")