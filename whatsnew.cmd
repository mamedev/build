@echo off
for /f %%i in ('git describe --tags --abbrev=0') do set LASTREV=%%i

rem for /f "usebackq tokens=1-2 delims=:" %%i in (`svn info https://github.com/mamedev/mame/tags`) do if /i "%%i"=="last changed rev" set LASTREV=%%j
echo Last = %LASTREV%
rem svn log https://github.com/mamedev/mame/trunk -v -r %LASTREV%:HEAD
