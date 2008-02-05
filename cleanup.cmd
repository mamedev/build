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
del /s *.s


@rem --- make sure all filenames are lowercase
@echo Ensuring all filenames are lowercase....
dir /s /b src | findstr "[ABCDEFGHIJKLOPQRSTUVWXYZ]" && goto :uppercasenames


@rem --- run a cleanup pass
@if not exist srcclean.exe (
mingw32-make maketree
mingw32-make srcclean.exe
)
@echo Cleaning up tabs/spaces/end of lines....
for /r src %%i in (*.c) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.h) do srcclean %%i || goto :cleanupfailed
for /r src %%i in (*.mak) do srcclean %%i || goto :cleanupfailed


@rem --- verify that all the games are referenced
set MISSING=0
call :finddrivers
if not "%MISSING%"=="0" goto :drivmissing

@goto :eof




@rem -----------------------------------------------------------
@rem 	Find drivers
@rem -----------------------------------------------------------

:finddrivers
@echo Finding all GAME macros in drivers....
findstr "\<GAME.*\([^,]*,[^,]*,[^,]*,[^,]*,[^,]*,.*\)" src\mame\drivers\*.c >gamelist.txt

@echo Pruning commented drivers....
findstr /v "\/\/.*GAME" gamelist.txt >gamelist2.txt
findstr /v "\/\*[^*]*GAME" gamelist2.txt >gamelist3.txt

@echo Scanning for missing entries....
for /f "delims=:,( tokens=1-4" %%i in (gamelist3.txt) do ( findstr " %%l " src\mame\mamedriv.c >nul || ( set MISSING=1 && echo %%l - %%i ) )

del gamelist.txt
del gamelist2.txt
del gamelist3.txt
goto :eof



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
