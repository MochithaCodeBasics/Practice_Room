@echo off
echo ==========================================
echo      Math ^& Stats Practice Room Setup
echo ==========================================
echo.
echo [1/2] Installing Backend dependencies (Python)...
python -m pip install -r backend/requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python dependency installation failed.
    echo Please ensure Python is installed and added to PATH.
    pause
    exit /b
)
echo.
echo [1.5/2] Building Docker Images...
echo Building base Python image...
docker build -t practice-room-python:latest -f backend/docker/Dockerfile.python backend
echo Building GenAI image...
docker build -t practice-room-genai:latest -f backend/docker/Dockerfile.genai backend
if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Docker build failed. Functionality might be limited.
    echo Ensure Docker Desktop is running if you want to use isolated execution.
)
echo.
echo [2/2] Installing Frontend dependencies (Node.js)...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Node.js dependency installation failed.
    echo Please ensure Node.js is installed.
    pause
    exit /b
)
cd ..

echo.
echo ==========================================
echo        Setup Complete! Ready to Launch
echo ==========================================
echo.
echo You can now double-click 'start_app.bat' to run the application.
echo.
pause
