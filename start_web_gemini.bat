@echo off
chcp 65001 >nul
echo.
echo ====================================
echo   自然语言转SQL查询工具 - Gemini版本
echo ====================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: Python未安装或不在PATH中
    echo 请安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 检查GEMINI_API_KEY环境变量
if "%GEMINI_API_KEY%"=="" (
    echo ⚠️  警告: 未设置GEMINI_API_KEY环境变量
    echo.
    echo 🔧 请按以下步骤设置API Key:
    echo 1. 访问 https://makersuite.google.com/app/apikey
    echo 2. 获取您的Gemini API Key
    echo 3. 运行命令: set GEMINI_API_KEY=your_api_key
    echo 4. 或者在系统环境变量中设置GEMINI_API_KEY
    echo.
    echo 💡 您也可以在网页中选择其他模型后端
    echo.
)

echo 🚀 正在启动Web服务器...
echo.
echo 📝 默认配置:
echo    - 后端: Google Gemini
echo    - 模型: gemini-1.5-flash
echo    - 端口: 5000
echo.
echo 🌐 服务启动后请访问: http://localhost:5000
echo.

REM 启动Web服务器，使用Gemini作为默认后端
python web_server.py --backend gemini --model gemini-1.5-flash

pause 