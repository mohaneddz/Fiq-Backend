@echo off
REM Start ngrok tunnels for all backend services
REM Requires ngrok to be installed and authenticated

echo Starting ngrok tunnels for all services...
echo.

REM Add ngrok to PATH if not found (winget installs to this location)
where ngrok >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\ngrok.exe" (
        set "PATH=%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links"
    ) else if exist "%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe\ngrok.exe" (
        set "PATH=%PATH%;%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\Ngrok.Ngrok_Microsoft.Winget.Source_8wekyb3d8bbwe"
    ) else (
        echo ERROR: ngrok not found. Please install it with: winget install ngrok.ngrok
        echo Then restart your terminal.
        pause
        exit /b 1
    )
)

REM Check if ngrok is authenticated by checking config
ngrok config check >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ngrok is not configured. Please enter your auth token.
    echo Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken
    echo.
    set /p NGROK_TOKEN="Enter your ngrok authtoken: "
    ngrok config add-authtoken %NGROK_TOKEN%
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to set auth token. Please try again.
        pause
        exit /b 1
    )
    echo Auth token configured successfully!
    echo.
)

echo Services:
echo   Chat    - Port 5001
echo   Relapse - Port 5002
echo   Blog    - Port 5003
echo   Voice   - Port 5004
echo.

REM Start ngrok with multiple tunnels using config
ngrok start --all --config ngrok.yml

pause
