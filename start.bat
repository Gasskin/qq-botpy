@echo off


echo Are you sure you want to discard all local changes? (y/n)
set /p confirm=

if /i "%confirm%"=="y" (
    git reset --hard HEAD
    git pull
    python entry.py
) 

