@echo off
echo ========================================
echo    HAMMAD BHAI AI Assistant Launcher
echo    Created by: MUHAMMAD HAMMAD ZUBAIR
echo ========================================
echo.
echo Starting Gemini Chat Application...
echo.
echo Make sure you've added your API key to app.py before running!
echo Or set GEMINI_API_KEY environment variable.
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo ✅ Virtual environment found. Activating...
    call venv\Scripts\activate
) else (
    echo ⚠️  Virtual environment not found. Using global Python...
    echo To create virtual environment, run: python -m venv venv
)

echo.
echo 🚀 Starting Flask application...
echo 🌐 App will be available at: http://127.0.0.1:5000
echo 🔄 Press Ctrl+C to stop the server
echo.

REM Run the Flask application
python app.py

echo.
echo 👋 Application stopped. Thanks for using HAMMAD BHAI AI Assistant!

REM Deactivate virtual environment if it was activated
if exist "venv\Scripts\activate.bat" (
    call deactivate
)

pause