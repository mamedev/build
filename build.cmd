@echo off
@setlocal


@rem --- switch to the script's directory
cd %~dp0


@rem --- validate that we can do 64-bit builds in this environment
@echo %path% | findstr amd64 >nul && goto :configok
@echo Error - must run under a build prompt configured for MSVC x64 building.
goto :eof


@rem --- ensure we have all the necessary tools
:configok
set ALLFOUND=1
for %%i in (mingw32-make svn 7za) do ( where /q %%i || ( set ALLFOUND=0 && echo Missing required tool %%i ) )
if not "%ALLFOUND%"=="1" goto :eof


@rem --- figure out what to do based on input parameters
@set MAKEPARAMS=-j %NUMBER_OF_PROCESSORS%
@set RESUME=0
@if "%3"=="resume" (set RESUME=1 && echo Resuming from previous attempt....)
@if "%1"=="" goto :usage
@if "%2"=="" goto :makefull
@if "%2"=="0" goto :makefull
goto :build



@rem -----------------------------------------------------------
@rem 	Build a 'u' release
@rem -----------------------------------------------------------

:build

@rem --- set up variables for a "u" update
set DIFFNAME=%1u%2.diff
set DIFFZIP=%1u%2_diff.zip
set WHATSNEWNAME=whatsnew_%1u%2.txt
set WHATSNEW=whatsnew\%WHATSNEWNAME%
set SRCBRANCH=mame%1
set SRCSUFFIX=
if not "%2"=="1" set /a SRCSUFFIX=%2-1
if not "%2"=="1" set SRCBRANCH=mame%1u%SRCSUFFIX%
set DSTBRANCH=mame%1u%2
set TEMP=%1
set VERSION=%temp:~0,1%.%temp:~1%u%2

@echo Creating u release between %SRCBRANCH% and %DSTBRANCH% to %DIFFNAME%


@rem --- see if the branch exists
svn list svn://mamedev.org/mame/tags/%SRCBRANCH% >nul 2>nul || goto :nosourcebranch
svn list svn://mamedev.org/mame/tags/%DSTBRANCH% >nul 2>nul && goto :destexists
@echo Target branch %DSTBRANCH% doesn't exist; promoting main branch....


@rem --- ensure everything is up-to-date
svn update .
svn update ..\trunk


@rem --- perform validation steps
set VALIDATED=0
call :dovalidate %3
if "%VALIDATED%"=="0" goto :eof


@rem --- all systems go, create the branch
@echo Creating target branch %DESTBRANCH%....
svn copy svn://mamedev.org/mame/trunk svn://mamedev.org/mame/tags/%DSTBRANCH% -m "MAME %VERSION% tag"


@rem --- now do the diff
:destexists
@echo Generating the full diff....
svn diff svn://mamedev.org/mame/tags/%SRCBRANCH% svn://mamedev.org/mame/tags/%DSTBRANCH% >%DIFFNAME%


@rem --- now package the diff
@echo Zipping the results....
if exist %DIFFZIP% del %DIFFZIP%
if exist %WHATSNEWNAME% del %WHATSNEWNAME%
copy %WHATSNEW% %WHATSNEWNAME% >nul
7za a -mpass=4 -mfb=255 -y -tzip %DIFFZIP% %DIFFNAME% %WHATSNEWNAME%
if exist %WHATSNEWNAME% del %WHATSNEWNAME%

@goto :eof




@rem -----------------------------------------------------------
@rem 	Build a full release
@rem -----------------------------------------------------------

:makefull

@rem --- set up variables for a full update
set WHATSNEW=whatsnew\whatsnew_%1.txt
set DSTBRANCH=mame%1
set FINALZIP=mame%1s
set FINALBINZIP=mame%1b
set TEMP=%1
set VERSION=%temp:~0,1%.%temp:~1%

@echo Creating full release for %DSTBRANCH%


@rem --- see if the branch exists
svn list svn://mamedev.org/mame/tags/%DSTBRANCH% >nul 2>nul && goto :destexistsfull
@echo Target branch %DSTBRANCH% doesn't exist; promoting main branch....


@rem --- ensure everything is up-to-date
svn update .
svn update ..\trunk


@rem --- perform validation steps
set VALIDATED=0
call :dovalidate %2
if "%VALIDATED%"=="0" goto :eof


@rem --- all systems go, create the branch
@echo Creating target branch %DESTBRANCH%....
svn copy svn://mamedev.org/mame/trunk svn://mamedev.org/mame/tags/%DSTBRANCH% -m "MAME %VERSION% tag"
goto :alreadybuilt


