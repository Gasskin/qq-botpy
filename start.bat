@echo off
cd /d %~dp0
git pull
if %ERRORLEVEL% neq 0 (
    echo Git update failed, start.py will not be run.
    exit /b %ERRORLEVEL%
)

python start.py