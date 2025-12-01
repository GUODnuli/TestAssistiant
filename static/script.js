// DOM元素获取
// Script version: 1.3
// 引入API配置文件
/// #if BROWSER
// 在浏览器环境中引入配置文件
/// #endif
const businessRulesInput = document.getElementById('business-rules-input');
const businessRulesFile = document.getElementById('business-rules-file');
const generateFromRulesBtn = document.getElementById('generate-from-rules-btn');
const generatedTestCases = document.getElementById('generated-test-cases');
const testCasesContent = document.getElementById('test-cases-content');
const useTestCasesBtn = document.getElementById('use-test-cases-btn');
const testCaseInput = document.getElementById('test-case-input');
const generateBtn = document.getElementById('generate-btn');
const scriptDisplaySection = document.getElementById('script-display-section');
const generatedScript = document.getElementById('generated-script');
const copyBtn = document.getElementById('copy-btn');
const executeBtn = document.getElementById('execute-btn');
const executionOutput = document.getElementById('execution-output');
const executionLog = document.getElementById('execution-log');
const responseSection = document.getElementById('response-section');
const responseContent = document.getElementById('response-content');
const aiAnalysisBtn = document.getElementById('ai-analysis-btn');
const aiAnalysisSection = document.getElementById('ai-analysis-section');
const aiAnalysisContent = document.getElementById('ai-analysis-content');
const viewReportBtn = document.getElementById('view-report-btn');
const reportContainer = document.getElementById('report-container');
const testReportFrame = document.getElementById('allure-report-frame');