@rem --- build the debug version
:destexistsfull
@echo Building debug version....
set ARCHOPTS=
set SUFFIX=
set MSVC_BUILD=
set PTR64=
set DEBUG=1
call :performbuild mamed || goto :eof


@rem --- build the release version
@echo Building release version....
set ARCHOPTS=
set SUFFIX=
set MSVC_BUILD=
set PTR64=
set DEBUG=
call :performbuild mame || goto :eof


@rem --- build the p6-optimized version
:alreadybuilt
@echo Building p6 version....
set ARCHOPTS=-march=pentiumpro
set SUFFIX=pp
set MSVC_BUILD=
set PTR64=
set DEBUG=
call :performbuild mamepp || goto :eof


@rem --- build the 64-bit version
@echo Building 64-bit version....
set ARCHOPTS=
set SUFFIX=64
set MSVC_BUILD=1
set PTR64=1
set DEBUG=
call :performbuild vmame64 || goto :eof


@rem --- now export the actual tree
@echo Checking out a temp copy....
if exist tempexport rd /s/q tempexport
svn export svn://mamedev.org/mame/tags/%DSTBRANCH% tempexport >nul


@rem --- copy in the whatsnew file
copy %WHATSNEW% tempexport\whatsnew.txt


@rem --- now package the results
if exist mame.zip del mame.zip
if exist %FINALZIP%.zip del %FINALZIP%.zip
if exist %FINALZIP%.exe del %FINALZIP%.exe
pushd tempexport
@echo Creating 7zip archive....
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\%FINALZIP%.exe * >nul
@echo Creating raw ZIP....
7za a -mx=0 -y -r -tzip ..\mame.zip * >nul
popd
@echo Creating final ZIP....
7za a -mpass=4 -mfb=255 -y -tzip %FINALZIP%.zip mame.zip >nul
del mame.zip


@rem --- now build the official binary
@echo Building official binary....
call :buildbinary mame %FINALBINZIP%.exe

@echo Building official debug binary....
call :buildbinary mamed %FINALBINZIP%_debug.exe

@echo Building official I686 binary....
call :buildbinary mamepp %FINALBINZIP%_i686.exe

@echo Building official 64-bit binary....
call :buildbinary v64mame %FINALBINZIP%_64bit.exe

goto :eof



@rem -----------------------------------------------------------
@rem 	Build a final binary version
@rem 	
@rem 	%1 = mame.exe name (without .exe)
@rem 	%2 = final filename
@rem -----------------------------------------------------------

:buildbinary
if exist tempbin rd /s/q tempbin
if exist %2 del %2
mkdir tempbin
pushd tempbin
copy ..\%WHATSNEW% whatsnew.txt
copy ..\..\trunk\%1.exe
copy ..\..\trunk\obj\windows\%1\chdman.exe
copy ..\..\trunk\obj\windows\%1\romcmp.exe
copy ..\..\trunk\obj\windows\%1\jedutil.exe
copy ..\..\trunk\obj\windows\%1\ledutil.exe
mkdir docs
copy ..\..\trunk\docs\*.* docs
7za x ..\mamedirs.zip
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\%2
popd

goto :eof



@rem -----------------------------------------------------------
@rem 	Perform a build
@rem 	
@rem    %1 = object directory/filename
@rem 	%2..%5 = build options
@rem -----------------------------------------------------------

:performbuild
pushd ..\trunk


@rem --- First cleanup old files
if "%RESUME%"=="0" rd /s/q ..\trunk\obj\windows\%1
if exist %1.exe del %1.exe
if exist chdman.exe del chdman.exe
if exist romcmp.exe del romcmp.exe
if exist jedutil.exe del jedutil.exe
if exist ledutil.exe del ledutil.exe


@rem --- Do the build
@echo mingw32-make buildtools %~2 %~3 %~4 %~5
mingw32-make buildtools %~2 %~3 %~4 %~5 || goto :builderror %1
@echo mingw32-make %MAKEPARAMS% %~2 %~3 %~4 %~5
mingw32-make %MAKEPARAMS% %~2 %~3 %~4 %~5 || goto :builderror %1


@rem --- Stash the specific binaries
move /y chdman.exe obj\windows\%1\
move /y romcmp.exe obj\windows\%1\
move /y jedutil.exe obj\windows\%1\
move /y ledutil.exe obj\windows\%1\


popd
goto :eof



