@echo off
REM 询问用户是否继续
echo 你确定要放弃所有未提交的更改并更新Git仓库吗？[Y/N]
choice /C YN /M "请输入你的选择: "
if errorlevel 2 goto end
if errorlevel 1 goto start

:start
REM 放弃当前目录的所有git修改
git checkout -- .

REM 拉取最新的代码以更新git
git pull

REM 执行当前目录内的start.py文件
python start.py

goto end

:end
echo 操作已取消或完成。
pause