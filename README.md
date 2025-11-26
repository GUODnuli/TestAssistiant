# AI驱动的接口自动化测试工具

## 项目简介

本项目是一个基于LangChain和FastAPI的AI驱动接口自动化测试工具，能够将自然语言描述的手工测试用例自动转换为可执行的自动化测试脚本。

## 技术架构

- **后端框架**: FastAPI
- **AI框架**: LangChain
- **大语言模型**: OpenAI GPT
- **测试框架**: pytest

## 功能特性

1. 自然语言测试用例解析
2. 自动化测试脚本生成
3. 批量处理能力
4. RESTful API接口
5. 多LLM提供商支持: 支持OpenAI、Azure OpenAI和自定义API端点

## 快速开始

### 简单三步使用法

1. **配置环境**
   ```bash
   # 安装依赖（任选其一）
   # 方法1：直接安装
   python3 -m pip install -r requirements.txt
   
   # 方法2：使用国内镜像源安装
   python3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
   
   # 方法3：单独安装依赖包
   python3 -m pip install fastapi uvicorn langchain langchain-community langchain-core openai python-dotenv
   
   # 如果遇到网络问题，可以尝试以下解决方案：
   # 1. 检查网络连接是否正常
   # 2. 尝试使用不同的网络环境
   # 3. 配置系统代理（如果适用）
   # 4. 离线安装：预先下载wheel文件，然后使用pip install package_name.whl安装
   
   # 配置环境变量
   cp .env.example .env
   # 编辑 .env 文件，填入你的API密钥(默认支持DeepSeek)
   ```

2. **启动服务**
   ```bash
   python3 main.py
   ```

3. **使用API**
   - 访问 http://localhost:8000/docs 查看API文档
   - 使用 `/api/v1/convert-test-case` 转换单个测试用例
   - 使用 `/api/v1/batch-convert` 批量转换测试用例

## 配置说明

### OpenAI配置
在`.env`文件中设置以下环境变量:
```
MODEL_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，用于自定义API端点
```

### Azure OpenAI配置
在`.env`文件中设置以下环境变量:
```
MODEL_PROVIDER=azure
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
```

### DeepSeek API配置
在`.env`文件中设置以下环境变量:
```
MODEL_PROVIDER=custom
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_API_BASE=https://api.deepseek.com/v1
```

### 其他自定义API端点配置
在`.env`文件中设置以下环境变量:
```
MODEL_PROVIDER=custom
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_custom_api_endpoint
```

### 模型参数配置
```
# 对于DeepSeek API，可选模型包括:
# - deepseek-chat: 通用对话模型
# - deepseek-coder: 代码生成模型
MODEL_NAME=deepseek-chat  # 或其他模型名称
MODEL_TEMPERATURE=0.7     # 控制生成文本的随机性(0-1)
```

### 服务URL配置
```
# 后端服务URL配置
BACKEND_SERVICE_URL=http://localhost:8002  # 后端Python服务地址
```

## API接口

### 转换单个测试用例

```
POST /api/v1/convert-test-case
```

请求示例：
```json
{
  "test_case_description": "发送一个正常的GET请求到用户接口",
  "parser_prompt_template": "可选的解析提示词模板",
  "generator_prompt_template": "可选的生成提示词模板",
  "generation_type": "script或test_cases"
}
```

### 批量转换测试用例

```
POST /api/v1/batch-convert
```

请求示例：
```json
{
  "test_cases": [
    "发送一个正常的GET请求到用户接口",
    "发送一个POST请求创建新用户",
    "发送一个无效的请求方法到用户接口"
  ],
  "parser_prompt_template": "可选的解析提示词模板",
  "generator_prompt_template": "可选的生成提示词模板"
}
```

## 项目结构

```
.
├── main.py                 # 主应用文件
├── config.py               # 配置文件
├── requirements.txt        # 依赖文件
├── .env.example            # 环境变量示例
├── README.md               # 项目说明文件
├── services/               # 服务层
│   ├── langchain_service.py    # LangChain集成服务
│   └── test_case_service.py    # 测试用例转换服务
└── 后端服务实现方案.md          # 后端服务实现方案文档
```

## 后续规划

1. 增加更多测试框架模板支持
2. 实现测试脚本执行和结果验证功能
3. 添加Web界面用于测试用例管理和脚本生成
4. 集成持续集成/持续部署(CI/CD)流程
5. 增强错误处理和日志记录机制