#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen模型服务类
提供对阿里云Qwen模型的支持
"""

import os
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOpenAI


class QwenService:
    """Qwen模型服务类"""
    
    def __init__(self, api_key: Optional[str] = None, 
                 base_url: Optional[str] = None, 
                 model: Optional[str] = None,
                 temperature: float = 0.7):
        """
        初始化Qwen模型服务
        
        Args:
            api_key: Qwen API密钥，如果未提供则从环境变量获取
            base_url: API基础URL，如果未提供则使用默认值
            model: 模型名称，如果未提供则使用默认值
            temperature: 模型温度，控制输出随机性
        """
        # 从环境变量或参数获取配置
        self.api_key = api_key or os.getenv(
            "QWEN_API_KEY", "sk-27d4a0ea78a84a6f92b02d84521e32c7")
        self.base_url = base_url or os.getenv(
            "ALIYUN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
        self.model = model or os.getenv("QWEN3_MAX", "qwen3-max")
        self.temperature = temperature
        
        # 初始化模型实例
        self.llm = self._init_llm()
    
    def _init_llm(self) -> ChatOpenAI:
        """
        初始化语言模型实例
        
        Returns:
            ChatOpenAI: 配置好的模型实例
        """
        return ChatOpenAI(
            model_name=self.model,
            temperature=self.temperature,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url
        )
    
    def get_llm(self) -> ChatOpenAI:
        """
        获取配置好的模型实例
        
        Returns:
            ChatOpenAI: 语言模型实例
        """
        return self.llm
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取当前服务配置
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model": self.model,
            "temperature": self.temperature
        }