// 生成自动化测试脚本的函数
async function generateTestScript(testCase) {
    try {
        // 构建请求体（不包含自定义提示词模板）
        const requestBody = {
            test_case_description: testCase,
            generation_type: "test_data"  // 添加test_data参数
        };

        const response = await fetch(`${ApiConfig.BACKEND_SERVICE_URL}${ApiConfig.API_ENDPOINTS.CONVERT_TEST_CASE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || '生成脚本时发生错误，请重试');
        }

        const data = await response.json();
        // 返回测试数据或脚本内容
        return data.generated_test_data || data.generated_script || null;
    } catch (error) {
        console.error('生成脚本时出错:', error);
        throw new Error(`生成脚本时发生错误: ${error.message}`);
    }
}

// 执行测试脚本的函数
async function executeTestScript(script) {
    try {
        const response = await fetch(`${ApiConfig.BACKEND_SERVICE_URL}${ApiConfig.API_ENDPOINTS.EXECUTE_TEST}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                script_content: script
            })
        });
        
        // 检查响应的内容类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            // 如果响应不是JSON格式，读取文本内容查看错误详情
            const errorText = await response.text();
            throw new Error(`服务器返回非JSON响应: ${errorText.substring(0, 200)}...`);
        }
        
        if (!response.ok) {
            try {
                const errorData = await response.json();
                throw new Error(errorData.detail || '执行脚本时发生错误');
            } catch (jsonError) {
                // 如果错误响应也不是JSON格式
                if (jsonError instanceof SyntaxError) {
                    const errorText = await response.text();
                    throw new Error(`服务器返回错误: ${errorText.substring(0, 200)}...`);
                }
                throw jsonError;
            }
        }
        
        const data = await response.json();
        
        // 存储报告路径到按钮的dataset中
        if (data.report_path) {
            viewReportBtn.dataset.reportPath = data.report_path;
            console.log('存储报告路径:', data.report_path);
        }
        
        // 获取report.html文件内容
        let reportHtmlContent = null;
        if (data.report_path) {
            try {
                // 构建报告文件的URL路径
                // 假设报告文件存储在后端，可以通过API获取
                const reportResponse = await fetch(`${ApiConfig.BACKEND_SERVICE_URL}/get-report?path=${encodeURIComponent(data.report_path)}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'text/html'
                    }
                });
                
                if (reportResponse.ok) {
                    reportHtmlContent = await reportResponse.text();
                    console.log('成功获取报告HTML内容');
                } else {
                    console.warn('无法获取报告HTML内容，状态码:', reportResponse.status);
                }
            } catch (reportError) {
                console.error('获取报告HTML内容时出错:', reportError);
            }
        }
        
        // 构造响应报文
        const responsePayload = {
            status: data.success ? "success" : "failure",
            data: {
                success: data.success,
                output: data.output,
                error: data.error,
                report_path: data.report_path,
                report_html: reportHtmlContent // 添加报告HTML内容到响应中
            },
            timestamp: new Date().toISOString()
        };
        
        return {
            result: data.output,
            response: JSON.stringify(responsePayload, null, 2),
            reportPath: data.report_path,
            reportHtml: reportHtmlContent // 返回报告HTML内容
        };
    } catch (error) {
        console.error('执行脚本时出错:', error);
        throw new Error(`执行脚本时发生错误: ${error.message}`);
    }
}

// 复制脚本到剪贴板的函数
function copyToClipboard() {
    const textArea = document.createElement('textarea');
    textArea.value = generatedScript.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    // 显示复制成功的提示
    const originalText = copyBtn.textContent;
    copyBtn.textContent = '已复制!';
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
}

// AI结果分析函数
async function analyzeTestResults(testCase, responsePayload) {
    try {
        // 解析响应数据
        const data = typeof responsePayload === 'string' ? JSON.parse(responsePayload) : responsePayload;
        
        // 准备发送到后端的数据
        const requestData = {
            test_case: testCase,
            execution_result: {
                success: data.data?.success,
                output: data.data?.output || '',
                error: data.data?.error || ''
            }
        };
        
        // 调用后端AI分析API
        // 使用完整的后端服务器地址而不是相对路径
        const response = await fetch(`${ApiConfig.BACKEND_SERVICE_URL}${ApiConfig.API_ENDPOINTS.ANALYZE_RESULTS}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        // 检查响应状态
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // 检查响应内容类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Received non-JSON response:', text);
            throw new Error('服务器返回了意外的响应格式');
        }
        
        const result = await response.json();
        
        if (result.success) {
            // 显示AI分析结果
            // 将Markdown格式转换为HTML格式显示
            let formattedAnalysis = result.analysis
                .replace(/## (.*?)(\n|$)/g, '<h2>$1</h2>')
                .replace(/### (.*?)(\n|$)/g, '<h3>$1</h3>')
                .replace(/\n\n/g, '<br><br>')
                .replace(/\n/g, '<br>')
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/- (.*?)(<br>|$)/g, '<li>$1</li>')
                .replace(/(<li>.*<\/li>)/g, '<ul>$1</ul>');
            
            aiAnalysisContent.innerHTML = formattedAnalysis;
            aiAnalysisSection.style.display = 'block';
        } else {
            throw new Error(result.error || 'AI分析失败');
        }
    } catch (err) {
        console.error('AI结果分析时出错:', err);
        // 显示简单的错误信息
        let errorMessage = '无法分析测试结果，请查看应答报文获取详细信息。';
        if (err.message.includes('Unexpected token')) {
            errorMessage = '服务器返回了意外的响应格式，请稍后重试或联系管理员。';
        } else if (err.message.includes('HTTP error')) {
            errorMessage = `服务器错误: ${err.message}`;
        } else if (err.message.includes('Failed to fetch') || err.name === 'TypeError') {
            errorMessage = '无法连接到后端服务器，请确保后端服务正在运行并且CORS设置正确。';
        }
        
        aiAnalysisContent.innerHTML = errorMessage;
        aiAnalysisSection.style.display = 'block';
    }
}

// 显示加载状态的函数
function showLoadingState(element, isLoading) {
    if (element && isLoading) {
        // 显示加载状态
        element.disabled = true;
        element.textContent = '生成中...';
        element.classList.add('loading');
    } else if (element && !isLoading) {
        // 隐藏加载状态
        element.disabled = false;
        element.textContent = '生成自动化测试脚本';
        element.classList.remove('loading');
    }
}

// 为第一个区域的生成按钮专门创建的加载状态函数
function showMainLoadingState() {
    generateBtn.disabled = true;
    generateBtn.textContent = '生成中...';
    generateBtn.classList.add('loading');
}

// 隐藏第一个区域加载状态的函数
function hideMainLoadingState() {
    generateBtn.disabled = false;
    generateBtn.textContent = '生成自动化测试脚本';
    generateBtn.classList.remove('loading');
}

// 显示错误信息的函数
function showError(message) {
    // 创建错误提示元素
    const errorElement = document.createElement('div');
    errorElement.className = 'error-message';
    errorElement.textContent = message;
    errorElement.style.cssText = `
        color: #e74c3c;
        background-color: #fdf2f2;
        border: 1px solid #f5b7b1;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-weight: 500;
    `;
    
    // 插入到输入区域后面
    testCaseInput.parentNode.insertBefore(errorElement, testCaseInput.nextSibling);
    
    // 3秒后自动移除错误提示
    setTimeout(() => {
        if (errorElement.parentNode) {
            errorElement.parentNode.removeChild(errorElement);
        }
    }, 3000);
}

// 生成按钮点击事件处理
generateBtn.addEventListener('click', async () => {
    const testCase = testCaseInput.value.trim();
    
    if (!testCase) {
        showError('请输入文本案例');
        testCaseInput.focus();
        return;
    }
    
    // 显示加载状态
    showMainLoadingState();
    
    try {
        // 生成自动化测试脚本
        const script = await generateTestScript(testCase);
        
        // 显示生成的脚本或测试数据信息
        generatedScript.textContent = script || '测试数据已成功生成到demo/testcases目录';
        scriptDisplaySection.style.display = 'block';
        
        // 显示执行按钮
        executeBtn.style.display = 'inline-block';
        
        // 滚动到脚本显示区域
        scriptDisplaySection.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('生成脚本时出错:', error);
        showError(error.message || '生成脚本时出错，请重试');
    } finally {
        // 恢复按钮状态
        hideMainLoadingState();
    }
});

// 检查并添加事件监听器
if (generateFromRulesBtn) {
    console.log('Adding event listener to generateFromRulesBtn');
    generateFromRulesBtn.addEventListener('click', async () => {
        console.log('Generate button clicked');
        // 检查业务规则输入是否为空
        const businessRules = businessRulesInput?.value.trim();
        
        if (!businessRules) {
            showError('请输入业务规则文档内容');
            businessRulesInput?.focus();
            return;
        }
        
        try {
            console.log('Generating test points from rules...');
            // 生成测试要点（加载状态在函数内部处理）
            const testCases = await generateTestPointsFromRules(businessRules);
            
            // 显示生成的测试要点
            if (testCasesContent) {
                testCasesContent.textContent = testCases;
            }
            
            if (generatedTestCases) {
                generatedTestCases.style.display = 'block';
                generatedTestCases.scrollIntoView({ behavior: 'smooth' });
            }
            
            // 显示使用按钮
            if (useTestCasesBtn) {
                useTestCasesBtn.style.display = 'inline-block';
            }
        } catch (error) {
            console.error('生成测试要点时出错:', error);
            showError(error.message || '生成测试要点时出错，请重试');
        }
        // 注意：加载状态在generateTestPointsFromRules函数内部处理，无需在此处处理
    });
} else {
    console.error('generateFromRulesBtn not found in the DOM');
}

// 使用生成的测试要点按钮点击事件处理
useTestCasesBtn.addEventListener('click', () => {
    const testCases = testCasesContent.textContent;
    if (testCases && testCases !== '生成失败: 未生成有效的测试要点') {
        testCaseInput.value = testCases;
        // 滚动到第一个区域
        document.querySelector('.region-1').scrollIntoView({ behavior: 'smooth' });
    } else {
        alert('没有可使用的测试要点');
    }
});

// 执行按钮点击事件处理
executeBtn.addEventListener('click', async () => {
    const script = generatedScript.textContent;
    const testCase = testCaseInput.value.trim();
    
    if (!script) {
        showError('请先生成自动化测试脚本');
        return;
    }
    
    // 显示加载状态
    executeBtn.classList.add('loading');
    executeBtn.textContent = '执行中...';
    
    // 清除之前的样式类
    executionOutput.classList.remove('success', 'error');
    executionLog.classList.remove('success', 'error');
    
    try {
        // 执行自动化测试脚本
        const data = await executeTestScript(script);
        
        // 显示执行结果
        executionLog.textContent = data.result;
        executionOutput.style.display = 'block';
        
        // 如果有报告HTML内容，嵌入到execution-output div中
        if (data.reportHtml) {
            // 创建一个新的div来容纳报告内容
            const reportDiv = document.createElement('div');
            reportDiv.className = 'embedded-report';
            reportDiv.innerHTML = data.reportHtml;
            
            // 确保移除可能导致问题的脚本
            const scripts = reportDiv.querySelectorAll('script');
            scripts.forEach(script => script.remove());
            
            // 找到execution-log元素后的位置插入报告
            const executionLogElement = executionOutput.querySelector('#execution-log');
            if (executionLogElement) {
                // 检查是否已有报告div，如果有则移除
                const existingReport = executionOutput.querySelector('.embedded-report');
                if (existingReport) {
                    executionOutput.removeChild(existingReport);
                }
                
                // 插入新的报告div
                executionOutput.appendChild(reportDiv);
                console.log('测试报告已成功嵌入到执行结果区域');
            }
        } else {
            // 如果没有报告HTML内容，确保移除可能存在的报告div
            const existingReport = executionOutput.querySelector('.embedded-report');
            if (existingReport) {
                executionOutput.removeChild(existingReport);
            }
        }
        
        // 显示应答报文
        responseContent.textContent = data.response;
        responseSection.style.display = 'block';
        
        // 根据执行结果添加样式类
        if (data.result.includes("FAILED") || data.result.includes("ERROR")) {
            executionOutput.classList.add('error');
            executionLog.classList.add('error');
        } else {
            executionOutput.classList.add('success');
            executionLog.classList.add('success');
        }
        
        // 显示AI分析按钮
        aiAnalysisBtn.style.display = 'inline-block';
        // 隐藏之前的AI分析结果
        aiAnalysisSection.style.display = 'none';
        
        // 存储执行结果供AI分析使用
        executeBtn.dataset.testCase = testCase;
        executeBtn.dataset.response = data.response;
        
        // 滚动到执行结果区域
        executionOutput.scrollIntoView({ behavior: 'smooth' });
        
        // 显示查看报告按钮
        viewReportBtn.style.display = 'inline-block';
        viewReportBtn.dataset.timestamp = Date.now();
    } catch (error) {
        console.error('执行脚本时出错:', error);
        executionLog.textContent = error.message || '执行脚本时出错，请重试';
        executionOutput.style.display = 'block';
        
        // 隐藏应答报文区域（出错时不需要显示）
        responseSection.style.display = 'none';
        
        // 添加错误样式类
        executionOutput.classList.add('error');
        executionLog.classList.add('error');
        
        // 隐藏AI分析按钮（出错时不需要分析）
        aiAnalysisBtn.style.display = 'none';
        
        executionOutput.scrollIntoView({ behavior: 'smooth' });
    } finally {
        // 恢复按钮状态
        executeBtn.classList.remove('loading');
        executeBtn.textContent = '执行自动化测试脚本';
    }
});

// 查看测试报告按钮点击事件
viewReportBtn.addEventListener('click', async () => {
    // 显示加载状态
    viewReportBtn.disabled = true;
    viewReportBtn.textContent = '加载中...';
    
    try {
        // 检查是否有存储的报告路径
        if (viewReportBtn.dataset.reportPath) {
            // 从存储的路径中构造完整URL
            const reportPath = viewReportBtn.dataset.reportPath;
            console.log('使用存储的报告路径:', reportPath);
            
            // 设置iframe的src属性，添加时间戳以防止缓存
            const timestamp = Date.now();
            const reportUrl = `${ApiConfig.BACKEND_SERVICE_URL}/${reportPath}?t=${timestamp}`;
            
            console.log('请求报告URL:', reportUrl);
            
            // 设置iframe的src属性
            testReportFrame.src = reportUrl;
        } else {
            // 如果没有存储的报告路径，显示提示信息
            console.warn('没有找到可用的报告路径，尝试加载最新报告...');
            
            // 尝试获取最新报告（这里可以添加一个API调用来获取最新报告路径）
            // 为了演示，我们使用默认路径
            const timestamp = Date.now();
            const reportUrl = `/results/${timestamp}/report.html`;
            testReportFrame.src = reportUrl;
        }
        
        // 显示报告容器
        reportContainer.style.display = 'block';
        
        // 滚动到报告区域
        reportContainer.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('加载报告时出错:', error);
        // 显示错误信息
        alert('加载报告失败: ' + error.message);
    } finally {
        // 恢复按钮状态
        viewReportBtn.disabled = false;
        viewReportBtn.textContent = '查看测试报告';
    }
});

// AI分析按钮点击事件处理
aiAnalysisBtn.addEventListener('click', async () => {
    const testCase = executeBtn.dataset.testCase;
    const response = executeBtn.dataset.response;
    
    if (!testCase || !response) {
        showError('缺少分析所需的数据');
        return;
    }
    
    // 显示加载状态
    aiAnalysisBtn.classList.add('loading');
    aiAnalysisBtn.textContent = '分析中...';
    
    try {
        // AI结果分析
        await analyzeTestResults(testCase, response);
        
        // 滚动到AI分析结果区域
        aiAnalysisSection.scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
        console.error('AI分析时出错:', error);
        aiAnalysisContent.innerHTML = 'AI分析时发生错误，请稍后重试。';
        aiAnalysisSection.style.display = 'block';
    } finally {
        // 恢复按钮状态
        aiAnalysisBtn.classList.remove('loading');
        aiAnalysisBtn.textContent = 'AI 结果分析';
    }
});

// 复制按钮点击事件处理
copyBtn.addEventListener('click', copyToClipboard);

// 初始化时不再添加默认示例文本到输入框
window.addEventListener('load', () => {
    // 空函数，不设置默认值
});

// 步骤切换功能
document.addEventListener('DOMContentLoaded', function() {
    // 获取所有步骤标签和区域
    const stepTabs = document.querySelectorAll('.step-tab');
    const regions = document.querySelectorAll('.region');
    
    // 为每个步骤标签添加点击事件监听器
    stepTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const stepIndex = parseInt(this.getAttribute('data-step'));
            
            // 移除所有标签的active类
            stepTabs.forEach(t => t.classList.remove('active'));
            
            // 为当前点击的标签添加active类
            this.classList.add('active');
            
            // 隐藏所有区域
            regions.forEach(region => {
                region.style.display = 'none';
            });
            
            // 显示对应的区域
            const targetRegion = document.querySelector(`.region-${stepIndex}`);
            if (targetRegion) {
                targetRegion.style.display = 'block';
            }
        });
    });
    
    // 为所有textarea元素添加双击全选功能
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('dblclick', function() {
            this.select();
        });
    });
    
    // 文件上传功能
    if (businessRulesFile) {
        businessRulesFile.addEventListener('change', handleBusinessRulesFileUpload);
    }
    
    // 初始化：只显示第一个区域（业务规则-->文本案例），隐藏其他区域
    regions.forEach((region, index) => {
        if (index === 0) {
            region.style.display = 'block';
        } else {
            region.style.display = 'none';
        }
    });
});

