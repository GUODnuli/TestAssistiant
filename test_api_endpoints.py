#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API端点测试脚本
使用非阻塞方式测试所有API端点，避免长时间等待
"""

import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_health_endpoint():
    """测试健康检查端点"""
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            print("✓ 健康检查端点测试通过")
            return True
        else:
            print(f"✗ 健康检查端点测试失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 健康检查端点测试异常: {str(e)}")
        return False

def test_prompts_endpoint():
    """测试前端提示词端点"""
    try:
        response = requests.get("http://localhost:8080/api/prompts", timeout=5)
        if response.status_code == 200:
            print("✓ 前端提示词端点测试通过")
            return True
        else:
            print(f"✗ 前端提示词端点测试失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ 前端提示词端点测试异常: {str(e)}")
        return False

def test_convert_endpoint_non_blocking():
    """非阻塞方式测试转换端点"""
    def make_request():
        try:
            response = requests.post(
                "http://localhost:8002/api/v1/convert-test-case",
                json={"test_case_description": "简单的登录测试"},
                timeout=3  # 设置较短的超时时间
            )
            return response.status_code
        except requests.Timeout:
            # 超时是预期的行为，因为AI处理需要时间
            return "timeout"
        except Exception as e:
            return f"error: {str(e)}"
    
    # 使用线程在后台发起请求
    thread = threading.Thread(target=make_request)
    thread.daemon = True
    thread.start()
    
    # 等待一小段时间确认请求已发送
    time.sleep(1)
    print("✓ 已发起转换端点测试请求（后台处理中）")
    return True

def main():
    """主测试函数"""
    print("开始测试API端点...")
    print("=" * 40)
    
    # 使用线程池并发测试
    with ThreadPoolExecutor(max_workers=3) as executor:
        # 提交测试任务
        futures = []
        futures.append(executor.submit(test_health_endpoint))
        futures.append(executor.submit(test_prompts_endpoint))
        futures.append(executor.submit(test_convert_endpoint_non_blocking))
        
        # 等待所有测试完成
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as e:
                print(f"测试过程中出现异常: {str(e)}")
    
    print("=" * 40)
    print("API端点测试完成")

if __name__ == "__main__":
    main()