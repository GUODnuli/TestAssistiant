# 提示词配置管理说明

## 概述
本项目实现了提示词的配置化管理，将所有提示词模板集中存储在独立的配置文件中，便于后续的修改与维护。

## 配置文件
- `prompts_config.json`：存储所有提示词模板的JSON文件

## 配置结构
```json
{
  "prompt_key": {
    "name": "提示词名称",
    "description": "提示词描述",
    "template": "提示词模板内容",
    "variables": ["变量1", "变量2"],
    "role": "AI角色定义",
    "tech_stack": "技术栈要求"
  }
}
```

## 使用方法
1. 修改`prompts_config.json`文件中的相应提示词模板
2. 重启应用服务使配置生效
3. 系统将自动加载新的提示词模板

## 提示词模板列表
1. `script_generator`：脚本生成提示词模板
2. `test_case_generator`：测试案例生成提示词模板
3. `ai_analysis`：AI分析提示词模板

## 模板变量说明

### test_case_generator 模板
- **变量名**：`business_rules`（更新于2023-10-30，原变量名为`test_case`）
- **用途**：接收业务规则文档输入，用于生成相应的测试用例

### script_generator 模板
- **变量名**：根据实际使用场景定义

### ai_analysis 模板
- **变量名**：根据实际使用场景定义