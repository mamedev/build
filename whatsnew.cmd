@echo off
set LASTREV=r243770
rem for /f "usebackq tokens=1-2 delims=:" %%i in (`svn info https://github.com/mamedev/mame/tags`) do if /i "%%i"=="last changed rev" set LASTREV=%%j
echo Last rev = %LASTREV%
svn log https://github.com/mamedev/mame/trunk -v -r %LASTREV%:HEAD
