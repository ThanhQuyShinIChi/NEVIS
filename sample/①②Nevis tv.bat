@echo off
chcp 65001 >nul
title NEVIS Library Debug

echo ==========================================
echo         NEVIS LIBRARY DEBUG MODE
echo ==========================================
echo.

cd /d "%~dp0"

echo Dang chay Nevis_thu_vien.py...
echo.

py -X utf8 "Nevis_thu_vien.py"

echo.
echo ==========================================
echo              KET THUC
echo ==========================================
echo.
echo Neu co loi, xem toan bo traceback o tren.
echo.

pause