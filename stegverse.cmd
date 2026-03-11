@echo off
setlocal
set REPO_ROOT=%~dp0
python "%REPO_ROOT%engine\stegverse_cli.py" %*
endlocal
