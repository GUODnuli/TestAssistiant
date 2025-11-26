import requests
import pytest
import allure
from unittest.mock import patch, Mock

@allure.feature("用户登录功能")
@allure.story("正确登录")
class TestUserLogin:
    @allure.title("验证用户使用正确用户名密码登录成功")
    @patch('requests.post')
    @patch('requests.get')
    def test_user_login_success(self, mock_get, mock_post):
        # Mock 登录响应
        mock_login_response = Mock()
        mock_login_response.status_code = 200
        mock_login_response.json.return_value = {"user_id": "12345"}
        mock_post.return_value = mock_login_response
        
        # Mock 个人中心响应
        mock_profile_response = Mock()
        mock_profile_response.status_code = 200
        mock_profile_response.json.return_value = {"nickname": "测试用户", "avatar": "avatar_url"}
        mock_get.return_value = mock_profile_response
        
        with allure.step("准备登录请求数据"):
            url = "https://api.example.com/login"
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
        
        with allure.step("发送POST登录请求"):
            response = requests.post(url, json=login_data)
            response.encoding = "utf-8"
        
        with allure.step("验证登录响应状态码为200"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容包含用户信息"):
            response_data = response.json()
            assert "user_id" in response_data
        
        with allure.step("验证跳转到个人中心页面"):
            profile_url = "https://api.example.com/user/profile"
            profile_response = requests.get(profile_url)
            profile_response.encoding = "utf-8"
            assert profile_response.status_code == 200
        
        with allure.step("验证页面显示用户昵称和头像"):
            profile_data = profile_response.json()
            assert "nickname" in profile_data
            assert "avatar" in profile_data