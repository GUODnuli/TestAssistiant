#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek API使用示例脚本
展示如何使用DeepSeek API进行测试用例转换
"""

import os
import sys
import json

# 设置环境变量以使用DeepSeek API
os.environ["MODEL_PROVIDER"] = "custom"
os.environ["OPENAI_API_KEY"] = "sk-9ceeb7a2324c461d9f8a45a6c95b13b5"
os.environ["OPENAI_API_BASE"] = "https://api.deepseek.com/v1"
os.environ["MODEL_NAME"] = "deepseek-chat"

def example_single_test_case_conversion():
    """单个测试用例转换示例"""
    print("=== 单个测试用例转换示例 ===")
    
    # 导入必要的模块
    try:
        from services.test_case_service import TestCaseService
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖包")
        return
    
    # 创建测试用例服务实例
    service = TestCaseService()
    
    # 示例接口文档内容
    context = """
    接口名称: 用户登录
    请求方法: POST
    请求路径: /api/v1/login
    请求参数:
    - username: 用户名 (字符串, 必填)
    - password: 密码 (字符串, 必填)
    
    响应:
    - 成功: {"code": 200, "message": "登录成功", "data": {"token": "xxx"}}
    - 失败: {"code": 400, "message": "用户名或密码错误"}
    """
    
    # 示例测试用例
    input_text = "输入正确的用户名和密码，验证能否成功登录并返回token"
    
    try:
        print("正在转换测试用例...")
        result = service.convert_single_test_case(context, input_text)
        print("转换结果:")
        print(result)
        print("\n")
    except Exception as e:
        print(f"转换过程中出现错误: {e}")

def example_batch_test_case_conversion():
    """批量测试用例转换示例"""
    print("=== 批量测试用例转换示例 ===")
    
    # 导入必要的模块
    try:
        from services.test_case_service import TestCaseService
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖包")
        return
    
    # 创建测试用例服务实例
    service = TestCaseService()
    
    # 示例接口文档内容
    context = """
    接口名称: 用户注册
    请求方法: POST
    请求路径: /api/v1/register
    请求参数:
    - username: 用户名 (字符串, 必填, 6-20字符)
    - email: 邮箱 (字符串, 必填)
    - password: 密码 (字符串, 必填, 8-20字符)
    
    响应:
    - 成功: {"code": 200, "message": "注册成功"}
    - 失败: {"code": 400, "message": "参数错误"}
    """
    
    # 示例测试用例列表
    inputs = [
        "输入有效的用户名、邮箱和密码，验证能否成功注册",
        "输入已存在的用户名，验证是否返回错误信息",
        "输入无效的邮箱格式，验证是否返回错误信息"
    ]
    
    try:
        print("正在批量转换测试用例...")
        results = service.convert_batch_test_cases(context, inputs)
        print("批量转换结果:")
        for i, result in enumerate(results):
            print(f"\n测试用例 {i+1}:")
            print(result)
        print("\n")
    except Exception as e:
        print(f"批量转换过程中出现错误: {e}")

def main():
    """主函数"""
    print("DeepSeek API测试用例转换示例")
    print("=" * 50)
    
    # 首先测试配置是否正确
    print("1. 测试DeepSeek API配置...")
    try:
        from config import Config
        config = Config()
        print(f"   MODEL_PROVIDER: {config.MODEL_PROVIDER}")
        print(f"   OPENAI_API_KEY: {config.OPENAI_API_KEY[:10]}..." if config.OPENAI_API_KEY else "   OPENAI_API_KEY: 未设置")
        print(f"   OPENAI_API_BASE: {config.OPENAI_API_BASE}")
        print(f"   MODEL_NAME: {config.MODEL_NAME}")
        print("   配置测试通过!\n")
    except Exception as e:
        print(f"   配置测试失败: {e}")
        sys.exit(1)
    
    # 运行示例
    example_single_test_case_conversion()
    example_batch_test_case_conversion()
    
    print("所有示例运行完成!")
    print("\n提示: 要在实际项目中使用此功能，请:")
    print("1. 复制 .env.example 文件为 .env")
    print("2. 根据需要修改 .env 文件中的配置")
    print("3. 运行 'python main.py' 启动服务")
    print("4. 访问 http://localhost:8000/docs 查看API文档")

if __name__ == "__main__":
    main()