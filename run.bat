@echo off
REM ѯ���û��Ƿ����
echo ��ȷ��Ҫ��������δ�ύ�ĸ��Ĳ�����Git�ֿ���[Y/N]
choice /C YN /M "���������ѡ��: "
if errorlevel 2 goto end
if errorlevel 1 goto start

:start
REM ������ǰĿ¼������git�޸�
git checkout -- .

REM ��ȡ���µĴ����Ը���git
git pull

REM ִ�е�ǰĿ¼�ڵ�start.py�ļ�
python start.py

goto end

:end
echo ������ȡ������ɡ�
pause