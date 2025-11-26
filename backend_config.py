#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
后端配置文件，用于管理所有API端点和服务URL
"""

import os
from config import Config

class BackendConfig:
    """后端服务配置类"""
    
    # 服务基础URL，从环境变量中读取，默认为http://localhost:8002
    BASE_URL = Config.BACKEND_SERVICE_URL
    
    # API端点路径
    API_ENDPOINTS = {
        "CONVERT_TEST_CASE": "/api/v1/convert-test-case",
        "BATCH_CONVERT": "/api/v1/batch-convert",
        "EXECUTE_TEST": "/api/v1/execute-test",
        "ANALYZE_RESULTS": "/api/v1/analyze-results",
        "HEALTH_CHECK": "/health"
    }
    
    # 获取完整API URL的方法
    @classmethod
    def get_api_url(cls, endpoint_key):
        """
        根据端点键名获取完整的API URL
        
        Args:
            endpoint_key (str): API端点键名
            
        Returns:
            str: 完整的API URL
        """
        if endpoint_key in cls.API_ENDPOINTS:
            return f"{cls.BASE_URL}{cls.API_ENDPOINTS[endpoint_key]}"
        else:
            raise ValueError(f"Unknown endpoint key: {endpoint_key}")