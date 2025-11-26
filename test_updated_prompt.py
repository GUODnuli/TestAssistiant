import requests
import json

# 测试因子组合数据
factor_combinations = """
3个月-等额本息-6.0%-不使用优惠券-6.0%
3个月-等额本息-6.0%-使用优惠券-2.0%
"""

# 构建测试数据
test_data = {
    "test_case_description": factor_combinations,
    "generation_type": "test_cases"
}

try:
    # 发送请求到API
    response = requests.post(
        "http://localhost:8001/api/v1/convert-test-case",
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )
    
    # 输出响应状态和内容
    print(f"响应状态码: {response.status_code}")
    print("响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    # 验证响应格式是否符合预期（是否为JSON数组）
    if response.status_code == 200:
        data = response.json()
        if data.get("status") == "success":
            generated_content = data.get("generated_test_cases", "")
            print("\n生成的测试用例内容:")
            print(generated_content)
            
            # 尝试解析为JSON以验证格式
            try:
                test_cases_json = json.loads(generated_content)
                if isinstance(test_cases_json, list):
                    print(f"\n验证成功! 生成了 {len(test_cases_json)} 个测试用例。")
                else:
                    print("\n验证失败: 生成的内容不是JSON数组。")
            except json.JSONDecodeError as e:
                print(f"\n验证失败: 生成的内容不是有效的JSON。错误: {e}")

except Exception as e:
    print(f"发生错误: {e}")