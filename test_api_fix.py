import requests
import json

# 测试API端点
url = "http://localhost:8001/api/v1/convert-test-case"

# 测试数据（贷款产品规则）
test_data = {
    "test_case_description": "贷款产品规则：\n1. 贷款期限：可选12个月、24个月、36个月\n2. 还款方式：可选等额本息、等额本金\n3. 利率标准：基准利率上浮10%-30%\n4. 优惠券：新用户可使用100元优惠券",
    "generation_type": "test_cases"
}

print("正在发送请求到API端点...")
try:
    # 发送POST请求
    response = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(test_data)
    )
    
    print(f"响应状态码: {response.status_code}")
    print("响应内容:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    if response.status_code == 200:
        print("\n测试成功！API调用正常工作。")
    else:
        print(f"\n测试失败：HTTP状态码 {response.status_code}")
        
except Exception as e:
    print(f"\n请求失败：{str(e)}")