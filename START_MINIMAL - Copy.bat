@echo off
title Aggarwal Bhawan, Haridwar - FLICKERING FIXED VERSION
echo ===============================================
echo    🏨 AGGARWAL BHAWAN, HARIDWAR 🏨
echo        FLICKERING ISSUE FIXED
echo ===============================================
echo.
echo � FLICKERING FIX APPLIED:
echo   - Port confusion resolved (Flask uses 5000, NOT 3000)
echo   - JavaScript refresh logic disabled
echo   - Next.js conflicts prevented
echo   - Auto-refresh intervals stopped
echo.
echo 🎯 FINAL SOLUTION:
echo   - No page refreshing or flickering
echo   - Download button works perfectly
echo   - Page remains completely stable
echo   - Clean Flask-only environment
echo.
echo 🌐 CORRECT URL: http://localhost:5000
echo 🚫 DO NOT USE: http://localhost:3000 (causes Next.js errors)
echo 👤 Login: admin / admin123
echo.
echo Press Ctrl+C to stop the server
echo ===============================================
echo.

:: Kill any existing processes that might conflict
taskkill /F /IM python.exe 2>nul >nul

:: Clear browser cache suggestion
echo 💡 TIP: Clear browser cache if you still see issues
echo.

cd /d "%~dp0"

:: Start Flask app directly
echo 🚀 Starting Aggarwal Bhawan Management System...
echo 🌐 Access at: http://localhost:5000
echo 🚫 NEVER use localhost:3000 - that causes flickering!
echo ✅ All refresh mechanisms disabled
echo.

python app.py
pause
