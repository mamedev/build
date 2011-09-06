@echo off
set LASTREV=r13649
for /f "usebackq tokens=1-2 delims=:" %%i in (`svn info svn://mamedev.org/mame/tags`) do if /i "%%i"=="last changed rev" set LASTREV=%%j
echo Last rev = %LASTREV%
svn log svn://mamedev.org/mame/trunk -v -r %LASTREV%:HEAD
