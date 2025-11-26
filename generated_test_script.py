import requests
import pytest
import allure

@allure.feature("用户登录功能")
@allure.story("正确登录")
class TestUserLogin:
    @allure.title("验证用户使用正确用户名密码登录成功")
    def test_user_login_success(self):
        with allure.step("准备登录请求数据"):
            url = "https://mall.shanrongmall.com/api/login"
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
        
        with allure.step("发送POST登录请求"):
            response = requests.post(url, json=login_data)
            response.encoding = "utf-8"
        
        with allure.step("验证登录响应状态码为200"):
            assert response.status_code == 200
        
        with allure.step("验证登录响应包含成功状态"):
            response_data = response.json()
            assert response_data["code"] == 200
            assert response_data["message"] == "登录成功"
        
        with allure.step("获取用户个人中心信息"):
            user_center_url = "https://mall.shanrongmall.com/api/user/profile"
            headers = {"Authorization": f"Bearer {response_data['data']['token']}"}
            user_response = requests.get(user_center_url, headers=headers)
            user_response.encoding = "utf-8"
        
        with allure.step("验证个人中心页面加载成功"):
            assert user_response.status_code == 200
        
        with allure.step("验证页面显示用户昵称和头像"):
            user_data = user_response.json()
            assert "nickname" in user_data["data"]
            assert "avatar" in user_data["data"]
            assert user_data["data"]["nickname"] is not None
            assert user_data["data"]["avatar"] is not None
