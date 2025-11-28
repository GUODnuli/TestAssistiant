"""
健康检查API测试脚本
验证后端服务的可用性
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


class HealthCheckAPI:
    """健康检查API类"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        # 配置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
    
    def check_health(self) -> dict:
        """
        检查服务健康状态
        
        Returns:
            dict: 健康检查响应数据
            
        Raises:
            requests.RequestException: 网络请求异常
            ValueError: JSON解析异常
        """
        health_url = f"{self.base_url}/health"
        
        try:
            logger.info("正在检查服务健康状态")
            response = self.session.get(
                health_url,
                timeout=10
            )
            
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = "健康检查请求超时"
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


class TestHealthAPI:
    """健康检查API测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """获取基础URL"""
        return os.getenv('BASE_URL', 'http://localhost:8003')
    
    @pytest.fixture(scope="class")
    def health_api(self, base_url: str) -> HealthCheckAPI:
        """健康检查API fixture"""
        return HealthCheckAPI(base_url)
    
    @allure.feature("服务健康检查")
    @allure.story("健康状态验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_health_check(self, health_api: HealthCheckAPI):
        """
        测试服务健康检查接口
        
        验证服务是否正常运行
        """
        with allure.step("步骤1: 发送健康检查请求"):
            health_result = health_api.check_health()
            
            # 验证响应包含status字段
            assert 'status' in health_result, "响应中缺少status字段"
            
            status = health_result['status']
            logger.info(f"服务健康状态: {status}")
        
        with allure.step("步骤2: 验证服务处于健康状态"):
            # 验证状态为healthy
            assert status == "healthy", f"服务状态不健康: 期望 'healthy', 实际 '{status}'"
            
            logger.info("服务健康检查通过")
            
            # 在allure报告中添加验证结果
            allure.attach(
                f"服务状态: {status}",
                name="健康检查结果",
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