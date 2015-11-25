@echo off
@setlocal


@rem --- verify environment
if not exist .\src goto :badenvironment
if not exist .\makefile goto :badenvironment


@rem --- look for junk files
@echo Deleting junk files....
del /s *.rej
del /s *~
del /s *#


@rem --- make sure all filenames are lowercase
@echo Ensuring all filenames are lowercase....
@rem dir /s /b src | findstr /v /c:"\\sdl\\" | findstr /v README | findstr "[ABCDEFGHIJKLOPQRSTUVWXYZ]" && goto :uppercasenames


@rem --- run a cleanup pass
@if not exist srcclean.exe (
make maketree
make srcclean.exe
)
@echo Cleaning up tabs/spaces/end of lines....
for /r src %%i in (*.cpp) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.h) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.mak) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.lst) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.lay) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.inc) do srcclean %%i || goto :cleanupfailed
for /r hash %%i in (*.xml) do srcclean %%i || goto :cleanupfailed


@rem --- verify that all the games are referenced
set MISSING=0
call :finddrivers
if not "%MISSING%"=="0" goto :drivmissing

@goto :eof


@rem -----------------------------------------------------------
@rem 	Error messages
@rem -----------------------------------------------------------

:badenvironment
@echo This command must be executed from the directory you wish to verify.
@goto :eof

:uppercasenames
@echo Some filenames have upper-case names.
@goto :eof

:drivmissing
@echo Missing drivers found!
@goto :eof
