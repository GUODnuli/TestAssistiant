const express = require('express');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 8080;

// 启用CORS
app.use(cors());

// 解析JSON请求体
app.use(express.json());

// 提供静态文件
app.use(express.static('.'));

// 获取提示词数据的API端点
app.get('/api/prompts', (req, res) => {
  try {
    const promptsConfigPath = path.join(__dirname, 'config', 'prompts_config.json');
    const promptsData = JSON.parse(fs.readFileSync(promptsConfigPath, 'utf8'));
    
    // 定义每个提示词模板的功能和用途说明
    const promptFunctions = {
      "test_case_generator": {
        "function": "AI生成测试要点",
        "purpose": "根据业务规则文档自动生成详细的文TestCase，覆盖各种正常和异常场景"
      },
      "script_generator": {
        "function": "AI生成测试脚本",
        "purpose": "将文本案例转换为可执行的Python自动化测试脚本，集成pytest和requests库"
      },
      "ai_analysis": {
        "function": "AI分析测试结果",
        "purpose": "对测试执行结果进行智能分析并生成结构化的分析报告，提供改进建议"
      }
    };
    
    // 转换数据格式以便前端展示，按照指定顺序排列
    const orderedKeys = ['test_case_generator', 'script_generator', 'ai_analysis'];
    const promptList = orderedKeys.map(key => {
      const prompt = promptsData[key];
      const funcInfo = promptFunctions[key] || {};
      return {
        id: key,
        name: prompt.name,
        description: prompt.description,
        template: prompt.template,
        role: prompt.role,
        techStack: prompt.tech_stack,
        variables: prompt.variables || [],
        function: funcInfo.function || "",
        purpose: funcInfo.purpose || ""
      };
    });
    
    res.json({ prompts: promptList });
  } catch (error) {
    console.error('Error reading prompts config:', error);
    res.status(500).json({ error: 'Failed to load prompts data' });
  }
});

// 处理所有其他路由，返回index.html
app.get(/^(?!\/api).*/, (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});