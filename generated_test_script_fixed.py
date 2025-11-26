import requests
import pytest
import allure

@allure.feature("用户登录功能")
@allure.story("正确登录")
class TestUserLogin:
    @allure.title("验证用户使用正确用户名密码登录成功")
    def test_user_login_success(self):
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
        
        with allure.step("验证系统跳转到用户个人中心页面"):
            assert response_data.get("redirect_url") == "/user/profile"
        
        with allure.step("验证页面显示用户的昵称和头像"):
            user_info = response_data.get("user_info", {})
            assert "nickname" in user_info
            assert "avatar" in user_info