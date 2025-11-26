// 配置管理JavaScript文件

// 默认配置
const defaultConfig = {
    // 模型配置
    modelProvider: 'custom',
    modelName: 'deepseek-chat',
    modelTemperature: 0.7,
    
    // OpenAI配置
    openaiApiKey: '',
    openaiApiBase: 'https://api.deepseek.com/v1',
    
    // Azure OpenAI配置
    azureOpenaiApiKey: '',
    azureOpenaiEndpoint: '',
    azureOpenaiDeploymentName: ''
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化配置
    loadConfig();
    
    // 绑定事件
    document.getElementById('save-config').addEventListener('click', saveConfig);
    document.getElementById('reset-config').addEventListener('click', resetConfig);
    document.getElementById('back-to-main').addEventListener('click', backToMain);
    
    // 绑定模型提供商切换事件
    document.getElementById('model-provider').addEventListener('change', toggleProviderFields);
});

// 加载配置
function loadConfig() {
    try {
        // 从localStorage加载配置，如果不存在则使用默认配置
        const savedConfig = localStorage.getItem('llmTestConfig');
        const config = savedConfig ? JSON.parse(savedConfig) : defaultConfig;
        
        // 填充表单
        document.getElementById('model-provider').value = config.modelProvider || defaultConfig.modelProvider;
        document.getElementById('model-name').value = config.modelName || defaultConfig.modelName;
        document.getElementById('model-temperature').value = config.modelTemperature || defaultConfig.modelTemperature;
        document.getElementById('openai-api-key').value = config.openaiApiKey || defaultConfig.openaiApiKey;
        document.getElementById('openai-api-base').value = config.openaiApiBase || defaultConfig.openaiApiBase;
        document.getElementById('azure-openai-api-key').value = config.azureOpenaiApiKey || defaultConfig.azureOpenaiApiKey;
        document.getElementById('azure-openai-endpoint').value = config.azureOpenaiEndpoint || defaultConfig.azureOpenaiEndpoint;
        document.getElementById('azure-openai-deployment-name').value = config.azureOpenaiDeploymentName || defaultConfig.azureOpenaiDeploymentName;
        
        // 根据模型提供商显示/隐藏相关字段
        toggleProviderFields();
    } catch (error) {
        console.error('加载配置时出错:', error);
        showNotification('加载配置时出错，请重置配置', 'error');
    }
}

// 保存配置
function saveConfig() {
    try {
        // 获取表单数据
        const config = {
            modelProvider: document.getElementById('model-provider').value,
            modelName: document.getElementById('model-name').value,
            modelTemperature: parseFloat(document.getElementById('model-temperature').value) || defaultConfig.modelTemperature,
            openaiApiKey: document.getElementById('openai-api-key').value,
            openaiApiBase: document.getElementById('openai-api-base').value,
            azureOpenaiApiKey: document.getElementById('azure-openai-api-key').value,
            azureOpenaiEndpoint: document.getElementById('azure-openai-endpoint').value,
            azureOpenaiDeploymentName: document.getElementById('azure-openai-deployment-name').value
        };
        
        // 保存到localStorage
        localStorage.setItem('llmTestConfig', JSON.stringify(config));
        
        // 显示成功消息
        showNotification('配置已保存', 'success');
    } catch (error) {
        console.error('保存配置时出错:', error);
        showNotification('保存配置时出错，请重试', 'error');
    }
}

// 重置配置
function resetConfig() {
    if (confirm('确定要重置所有配置为默认值吗？')) {
        try {
            // 重置表单
            document.getElementById('model-provider').value = defaultConfig.modelProvider;
            document.getElementById('model-name').value = defaultConfig.modelName;
            document.getElementById('model-temperature').value = defaultConfig.modelTemperature;
            document.getElementById('openai-api-key').value = defaultConfig.openaiApiKey;
            document.getElementById('openai-api-base').value = defaultConfig.openaiApiBase;
            document.getElementById('azure-openai-api-key').value = defaultConfig.azureOpenaiApiKey;
            document.getElementById('azure-openai-endpoint').value = defaultConfig.azureOpenaiEndpoint;
            document.getElementById('azure-openai-deployment-name').value = defaultConfig.azureOpenaiDeploymentName;
            
            // 删除localStorage中的配置
            localStorage.removeItem('llmTestConfig');
            
            // 显示成功消息
            showNotification('配置已重置为默认值', 'success');
            
            // 根据模型提供商显示/隐藏相关字段
            toggleProviderFields();
        } catch (error) {
            console.error('重置配置时出错:', error);
            showNotification('重置配置时出错，请重试', 'error');
        }
    }
}

// 根据模型提供商显示/隐藏相关字段
function toggleProviderFields() {
    const provider = document.getElementById('model-provider').value;
    
    // 根据选择的提供商显示相应的配置字段
    if (provider === 'openai') {
        document.getElementById('openai-api-key').closest('.form-group').style.display = 'block';
        document.getElementById('openai-api-base').closest('.form-group').style.display = 'block';
        document.getElementById('azure-openai-api-key').closest('.form-group').style.display = 'none';
        document.getElementById('azure-openai-endpoint').closest('.form-group').style.display = 'none';
        document.getElementById('azure-openai-deployment-name').closest('.form-group').style.display = 'none';
    } else if (provider === 'azure') {
        document.getElementById('openai-api-key').closest('.form-group').style.display = 'none';
        document.getElementById('openai-api-base').closest('.form-group').style.display = 'none';
        document.getElementById('azure-openai-api-key').closest('.form-group').style.display = 'block';
        document.getElementById('azure-openai-endpoint').closest('.form-group').style.display = 'block';
        document.getElementById('azure-openai-deployment-name').closest('.form-group').style.display = 'block';
    } else {
        // custom provider
        document.getElementById('openai-api-key').closest('.form-group').style.display = 'block';
        document.getElementById('openai-api-base').closest('.form-group').style.display = 'block';
        document.getElementById('azure-openai-api-key').closest('.form-group').style.display = 'none';
        document.getElementById('azure-openai-endpoint').closest('.form-group').style.display = 'none';
        document.getElementById('azure-openai-deployment-name').closest('.form-group').style.display = 'none';
    }
}

// 显示通知消息
function showNotification(message, type) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = 'notification ' + type;
    notification.style.display = 'block';
    
    // 3秒后自动隐藏
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// 返回主页面
function backToMain() {
    window.location.href = 'index.html';
}