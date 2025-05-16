@echo off
rem 设置控制台代码页为UTF-8，解决中文乱码
chcp 65001 >nul
title FGO从者猜猜看 - 测试环境
color 0B
echo ====================================
echo  FGO从者猜猜看游戏 - 测试环境启动
echo  启动时间: %date% %time%
echo ====================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python。请先安装Python。
    pause
    exit /b 1
)

:: 检查并创建虚拟环境
if not exist venv (
    echo [信息] 虚拟环境不存在，正在创建...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败，请检查Python安装。
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境已创建。
) else (
    echo [信息] 检测到已有虚拟环境。
)

:: 启动虚拟环境
echo [信息] 启动虚拟环境...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 启动虚拟环境失败。
    pause
    exit /b 1
)
echo [成功] 虚拟环境已激活。

:: 设置测试环境变量
echo [信息] 设置测试环境变量...
set FLASK_ENV=development
set FLASK_DEBUG=1
set FLASK_APP=app
set SECRET_KEY=dev-test-secret-key

:: 检查wsgi.py文件 - 注意端口修改为51000
if not exist wsgi.py (
    echo [信息] 创建wsgi.py文件...
    (
        echo from app import create_app
        echo application = create_app^(^)
        echo.
        echo if __name__ == "__main__":
        echo     application.run^(debug=True, host='0.0.0.0', port=51000^)
    ) > wsgi.py
)

:: 检查必要的依赖 - 确保在虚拟环境中安装
echo [信息] 检查依赖...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 虚拟环境中未安装Flask。正在安装...
    pip install flask
)

:: 确保其他依赖也在虚拟环境中安装
pip show flask-wtf >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 安装Flask-WTF...
    pip install flask-wtf
)

pip show waitress >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 预安装Waitress服务器...
    pip install waitress
)

pip show requests >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 预安装requests
    pip install requests
)

:: 显示本机IP
echo [信息] 本机IP地址:
ipconfig | findstr /i "IPv4"
echo.

echo [信息] 使用Flask开发服务器启动应用...
echo [信息] 调试模式已启用。代码修改后将自动重新加载。
echo [信息] 访问地址: http://localhost:51000
echo ====================================
flask run --host=0.0.0.0 --port=51000 --debug

pause