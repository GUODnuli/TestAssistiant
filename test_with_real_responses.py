import requests
import pytest
import allure
import json

@allure.feature("用户登录功能")
@allure.story("正确登录")
class TestUserLogin:
    @allure.title("验证用户使用正确用户名密码登录成功")
    def test_user_login_success(self):
        with allure.step("准备登录请求数据"):
            # 使用一个真实的测试API端点（httpbin.org是一个HTTP请求&响应服务）
            url = "https://httpbin.org/post"
            login_data = {
                "username": "test_user",
                "password": "test_password"
            }
        
        with allure.step("发送POST登录请求"):
            response = requests.post(url, json=login_data)
            response.encoding = "utf-8"
            
            # 记录请求详细信息
            allure.attach(json.dumps(login_data, ensure_ascii=False, indent=2), 
                         "请求体", allure.attachment_type.JSON)
            
            # 记录完整的响应信息
            allure.attach(str(response.status_code), "响应状态码", allure.attachment_type.TEXT)
            allure.attach(json.dumps(dict(response.headers), ensure_ascii=False, indent=2), 
                         "响应头", allure.attachment_type.JSON)
            allure.attach(response.text, "响应体", allure.attachment_type.JSON)
        
        with allure.step("验证登录响应状态码为200"):
            assert response.status_code == 200
        
        with allure.step("验证响应内容包含请求数据"):
            response_data = response.json()
            assert "json" in response_data
            assert response_data["json"]["username"] == "test_user"
        
        with allure.step("验证跳转到个人中心页面"):
            # 使用httpbin.org的GET端点模拟个人中心请求
            profile_url = "https://httpbin.org/get"
            profile_params = {"user_id": "12345"}
            profile_response = requests.get(profile_url, params=profile_params)
            profile_response.encoding = "utf-8"
            
            # 记录个人中心请求的响应信息
            allure.attach(json.dumps(profile_params, ensure_ascii=False, indent=2), 
                         "个人中心请求参数", allure.attachment_type.JSON)
            allure.attach(str(profile_response.status_code), "个人中心响应状态码", allure.attachment_type.TEXT)
            allure.attach(json.dumps(dict(profile_response.headers), ensure_ascii=False, indent=2), 
                         "个人中心响应头", allure.attachment_type.JSON)
            allure.attach(profile_response.text, "个人中心响应体", allure.attachment_type.JSON)
            
            assert profile_response.status_code == 200
        
        with allure.step("验证页面显示用户信息"):
            profile_data = profile_response.json()
            assert "args" in profile_data
            assert "user_id" in profile_data["args"]