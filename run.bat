@echo off

echo �������и��Ĳ�����GIT��[Y/N]
choice /C YN /M "ѡ��: "
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
echo ������ȡ������ɡ�
pause