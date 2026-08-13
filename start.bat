@echo off
REM Elkayem Manpower Allocation System – Windows Startup Script
REM Usage: start.bat [options]

setlocal enabledelayedexpansion

set PORT=8080
set MODE=foreground

:parse_args
if "%1"=="" goto start_server
if "%1"=="-p" (
    set PORT=%2
    shift
    shift
    goto parse_args
) else if "%1"=="--port" (
    set PORT=%2
    shift
    shift
    goto parse_args
) else if "%1"=="-b" (
    set MODE=background
    shift
    goto parse_args
) else if "%1"=="--background" (
    set MODE=background
    shift
    goto parse_args
) else if "%1"=="-s" (
    set MODE=stop
    shift
    goto parse_args
) else if "%1"=="--stop" (
    set MODE=stop
    shift
    goto parse_args
) else if "%1"=="-h" (
    goto show_help
) else if "%1"=="--help" (
    goto show_help
) else (
    echo Unknown option: %1
    goto show_help
)

:show_help
echo Usage: start.bat [OPTIONS]
echo.
echo Options:
echo   -p, --port PORT         Use custom port (default: 8080)
echo   -b, --background        Run in background
echo   -s, --stop              Stop background server
echo   -h, --help              Show this help message
echo.
echo Examples:
echo   start.bat               Start in foreground on port 8080
echo   start.bat -p 9000       Start on port 9000
echo   start.bat -b            Start in background
echo   start.bat -s            Stop background server
exit /b 0

:start_server
REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed or not in PATH
    echo Please install Python 3.6 or higher from python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Check if server_advanced.py exists
if not exist "server_advanced.py" (
    echo [ERROR] server_advanced.py not found
    echo Please ensure server_advanced.py is in the current directory
    pause
    exit /b 1
)

if not exist "index_advanced.html" (
    echo [WARNING] index_advanced.html not found in current directory
    echo The server may not serve the web interface properly
)

if "%MODE%"=="foreground" goto start_foreground
if "%MODE%"=="background" goto start_background
if "%MODE%"=="stop" goto stop_server

:start_foreground
cls
echo.
echo ===============================================================
echo   Starting Elkayem Manpower Allocation Server
echo ===============================================================
echo.
echo Port: %PORT%
echo Mode: Foreground
echo Database: elkayem.db
echo.
echo [OK] Server starting...
echo [OK] Open browser: http://localhost:%PORT%
echo.
echo Default login:
echo   Username: admin
echo   Password: admin123
echo.
echo Press Ctrl+C to stop server
echo ===============================================================
echo.

python server_advanced.py
goto end

:start_background
echo Starting server in background...
start "Elkayem Manpower Server" cmd /c "python server_advanced.py > server.log 2>&1"
timeout /t 2 /nobreak
if exist "server.log" (
    echo [OK] Server started successfully
    echo Access at: http://localhost:%PORT%
    echo View logs: type server.log
    echo Stop server: start.bat -s
) else (
    echo [ERROR] Failed to start server
    pause
    exit /b 1
)
goto end

:stop_server
echo Stopping server...
tasklist /FI "WINDOWTITLE eq Elkayem Manpower Server" 2>NUL | find /I /N "cmd.exe">NUL
if "%ERRORLEVEL%"=="0" (
    taskkill /FI "WINDOWTITLE eq Elkayem Manpower Server" /T /F >nul 2>&1
    timeout /t 1 /nobreak
    echo [OK] Server stopped
) else (
    echo [WARNING] Server window not found
    echo Trying alternate method...
    taskkill /F /IM python.exe >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] No Python process found
    ) else (
        echo [OK] Server stopped
    )
)
goto end

:end
endlocal
exit /b 0
