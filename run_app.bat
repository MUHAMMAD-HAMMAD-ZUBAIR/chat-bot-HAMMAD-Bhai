@echo off
echo Starting Gemini Chat Application...
echo.
echo Make sure you've added your API key to app.py before running!
echo.

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Flask application
python app.py

REM Deactivate the virtual environment when done
call deactivate

pause
