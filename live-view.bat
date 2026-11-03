@echo off
rem Watch Nuclear@Home tasks running on this Windows PC in 3D. Double-click this file.
rem Needs Python 3.11+ (python.org, tick "Add python.exe to PATH") and this project folder.
rem Reads only the task progress and snapshots in C:\ProgramData\BOINC\slots; closes with this window.
cd /d "%~dp0"
where py >nul 2>nul || (echo Python is not installed: get it from https://www.python.org/downloads/ & pause & exit /b 1)
start "" "http://127.0.0.1:8080/cascade.html?live=1"
py scripts\serve.py 8080
pause
