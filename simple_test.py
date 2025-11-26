import json

# 直接读取配置文件来验证更新
with open('config/prompts_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 输出更新后的提示词模板相关信息
print("=== 验证提示词模板更新 ===")
print(f"模板名称: {config['script_generator']['name']}")
print(f"模板描述: {config['script_generator']['description']}")
print(f"模板变量: {config['script_generator']['variables']}")
print(f"角色: {config['script_generator']['role']}")
print(f"技术栈: {config['script_generator']['tech_stack']}")

# 验证变量名是否已更新为factor_combinations
if 'factor_combinations' in config['script_generator']['variables']:
    print("✅ 验证成功: 变量名已更新为factor_combinations")
else:
    print("❌ 验证失败: 变量名未更新")

# 验证提示词中是否包含factor_combinations占位符
if '{factor_combinations}' in config['script_generator']['template']:
    print("✅ 验证成功: 提示词模板中包含factor_combinations占位符")
else:
    print("❌ 验证失败: 提示词模板中未包含factor_combinations占位符")