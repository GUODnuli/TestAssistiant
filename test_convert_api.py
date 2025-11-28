"""
测试用例转换API测试脚本
验证测试用例转换功能
"""

import os
import json
import logging
import requests
import pytest
import allure
from allure_commons.types import AttachmentType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ConvertTestCaseAPI:
    """测试用例转换API类"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        # 配置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
    
    def convert_test_case(self, test_case_description: str, template_type: str = "pytest") -> dict:
        """
        转换测试用例
        
        Args:
            test_case_description: 测试用例描述
            template_type: 模板类型，默认为"pytest"
            
        Returns:
            dict: 转换结果
            
        Raises:
            requests.RequestException: 网络请求异常
            ValueError: JSON解析异常
        """
        convert_url = f"{self.base_url}/api/v1/convert-test-case"
        
        payload = {
            "test_case_description": test_case_description,
            "template_type": template_type
        }
        
        try:
            logger.info("正在发送测试用例转换请求")
            response = self.session.post(
                convert_url,
                json=payload,
                timeout=30
            )
            
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = "测试用例转换请求超时"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)
            
        except requests.exceptions.ConnectionError:
            error_msg = "网络连接错误"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP错误: {e.response.status_code} - {e.response.reason}"
            logger.error(error_msg)
            raise requests.RequestException(error_msg)
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)


class TestConvertAPI:
    """测试用例转换API测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """获取基础URL"""
        return os.getenv('BASE_URL', 'http://localhost:8003')
    
    @pytest.fixture(scope="class")
    def convert_api(self, base_url: str) -> ConvertTestCaseAPI:
        """测试用例转换API fixture"""
        return ConvertTestCaseAPI(base_url)
    
    @allure.feature("测试用例转换")
    @allure.story("测试用例转换功能验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_convert_test_case(self, convert_api: ConvertTestCaseAPI):
        """
        测试测试用例转换功能
        
        验证API能否正确转换测试用例描述
        """
        test_description = "验证用户登录功能：输入正确的用户名和密码，点击登录按钮，系统应跳转到用户个人中心页面"
        
        with allure.step("步骤1: 发送测试用例转换请求"):
            convert_result = convert_api.convert_test_case(test_description)
            
            # 验证响应包含必要字段
            assert 'status' in convert_result, "响应中缺少status字段"
            
            status = convert_result['status']
            logger.info(f"测试用例转换状态: {status}")
        
        with allure.step("步骤2: 验证转换成功"):
            # 验证状态为success或其他表示成功的状态
            assert status in ["success", "Success", "successful"], f"测试用例转换失败: 状态为 '{status}'"
            
            logger.info("测试用例转换成功")
            
            # 在allure报告中添加转换结果
            allure.attach(
                f"转换状态: {status}\n转换结果: {json.dumps(convert_result, indent=2, ensure_ascii=False)}",
                name="测试用例转换结果",
                attachment_type=AttachmentType.TEXT
            )


if __name__ == "__main__":
    # 可以直接运行测试
    pytest.main([
        __file__,
        "-v",
        "--alluredir=./allure-results",
        "--capture=no"
    ])