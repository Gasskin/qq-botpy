@echo off

echo �������и��Ĳ�����GIT��[Y/N]
choice /C YN /M "ѡ��: "

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