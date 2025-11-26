#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Excel文件中提取测试用例的脚本
"""
import pandas as pd
import sys
import os

def extract_test_cases_from_excel(file_path):
    """
    从Excel文件中提取测试用例
    
    Args:
        file_path (str): Excel文件路径
        
    Returns:
        str: 提取的测试用例内容
    """
    try:
        # 读取Excel文件的所有工作表
        excel_file = pd.ExcelFile(file_path)
        all_test_cases = []
        
        for sheet_name in excel_file.sheet_names:
            # 读取每个工作表
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # 将DataFrame转换为文本格式
            sheet_content = f"工作表: {sheet_name}\n"
            sheet_content += df.to_string(index=False)
            sheet_content += "\n" + "="*50 + "\n"
            
            all_test_cases.append(sheet_content)
            
        return '\n'.join(all_test_cases)
    except Exception as e:
        raise Exception(f"读取Excel文件时出错: {str(e)}")

def main():
    if len(sys.argv) != 2:
        print("使用方法: python extract_test_cases.py <excel_file_path>")
        sys.exit(1)
        
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
        
    try:
        content = extract_test_cases_from_excel(file_path)
        print(content)
    except Exception as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()