"""
用户登录功能自动化测试脚本
使用Page Object模式组织，支持数据驱动测试
"""

import os
import json
import logging
import pytest
import requests
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import allure
from allure_commons.types import AttachmentType

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestData:
    """测试数据类"""
    username: str
    password: str
    expected_nickname: str
    expected_avatar_url: str


class LoginPage:
    """登录页面对象类"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        # 配置请求头
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json'
        })
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        执行登录操作
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Dict: 登录响应数据
            
        Raises:
            requests.RequestException: 网络请求异常
            ValueError: JSON解析异常
        """
        login_url = f"{self.base_url}/api/login"
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            with allure.step("发送登录请求"):
                logger.info(f"正在登录用户: {username}")
                response = self.session.post(
                    login_url, 
                    json=login_data,
                    timeout=10
                )
                
                # 记录请求和响应详情到allure报告
                allure.attach(
                    f"请求URL: {login_url}\n请求数据: {json.dumps(login_data, indent=2)}",
                    name="登录请求详情",
                    attachment_type=AttachmentType.TEXT
                )
                
            # 检查HTTP状态码
            response.raise_for_status()
            
            # 解析JSON响应
            result = response.json()
            
            with allure.step("验证登录响应"):
                allure.attach(
                    f"响应状态码: {response.status_code}\n响应数据: {json.dumps(result, indent=2)}",
                    name="登录响应详情",
                    attachment_type=AttachmentType.TEXT
                )
            
            return result
            
        except requests.exceptions.Timeout:
            error_msg = "登录请求超时"
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
    
    def get_user_profile(self, token: str) -> Dict[str, Any]:
        """
        获取用户个人信息
        
        Args:
            token: 认证令牌
            
        Returns:
            Dict: 用户个人信息
        """
        profile_url = f"{self.base_url}/api/user/profile"
        
        headers = {'Authorization': f'Bearer {token}'}
        
        try:
            with allure.step("获取用户个人信息"):
                logger.info("正在获取用户个人信息")
                response = self.session.get(
                    profile_url,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                profile_data = response.json()
                
                allure.attach(
                    f"响应数据: {json.dumps(profile_data, indent=2)}",
                    name="用户个人信息",
                    attachment_type=AttachmentType.TEXT
                )
                
                return profile_data
                
        except requests.RequestException as e:
            error_msg = f"获取用户信息失败: {str(e)}"
            logger.error(error_msg)
            raise
    
    def logout(self):
        """退出登录"""
        self.session.close()


class TestUserLogin:
    """用户登录测试类"""
    
    @pytest.fixture(scope="class")
    def base_url(self) -> str:
        """获取基础URL"""
        return os.getenv('BASE_URL', 'https://api.example.com')
    
    @pytest.fixture(scope="class")
    def login_page(self, base_url: str) -> LoginPage:
        """登录页面fixture"""
        page = LoginPage(base_url)
        yield page
        page.logout()
    
    @pytest.fixture
    def test_data(self) -> TestData:
        """测试数据fixture"""
        # 从环境变量获取敏感信息
        username = os.getenv('TEST_USERNAME')
        password = os.getenv('TEST_PASSWORD')
        
        if not username or not password:
            pytest.skip("未设置测试用户名或密码环境变量")
        
        return TestData(
            username=username,
            password=password,
            expected_nickname="测试用户",
            expected_avatar_url="https://example.com/avatar.jpg"
        )
    
    @pytest.fixture
    def load_test_cases(self) -> list:
        """
        从外部文件加载测试用例数据
        支持JSON格式的测试数据文件
        """
        test_cases_file = "test_data/login_test_cases.json"
        test_cases = []
        
        try:
            if os.path.exists(test_cases_file):
                with open(test_cases_file, 'r', encoding='utf-8') as f:
                    test_cases = json.load(f)
            else:
                # 如果没有外部文件，使用默认测试数据
                test_cases = [
                    {
                        "username": os.getenv('TEST_USERNAME'),
                        "password": os.getenv('TEST_PASSWORD'),
                        "expected_nickname": "测试用户",
                        "expected_avatar_url": "https://example.com/avatar.jpg",
                        "should_succeed": True
                    }
                ]
                logger.warning(f"未找到测试数据文件 {test_cases_file}，使用默认测试数据")
                
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载测试数据文件失败: {str(e)}")
            pytest.skip(f"无法加载测试数据: {str(e)}")
        
        return test_cases
    
    @allure.feature("用户登录")
    @allure.story("用户登录功能验证")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_successful_login(self, login_page: LoginPage, test_data: TestData):
        """
        测试成功登录场景
        
        测试步骤:
        1. 输入正确的用户名和密码
        2. 验证登录成功
        3. 验证跳转到个人中心页面
        4. 验证显示用户昵称和头像
        """
        with allure.step("步骤1: 输入正确的用户名和密码进行登录"):
            login_result = login_page.login(
                test_data.username, 
                test_data.password
            )
            
            # 验证登录成功
            assert login_result.get('success') is True, "登录失败"
            assert 'token' in login_result, "响应中缺少认证令牌"
            
            token = login_result['token']
            logger.info("登录成功，获取到认证令牌")
        
        with allure.step("步骤2: 验证系统跳转到用户个人中心页面"):
            # 在实际项目中，这里可能需要验证重定向或页面URL
            # 这里我们假设登录成功后可以获取用户信息
            user_profile = login_page.get_user_profile(token)
            
            assert user_profile is not None, "无法获取用户个人信息"
            logger.info("成功跳转到用户个人中心页面")
        
        with allure.step("步骤3: 验证页面显示用户的昵称和头像"):
            actual_nickname = user_profile.get('nickname')
            actual_avatar_url = user_profile.get('avatar_url')
            
            # 验证昵称
            assert actual_nickname == test_data.expected_nickname, \
                f"昵称不匹配: 期望 {test_data.expected_nickname}, 实际 {actual_nickname}"
            
            # 验证头像URL
            assert actual_avatar_url == test_data.expected_avatar_url, \
                f"头像URL不匹配: 期望 {test_data.expected_avatar_url}, 实际 {actual_avatar_url}"
            
            logger.info(f"用户昵称验证成功: {actual_nickname}")
            logger.info(f"用户头像URL验证成功: {actual_avatar_url}")
            
            # 在allure报告中添加验证结果截图
            allure.attach(
                f"昵称: {actual_nickname}\n头像URL: {actual_avatar_url}",
                name="用户信息验证结果",
                attachment_type=AttachmentType.TEXT
            )
    
    @allure.feature("用户登录")
    @allure.story("数据驱动登录测试")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("test_case", [
        {
            "username": "valid_user",
            "password": "valid_password", 
            "expected_nickname": "测试用户",
            "should_succeed": True
        }
    ])
    def test_login_data_driven(self, login_page: LoginPage, test_case: Dict[str, Any]):
        """
        数据驱动登录测试
        
        使用@pytest.mark.parametrize实现数据驱动测试
        支持多种测试场景
        """
        username = test_case.get('username')
        password = test_case.get('password')
        should_succeed = test_case.get('should_succeed', True)
        
        with allure.step(f"数据驱动测试 - 用户名: {username}"):
            try:
                login_result = login_page.login(username, password)
                
                if should_succeed:
                    assert login_result.get('success') is True, "预期登录成功但实际失败"
                    assert 'token' in login_result, "响应中缺少认证令牌"
                    logger.info(f"用户 {username} 登录成功")
                else:
                    assert login_result.get('success') is False, "预期登录失败但实际成功"
                    logger.info(f"用户 {username} 登录失败（符合预期）")
                    
            except requests.RequestException as e:
                if should_succeed:
                    pytest.fail(f"预期登录成功但发生请求异常: {str(e)}")
                else:
                    logger.info(f"请求异常（符合预期）: {str(e)}")
    
    @allure.feature("用户登录")
    @allure.story("登录异常场景测试")
    @allure.severity(allure.severity_level.NORMAL)
    def test_login_exception_handling(self, login_page: LoginPage):
        """
        测试登录异常处理
        
        验证脚本能够正确处理各种异常情况
        """
        # 测试无效URL
        invalid_page = LoginPage("http://invalid-url-that-does-not-exist")
        
        with allure.step("测试网络连接异常"):
            with pytest.raises(requests.RequestException):
                invalid_page.login("test", "test")
        
        # 测试无效JSON响应（需要模拟服务端返回无效JSON的场景）
        # 这里只是演示异常处理结构


if __name__ == "__main__":
    # 可以直接运行测试
    pytest.main([
        __file__,
        "-v",
        "--alluredir=./allure-results",
        "--capture=no"
    ])