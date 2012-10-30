@echo off
set LASTREV=r15683
for /f "usebackq tokens=1-2 delims=:" %%i in (`svn info svn://dspnet.fr/mame/tags`) do if /i "%%i"=="last changed rev" set LASTREV=%%j
echo Last rev = %LASTREV%
svn log svn://dspnet.fr/mame/trunk -v -r %LASTREV%:HEAD