// 根据业务规则生成文本案例的函数
async function generateTestPointsFromRules(businessRules) { // 函数名保持不变以避免引用错误
    console.log('generateTestPointsFromRules called with:', businessRules);
    if (!businessRules) {
        alert('请输入业务规则文档内容');
        return;
    }
    
    // 确保UI元素存在
    if (!generateFromRulesBtn || !testCasesContent) {
        console.error('UI elements not found');
        alert('界面元素未找到，请刷新页面重试');
        return;
    }
    
    // 显示加载状态 - 只在生成测试要点的按钮上显示
    generateFromRulesBtn.disabled = true;
    generateFromRulesBtn.textContent = '生成中...';
    generateFromRulesBtn.classList.add('loading');
    
    try {
        console.log('Fetching from:', `${ApiConfig.BACKEND_SERVICE_URL}${ApiConfig.API_ENDPOINTS.CONVERT_TEST_CASE}`);
        const response = await fetch(`${ApiConfig.BACKEND_SERVICE_URL}${ApiConfig.API_ENDPOINTS.CONVERT_TEST_CASE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                test_case_description: businessRules,
                generation_type: "test_cases"  // 指定生成类型为测试要点
            })
        });
        
        console.log('Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('Response data:', data);
        
        if (data.status === 'success') {
            // 显示生成的测试要点
            testCasesContent.textContent = data.generated_test_cases || '未生成有效的测试要点';
            return data.generated_test_cases || '未生成有效的测试要点';
        } else {
            testCasesContent.textContent = '生成失败: ' + (data.detail || '未知错误');
            return '生成失败: ' + (data.detail || '未知错误');
        }
    } catch (error) {
        console.error('Error:', error);
        testCasesContent.textContent = '生成失败: ' + error.message;
        return '生成失败: ' + error.message;
    } finally {
        // 隐藏加载状态 - 只在生成测试要点的按钮上隐藏
        generateFromRulesBtn.disabled = false;
        generateFromRulesBtn.textContent = 'AI生成测试要点';
        generateFromRulesBtn.classList.remove('loading');
    }
}

// 处理业务规则文件上传的函数
async function handleBusinessRulesFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // 检查文件类型
    const allowedTypes = [
        'text/plain', 
        'application/msword', 
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];
    const allowedExtensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(file.type) && !allowedExtensions.includes(fileExtension)) {
        alert('请上传 TXT, DOC, DOCX, XLS 或 XLSX 格式的文件');
        event.target.value = ''; // 清空文件选择
        return;
    }
    
    try {
        // 对于文本文件，直接读取内容
        if (file.type === 'text/plain' || fileExtension === '.txt') {
            const text = await readFileAsText(file);
            businessRulesInput.value = text;
        } 
        // 对于 DOCX 文件，尝试使用 mammoth.js 解析，如果不可用则提示用户
        else if (file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' || 
                 fileExtension === '.docx') {
            if (typeof mammoth !== 'undefined') {
                try {
                    const arrayBuffer = await readFileAsArrayBuffer(file);
                    const result = await mammoth.extractRawText({arrayBuffer: arrayBuffer});
                    businessRulesInput.value = result.value;
                } catch (error) {
                    console.error('mammoth.js解析DOCX文件失败:', error);
                    // 降级处理
                    businessRulesInput.value = `【DOCX文件上传】\n文件名: ${file.name}\n文件大小: ${formatFileSize(file.size)}\n文件类型: ${file.type || fileExtension}\n\n文件解析时出现错误，将通过后端服务处理提取测试用例。`;
                }
            } else {
                // mammoth.js 未加载，降级为后端处理
                businessRulesInput.value = `【DOCX文件上传】\n文件名: ${file.name}\n文件大小: ${formatFileSize(file.size)}\n文件类型: ${file.type || fileExtension}\n\n由于浏览器环境限制，将通过后端服务处理提取测试用例。`;
            }
        }
        // 对于 Excel 文件，需要后端处理
        else if (file.type === 'application/vnd.ms-excel' || 
                 file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                 fileExtension === '.xls' || fileExtension === '.xlsx') {
            // 对于Excel文件，显示提示信息，实际处理将在后端进行
            businessRulesInput.value = `【Excel文件上传】\n文件名: ${file.name}\n文件大小: ${formatFileSize(file.size)}\n文件类型: ${file.type || fileExtension}\n\nExcel文件将通过后端服务处理提取测试用例。`;
        }
        // 对于 DOC 文件，需要后端处理或提示用户转换为 DOCX/TXT 格式
        else if (file.type === 'application/msword' || fileExtension === '.doc') {
            alert('DOC 格式需要特殊处理，请将文件转换为 DOCX 或 TXT 格式以获得更好的支持。');
            businessRulesInput.value = `【文件上传】\n文件名: ${file.name}\n文件大小: ${formatFileSize(file.size)}\n文件类型: ${file.type || fileExtension}\n\n请将文件内容复制粘贴到此处或转换为 DOCX/TXT 格式。`;
        }
    } catch (error) {
        console.error('文件读取出错:', error);
        alert('文件读取出错: ' + error.message);
        event.target.value = ''; // 清空文件选择
    }
}

// 读取文件内容为文本
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsText(file, 'UTF-8');
    });
}

// 读取文件内容为ArrayBuffer
function readFileAsArrayBuffer(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = event => resolve(event.target.result);
        reader.onerror = error => reject(error);
        reader.readAsArrayBuffer(file);
    });
}

// 格式化文件大小
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}