@rem -----------------------------------------------------------
@rem 	Find drivers
@rem -----------------------------------------------------------

:finddrivers
@echo Finding all GAME macros in drivers....
findstr "\<GAME.*\([^,]*,[^,]*,[^,]*,[^,]*,[^,]*,.*\)" ..\trunk\src\mame\drivers\*.c >gamelist.txt

@echo Pruning commented drivers....
findstr /v "\/\/.*GAME" gamelist.txt >gamelist2.txt
findstr /v "\/\*[^*]*GAME" gamelist2.txt >gamelist3.txt

@echo Scanning for missing entries....
for /f "delims=:,( tokens=1-4" %%i in (gamelist3.txt) do ( findstr " %%l " ..\trunk\src\mame\mamedriv.c >nul || ( set MISSING=1 && echo %%l - %%i ) )

del gamelist.txt
del gamelist2.txt
del gamelist3.txt
goto :eof



@rem -----------------------------------------------------------
@rem 	Perform validation steps
@rem -----------------------------------------------------------

:dovalidate

@rem --- see if the whatsnew exists
if not exist %WHATSNEW% goto :nowhatsnew
findstr 123456789 %WHATSNEW% >nul && goto :junkinwhatsnew


@rem --- look for junk files
@echo Deleting junk files....
del /s ..\trunk\*.rej
del /s ..\trunk\*~
del /s ..\trunk\*#
del /s ..\trunk\*.s


@rem --- make sure all filenames are lowercase
@echo Ensuring all filenames are lowercase....
dir /s /b ..\trunk\src | findstr "[ABCDEFGHIJKLOPQRSTUVWXYZ]" && goto :uppercasenames


@rem --- verify the version on the top of tree
@echo Verifying version.c....
findstr %VERSION% ..\trunk\src\version.c >nul || goto :wrongversion


@rem --- run a cleanup pass
@if not exist ..\trunk\srcclean.exe (
pushd ..\trunk
mingw32-make srcclean.exe
popd
)
@echo Cleaning up tabs/spaces/end of lines....
for /r ..\trunk\src %%i in (*.c) do ..\trunk\srcclean %%i || goto :cleanupfailed
for /r ..\trunk\src %%i in (*.h) do ..\trunk\srcclean %%i || goto :cleanupfailed
for /r ..\trunk\src %%i in (*.mak) do ..\trunk\srcclean %%i || goto :cleanupfailed


@rem --- verify that all the games are referenced
set MISSING=0
call :finddrivers
if not "%MISSING%"=="0" goto :drivmissing


@rem --- verify that everything is checked in
@echo Verifying that everything is checked in....
svn status %WHATSNEW% | findstr whatsnew >nul && goto :notcheckedin
svn status ..\trunk\src | findstr trunk >nul && goto :notcheckedin
svn status ..\trunk\makefile | findstr trunk >nul && goto :notcheckedin


@echo Verifying debug build....
set ARCHOPTS=
set SUFFIX=
set MSVC_BUILD=
set PTR64=
set DEBUG=1
call :performbuild mamed || goto :eof
set DEBUG=

@echo Verifying validation....
..\trunk\mamed -valid >nul || goto :validationerror

@echo Verifying release build....
set ARCHOPTS=
set SUFFIX=
set MSVC_BUILD=
set PTR64=
set DEBUG=
call :performbuild mame || goto :eof

set VALIDATED=1
@goto :eof




@rem -----------------------------------------------------------
@rem 	Error messages
@rem -----------------------------------------------------------

:usage
@echo Usage:
@echo   build ^<primaryver^> ^<unum^> [resume]
@goto :eof

:nowhatsnew
@echo File %WHATSNEW% doesn't exist!
@goto :eof

:junkinwhatsnew
@echo File %WHATSNEW% contains 123456789 junk.
@goto :eof

:uppercasenames
@echo Some filenames have upper-case names.
@goto :eof

:nosourcebranch
@echo Source branch %SRCBRANCH% doesn't exist!
@goto :eof

:notcheckedin
@echo Not everything is checked in!
@goto :eof

:garbagefiles
@echo Some garbage .rej or ~ suffix files exist!
goto :eof

:drivmissing
@echo Missing drivers found!
@goto :eof

:wrongversion
@echo Version.c doesn't contain the correct version! (%VERSION%)
@goto :eof

:builderror
@echo Error building top of tree (target=%1)
@goto :eof

:validationerror
@echo Error in validation routines:
mamed -valid
@goto :eof

:cleanupfailed
@echo Cleanup failed!
@goto :eof

