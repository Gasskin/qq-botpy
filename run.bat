@echo off

echo 放弃所有更改并更新GIT？[Y/N]
choice /C YN /M "选择: "
if errorlevel 2 goto end
if errorlevel 1 goto start

:start
git reset --hard HEAD
if errorlevel > 1 goto end

git pull
if errorlevel > 1 goto end

python entry.py
goto end

:end
echo 操作已取消或完成。
pause