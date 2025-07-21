@echo off
title Aggarwal Bhawan - PROJECT CLEANUP
echo ===============================================
echo    🏨 AGGARWAL BHAWAN PROJECT CLEANUP 🏨
echo        REMOVING UNWANTED FILES
echo ===============================================
echo.
echo 🗑️ CLEANING UP:
echo   - Debug and test files
echo   - Extra batch files
echo   - Markdown documentation files
echo   - Backup and temporary files
echo   - Unused scripts
echo.
echo 📁 KEEPING ESSENTIAL FILES:
echo   - app.py (main application)
echo   - receipt_system.py (receipt functionality)
echo   - templates/ (HTML templates)
echo   - static/ (CSS, JS, images)
echo   - hotel_management.db (database)
echo   - requirements.txt (dependencies)
echo   - START_MINIMAL.bat (launcher)
echo.
echo Press any key to start cleanup...
pause >nul
echo.

cd /d "%~dp0"

echo 🗑️ Deleting debug files...
del /q debug_*.py 2>nul
del /q test_*.py 2>nul
del /q check_*.py 2>nul
del /q clean_*.py 2>nul
del /q fix_*.py 2>nul
del /q quick_*.py 2>nul
del /q verify_*.py 2>nul
del /q init_*.py 2>nul
del /q migrate_*.py 2>nul
del /q generate_*.py 2>nul
del /q update_*.py 2>nul
del /q recreate_*.py 2>nul
del /q enhance_*.py 2>nul
del /q enhanced_*.py 2>nul
del /q final_*.py 2>nul
del /q simple_*.py 2>nul

echo 🗑️ Deleting extra batch files...
del /q START_DEBUG*.bat 2>nul
del /q START_ENHANCED*.bat 2>nul
del /q START_FIXED*.bat 2>nul
del /q START_FRESH*.bat 2>nul
del /q START_HOTEL*.bat 2>nul
del /q START_LAYOUT*.bat 2>nul
del /q START_MODERN*.bat 2>nul
del /q START_NO_REFRESH.bat 2>nul
del /q START_ORIGINAL*.bat 2>nul
del /q START_RECEIPT*.bat 2>nul
del /q START_REVERTED*.bat 2>nul
del /q START_ROOM*.bat 2>nul
del /q START_SIMPLE*.bat 2>nul
del /q START_STABLE*.bat 2>nul
del /q START_SYSTEM*.bat 2>nul
del /q START_VERBOSE*.bat 2>nul
del /q START_WITH*.bat 2>nul
del /q START_CLEAN*.bat 2>nul
del /q DEBUG_ERROR.bat 2>nul
del /q QUICK_TEST.bat 2>nul
del /q TEST_EMOJI*.bat 2>nul
del /q RUN_HOTEL*.bat 2>nul
del /q HOW_TO*.bat 2>nul
del /q launcher.bat 2>nul
del /q simple_launcher.bat 2>nul
del /q start_app.bat 2>nul

echo 🗑️ Deleting markdown documentation files...
del /q *.md 2>nul
del /q *.txt 2>nul

echo 🗑️ Deleting backup and temporary files...
del /q hotel_management_backup_*.db 2>nul
del /q aggarwal_bhawan.db 2>nul
del /q emoji_test.html 2>nul
del /q test_ui.html 2>nul
del /q redirect_to_flask.html 2>nul
del /q start_app.ps1 2>nul

echo 🗑️ Cleaning up cache directories...
rmdir /s /q __pycache__ 2>nul
rmdir /s /q .vscode 2>nul
rmdir /s /q .github 2>nul

echo ✅ CLEANUP COMPLETE!
echo.
echo 📁 REMAINING FILES:
dir /b
echo.
echo 🎯 PROJECT IS NOW CLEAN AND READY TO USE!
echo 🚀 Run START_MINIMAL.bat to start the application
echo.
pause
