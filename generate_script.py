#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.langchain_service import LangChainService

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_script.py <input_test_case_file> <output_script_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    # 读取测试用例
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            test_case = f.read().strip()
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # 初始化LangChain服务
    langchain_service = LangChainService()
    
    # 生成测试脚本
    try:
        print("Generating test script...")
        generated_script = langchain_service.generate_test_script(test_case)
        
        # 保存生成的脚本
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(generated_script)
        
        print(f"Test script successfully generated and saved to '{output_file}'")
        
    except Exception as e:
        print(f"Error generating test script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()