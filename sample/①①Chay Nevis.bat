@echo off
chcp 932 > nul

REM #jww
REM #cd
REM #h2
REM #hc Quet tim ong va nen tham chieu
REM #1 Bam chuot phai diem nuoc tap trung ve
REM #10#
REM #e

echo ==== START PIPE TOOL ====

copy jwc_temp.txt temp.txt > nul
py Nevis_no_ui.py temp.txt

if errorlevel 1 (
    echo NEVIS Python loi.
    pause
    exit /b
)

if exist jwc_out.txt copy jwc_out.txt jwc_temp.txt > nul
exit /b