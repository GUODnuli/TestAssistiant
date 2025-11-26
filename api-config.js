// API配置文件
// 统一管理所有服务端点URL，避免硬编码

// 尝试从环境变量获取URL，如果不存在则使用默认值
function getEnvVar(name, defaultValue) {
    // 浏览器环境下无法直接访问环境变量，这里只是定义接口
    // 实际使用时可以通过构建工具注入环境变量
    if (typeof process !== 'undefined' && process.env && process.env[name]) {
        return process.env[name];
    }
    return defaultValue;
}

const ApiConfig = {
    // 后端Python服务地址
    BACKEND_SERVICE_URL: getEnvVar('BACKEND_SERVICE_URL', 'http://localhost:8003'),
    
    // Node.js前端服务地址
    FRONTEND_SERVICE_URL: getEnvVar('FRONTEND_SERVICE_URL', 'http://localhost:8080'),
    
    // Allure测试报告服务地址
    ALLURE_REPORT_URL: getEnvVar('ALLURE_REPORT_URL', 'http://localhost:8080'),
    
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

// 导出配置
if (typeof module !== 'undefined' && module.exports) {
    // Node.js环境
    module.exports = ApiConfig;
} else if (typeof window !== 'undefined') {
    // 浏览器环境
    window.ApiConfig = ApiConfig;
}