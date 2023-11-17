@echo off

echo Installing Python packages from requirements.txt...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo Error: Failed to install Python packages. Please check the requirements.txt file.
    pause
    exit /b 1
)

echo Python packages installed successfully.
echo Running app.py...

start /B cmd /C "python app.py"

echo Opening the web browser...
start http://127.0.0.1:5000  # Replace with your Flask app's local URL

exit /b 0
