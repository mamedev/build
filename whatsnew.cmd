@echo off
rem for /f "usebackq tokens=1-2 delims=:" %%i in (`svn info https://github.com/mamedev/mame/tags`) do if /i "%%i"=="last changed rev" set LASTREV=%%j
set LASTREV=r248552
svn log https://github.com/mamedev/mame/trunk -v -r %LASTREV%:HEAD
