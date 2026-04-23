@echo off
echo ========================================
echo Gemini Chatbot Installation
echo ========================================
echo.

echo Installing required packages...
pip install google-generativeai Pillow

echo.
echo ========================================
echo Testing API Connection
echo ========================================
echo.

python test_gemini_api.py

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo The chatbot is now ready to use.
echo Simply run your Flask application:
echo   python app.py
echo.
echo The chatbot widget will appear at the
echo bottom-right corner of all pages.
echo.
echo Features:
echo - Text chat with Gemini AI
echo - Voice input and output
echo - Camera capture and analysis
echo - File upload and analysis
echo.
pause
