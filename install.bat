@echo off
echo ====================================
echo  FGO从者猜猜看游戏安装程序
echo ====================================
echo.

:: 检查Python是否已安装
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python。请先安装Python 3.8或更高版本。
    echo 您可以从 https://www.python.org/downloads/ 下载安装。
    pause
    exit /b 1
)

:: 显示检测到的Python版本
echo [信息] 检测到Python：
python --version
echo.

:: 创建虚拟环境
echo [步骤1] 创建虚拟环境...
if exist venv (
    echo [信息] 虚拟环境已存在，跳过创建步骤。
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败。
        pause
        exit /b 1
    )
    echo [信息] 虚拟环境创建成功。
)

:: 激活虚拟环境并安装依赖
echo [步骤2] 安装所需依赖...
call venv\Scripts\activate.bat
pip install flask flask-wtf flask-session
pip install requests Pillow
echo [信息] 基本依赖安装完成。

:: 安装完成
echo ====================================
echo  安装完成!
echo ====================================
echo.
echo 启动应用，请运行:
echo call venv\Scripts\activate.bat
echo cd flask-app
echo flask run
echo.
echo 然后在浏览器中访问: http://127.0.0.1:5000
echo.
pause