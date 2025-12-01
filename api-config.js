// API配置文件
// 统一管理所有服务端口号和URL，避免硬编码

// 尝试从环境变量获取配置值，如果不存在则使用默认值
function getEnvVar(name, defaultValue) {
    // 浏览器环境下无法直接访问环境变量，这里只是定义接口
    // 实际使用时可以通过构建工具注入环境变量
    if (typeof process !== 'undefined' && process.env && process.env[name]) {
        return process.env[name];
    }
    return defaultValue;
}

// 从.env文件加载环境变量（Node.js环境）
if (typeof require !== 'undefined' && typeof process !== 'undefined') {
    require('dotenv').config();
}

// 端口号配置
const PORT_CONFIG = {
    // 前端服务端口
    FRONTEND_PORT: parseInt(getEnvVar('FRONTEND_PORT', '8080')),
    
    // 后端服务端口
    BACKEND_PORT: parseInt(getEnvVar('BACKEND_PORT', '8000')),
    
    // Allure报告服务端口
    ALLURE_PORT: parseInt(getEnvVar('ALLURE_PORT', '5000'))
};

// 基础URL配置
const BASE_URLS = {
    // 后端Python服务地址
    BACKEND_BASE_URL: getEnvVar('BACKEND_BASE_URL', 'http://localhost'),
    
    // Node.js前端服务地址
    FRONTEND_BASE_URL: getEnvVar('FRONTEND_BASE_URL', 'http://localhost'),
    
    // HTML测试报告服务地址
    ALLURE_BASE_URL: getEnvVar('ALLURE_BASE_URL', 'http://localhost')
};

const ApiConfig = {
    // 端口号配置
    PORT: PORT_CONFIG,
    
    // 基础URL配置
    BASE_URL: BASE_URLS,
    
    // 完整服务地址
    BACKEND_SERVICE_URL: `${BASE_URLS.BACKEND_BASE_URL}:${PORT_CONFIG.BACKEND_PORT}`,
    FRONTEND_SERVICE_URL: `${BASE_URLS.FRONTEND_BASE_URL}:${PORT_CONFIG.FRONTEND_PORT}`,
    ALLURE_REPORT_URL: `${BASE_URLS.ALLURE_BASE_URL}:${PORT_CONFIG.ALLURE_PORT}`,
    
    // API端点
    API_ENDPOINTS: {
        // Python后端API
        CONVERT_TEST_CASE: '/api/v1/convert-test-case',
        EXECUTE_TEST: '/api/v1/execute-test',
        ANALYZE_RESULTS: '/api/v1/analyze-results',
        
        // Node.js前端API
        PROMPTS: '/api/prompts'
    }
};

// 根据环境判断导出方式
// Node.js环境 - 导出ApiConfig对象
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ApiConfig };
} else if (typeof window !== 'undefined') {
    // 浏览器环境 - 将ApiConfig挂载到全局window对象
    window.ApiConfig = ApiConfig;
}