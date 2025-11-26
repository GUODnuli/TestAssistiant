#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel文件处理工具模块
用于读取和解析Excel文件中的测试用例
"""
import pandas as pd
from typing import Dict, List
import os

class ExcelProcessor:
    """Excel文件处理器"""
    
    @staticmethod
    def extract_test_cases_from_excel(file_path: str) -> str:
        """
        从Excel文件中提取测试用例
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            str: 提取的测试用例内容
            
        Raises:
            Exception: 文件读取或处理过程中出现的错误
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 读取Excel文件的所有工作表
            excel_file = pd.ExcelFile(file_path)
            all_test_cases = []
            
            # 遍历所有工作表
            for sheet_name in excel_file.sheet_names:
                # 读取每个工作表
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # 将DataFrame转换为文本格式
                sheet_content = f"工作表: {sheet_name}\n"
                
                # 如果DataFrame不为空，转换为字符串
                if not df.empty:
                    sheet_content += df.to_string(index=False)
                else:
                    sheet_content += "（空工作表）"
                
                sheet_content += "\n" + "="*50 + "\n"
                all_test_cases.append(sheet_content)
                
            return '\n'.join(all_test_cases)
        except Exception as e:
            raise Exception(f"读取Excel文件时出错: {str(e)}")
    
    @staticmethod
    def extract_structured_test_cases_from_excel(file_path: str) -> List[Dict]:
        """
        从Excel文件中提取结构化测试用例
        
        Args:
            file_path (str): Excel文件路径
            
        Returns:
            List[Dict]: 结构化的测试用例列表
            
        Raises:
            Exception: 文件读取或处理过程中出现的错误
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 读取Excel文件的第一个工作表
            df = pd.read_excel(file_path)
            
            # 转换为结构化数据
            test_cases = []
            
            # 遍历每一行数据
            for index, row in df.iterrows():
                # 将行数据转换为字典
                case_data = {}
                for col_name in df.columns:
                    # 处理NaN值
                    value = row[col_name]
                    case_data[col_name] = "" if pd.isna(value) else str(value)
                
                test_cases.append(case_data)
                
            return test_cases
        except Exception as e:
            raise Exception(f"读取Excel文件时出错: {str(e)}")

# 使用示例
if __name__ == "__main__":
    # 示例用法
    processor = ExcelProcessor()
    
    # 提取测试用例文本
    # test_cases_text = processor.extract_test_cases_from_excel("测试用例.xlsx")
    # print(test_cases_text)
    pass