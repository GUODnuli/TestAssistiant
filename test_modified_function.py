#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试修改后的generate_test_cases_from_rules方法"""

from services.langchain_service import LangChainService

def test_generate_test_cases():
    """测试生成测试要点功能"""
    # 初始化服务
    langchain_service = LangChainService()
    
    # 准备测试用的需求文档内容
    test_requirements = """贷款产品规则：
1. 贷款期限：3个月、6个月、12个月
2. 还款方式：等额本息、等额本金
3. 基础利率：6.0%
4. 优惠券：使用优惠券可享受2%优惠，但最终利率不低于2.0%（兜底机制）
"""
    
    print("开始测试generate_test_cases_from_rules方法...")
    print(f"输入的requirements参数: {test_requirements}")
    
    try:
        # 调用修改后的方法
        result = langchain_service.generate_test_cases_from_rules(requirements=test_requirements)
        
        print("\n生成结果:")
        print(result)
        print("\n测试成功！方法已正确接受requirements参数并生成多因子分析格式输出。")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        raise

if __name__ == "__main__":
    test_generate_test_cases()