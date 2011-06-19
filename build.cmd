@echo off
@setlocal

@rem --- set to 1 to enable testing; otherwise, leave blank
@set TEST=1


@rem --- use these macros to redirect to NUL so that they don't redirect
@rem --- when testing
@set NULLOUT=^>nul
@set NULLERR=2^>nul
@if not "%TEST%" == "" echo on& set NULLOUT=&set NULLERR=2^>^&1


@rem --- switch to the script's directory
cd %~dp0


@rem --- validate that we have a config script
if exist ..\trunk\config.cmd goto :configok
@echo Error - no config.cmd present; make sure there is a config.cmd that accepts both "32" and "64" as parameters
goto :eof


@rem --- ensure we have all the necessary tools
:configok
call ..\trunk\config 32
@if not "%TEST%" == "" echo on
@if not "%TEST%" == "" set
set ALLFOUND=1
for %%i in (make svn 7za) do ( where /q %%i || ( set ALLFOUND=0 && echo Missing required tool %%i ) )
if not "%ALLFOUND%"=="1" goto :eof


@rem --- figure out what to do based on input parameters
set /a PROCS=%NUMBER_OF_PROCESSORS% + 1
set MAKEPARAMS=-j %PROCS%
set RESUME=0
set REVISION=%1
if "%4"=="resume" (set RESUME=1 && echo Resuming from previous attempt....)
if "%1"=="" goto :usage
if "%2"=="" goto :usage
if "%3"=="" goto :makefull
if "%3"=="0" goto :makefull
goto :build



@rem -----------------------------------------------------------
@rem 	Build a 'u' release
@rem -----------------------------------------------------------

:build

@rem --- set up variables for a "u" update
set DIFFNAME=%2u%3.diff
set DIFFZIP=%2u%3_diff.zip
set WHATSNEWNAME=whatsnew_%2u%3.txt
set WHATSNEW=whatsnew\%WHATSNEWNAME%
set SRCBRANCH=mame%2
set SRCSUFFIX=
if not "%3"=="1" set /a SRCSUFFIX=%3-1
if not "%3"=="1" set SRCBRANCH=mame%2u%SRCSUFFIX%
set DSTBRANCH=mame%2u%3
set TEMP=%2
set VERSION=%temp:~0,1%.%temp:~1%u%3

@echo Creating u release between %SRCBRANCH% and %DSTBRANCH% to %DIFFNAME%


@rem --- see if the branch exists
svn list svn://mamedev.org/mame/tags/%SRCBRANCH% %NULLOUT% %NULLERR% || goto :nosourcebranch
svn list svn://mamedev.org/mame/tags/%DSTBRANCH% %NULLOUT% %NULLERR% && goto :destexists
@echo Target branch %DSTBRANCH% doesn't exist; promoting main branch....


@rem --- ensure everything is up-to-date
svn update -r %REVISION% .
svn update -r %REVISION% ..\trunk


@rem --- perform validation steps
set VALIDATED=0
call :dovalidate
if "%VALIDATED%"=="0" goto :eof


@rem --- all systems go, create the branch
@echo Creating target branch %DESTBRANCH%....
if "%TEST%" == "" svn copy svn://mamedev.org/mame/trunk -r %REVISION% svn://mamedev.org/mame/tags/%DSTBRANCH% -m "MAME %VERSION% tag"


@rem --- now do the diff
:destexists
@echo Generating the full diff....
if exist temp rd /s/q temp
if exist %DIFFNAME% del %DIFFNAME%
svn export svn://mamedev.org/mame/tags/%SRCBRANCH% temp\%SRCBRANCH%
svn export svn://mamedev.org/mame/tags/%DSTBRANCH% temp\%DSTBRANCH%
cd temp
for /f "usebackq" %%i in (`dir /b %SRCBRANCH%`) do ( move %SRCBRANCH%\%%i %%i-old && move %DSTBRANCH%\%%i %%i && diff -Nru %%i-old %%i >>..\%DIFFNAME% )
cd ..
@rem svn diff svn://mamedev.org/mame/tags/%SRCBRANCH% svn://mamedev.org/mame/tags/%DSTBRANCH% >%DIFFNAME%


@rem --- now package the diff
@echo Zipping the results....
if exist %DIFFZIP% del %DIFFZIP%
if exist %WHATSNEWNAME% del %WHATSNEWNAME%
copy %WHATSNEW% %WHATSNEWNAME% %NULLOUT%
7za a -mpass=4 -mfb=255 -y -tzip %DIFFZIP% %DIFFNAME% %WHATSNEWNAME%
if exist %WHATSNEWNAME% del %WHATSNEWNAME%

@goto :eof




@rem -----------------------------------------------------------
@rem 	Build a full release
@rem -----------------------------------------------------------

:makefull

@rem --- set up variables for a full update
set WHATSNEW=whatsnew\whatsnew_%2.txt
set DSTBRANCH=mame%2
set FINALZIP=mame%2s
set FINALBINZIP=mame%2b
set TEMP=%2
set VERSION=%temp:~0,1%.%temp:~1%

@echo Creating full release for %DSTBRANCH%


@rem --- see if the branch exists
svn list svn://mamedev.org/mame/tags/%DSTBRANCH% %NULLOUT% %NULLERR% && goto :destexistsfull
@echo Target branch %DSTBRANCH% doesn't exist; promoting main branch....


@rem --- ensure everything is up-to-date
svn update -r %REVISION% .
svn update -r %REVISION% ..\trunk


@rem --- perform validation steps
set VALIDATED=0
call :dovalidate
if "%VALIDATED%"=="0" goto :eof


@rem --- all systems go, create the branch
@echo Creating target branch %DESTBRANCH%....
if "%TEST%" == "" svn copy svn://mamedev.org/mame/trunk -r %REVISION% svn://mamedev.org/mame/tags/%DSTBRANCH% -m "MAME %VERSION% tag"


@rem --- export the tree for building
:destexistsfull
@echo Checking out a temp copy....
if exist tempbuild rd /s/q tempbuild
svn export svn://mamedev.org/mame/tags/%DSTBRANCH% tempbuild %NULLOUT%


@rem --- build the debug version
@echo Building debug version....

call ..\trunk\config 32
@if not "%TEST%" == "" echo on
set ARCHOPTS=
set DEBUG=1
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=1
set SYMLEVEL=1
set OSD=
pushd tempbuild
call :performbuild mamed windows\mamed || goto :eof
popd


@rem --- build the release version
@echo Building release version....
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=1
set SYMLEVEL=1
set SUFFIX=
pushd tempbuild
call :performbuild mame windows\mame || goto :eof
popd


@rem --- build the p6-optimized version
:alreadybuilt
@echo Building p6 version....
set ARCHOPTS=-march=pentiumpro
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=1
set SYMLEVEL=1
set SUFFIX=pp
pushd tempbuild
call :performbuild mamepp windows\mamepp || goto :eof
popd


@rem --- build the 64-bit version
@echo Building 64-bit version....
call ..\trunk\config 64
@if not "%TEST%" == "" echo on
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=1
set SYMLEVEL=1
set SUFFIX=
pushd tempbuild
@rem call :performbuild mame64 windows\mame64 || goto :eof
popd


@rem --- now export the actual tree
@echo Checking out a temp copy....
if exist tempexport rd /s/q tempexport
svn export svn://mamedev.org/mame/tags/%DSTBRANCH% tempexport %NULLOUT%


@rem --- copy in the whatsnew file
copy %WHATSNEW% tempexport\whatsnew.txt


@rem --- now package the results
if exist mame.zip del mame.zip
if exist %FINALZIP%.zip del %FINALZIP%.zip
if exist %FINALZIP%.exe del %FINALZIP%.exe
pushd tempexport
@echo Creating 7zip archive....
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\%FINALZIP%.exe * %NULLOUT%
@echo Creating raw ZIP....
7za a -mx=0 -y -r -tzip ..\mame.zip * %NULLOUT%
popd
@echo Creating final ZIP....
7za a -mpass=4 -mfb=255 -y -tzip %FINALZIP%.zip mame.zip %NULLOUT%
del mame.zip


@rem --- now build the official binary
@echo Building official binary....
call :buildbinary mame %FINALBINZIP%.exe

@echo Building official debug binary....
call :buildbinary mamed %FINALBINZIP%_debug.exe

@echo Building official I686 binary....
call :buildbinary mamepp %FINALBINZIP%_i686.exe

@echo Building official 64-bit binary....
call :buildbinary mame64 %FINALBINZIP%_64bit.exe

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
copy ..\tempbuild\%1.exe
copy ..\tempbuild\%1.sym
copy ..\tempbuild\obj\windows\%1\chdman.exe
copy ..\tempbuild\obj\windows\%1\ldverify.exe
copy ..\tempbuild\obj\windows\%1\ldresample.exe
copy ..\tempbuild\obj\windows\%1\romcmp.exe
copy ..\tempbuild\obj\windows\%1\jedutil.exe
copy ..\tempbuild\obj\windows\%1\ledutil.exe
copy ..\tempbuild\obj\windows\%1\unidasm.exe
mkdir docs
copy ..\tempbuild\docs\*.* docs
mkdir hash
copy ..\tempbuild\hash\*.* hash
mkdir hlsl
copy ..\tempbuild\hlsl\*.* hlsl
7za x ..\mamedirs.zip
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\%2
popd

goto :eof



@rem -----------------------------------------------------------
@rem 	Perform a build
@rem 	
@rem    %1 = filename
@rem    %2 = object directory/filename
@rem 	%3..%6 = build options
@rem -----------------------------------------------------------

:performbuild

@rem --- First cleanup old files
if "%RESUME%"=="0" rd /s/q obj\%2
if exist %1.exe del %1.exe
if exist chdman.exe del chdman.exe
if exist ldverify.exe del ldverify.exe
if exist ldresample.exe del ldresample.exe
if exist romcmp.exe del romcmp.exe
if exist jedutil.exe del jedutil.exe
if exist ledutil.exe del ledutil.exe
if exist unidasm.exe del unidasm.exe


@rem --- Do the build
@echo make buildtools %~3 %~4 %~5 %~6
make buildtools %~3 %~4 %~5 %~6 || goto :builderror %1
@echo make all %MAKEPARAMS% %~3 %~4 %~5 %~6
make all %MAKEPARAMS% %~3 %~4 %~5 %~6 || goto :builderror %1
if exist %1.exe strip -s %1.exe


@rem --- Stash the specific binaries
move /y chdman.exe obj\%2\
move /y ldverify.exe obj\%2\
move /y ldresample.exe obj\%2\
move /y romcmp.exe obj\%2\
move /y jedutil.exe obj\%2\
move /y ledutil.exe obj\%2\
move /y unidasm.exe obj\%2

goto :eof



@rem -----------------------------------------------------------
@rem 	Perform validation steps
@rem -----------------------------------------------------------

:dovalidate

@rem --- see if the whatsnew exists
if not exist %WHATSNEW% goto :nowhatsnew
findstr 123456789 %WHATSNEW% %NULLOUT% && goto :junkinwhatsnew


@rem --- make sure all filenames are lowercase
@echo Ensuring all filenames are lowercase....
@rem dir /s /b ..\trunk\src | findstr /v /c:"\\sdl\\" | findstr /v README | findstr "[ABCDEFGHIJKLOPQRSTUVWXYZ]" && goto :uppercasenames


@rem --- verify the version on the top of tree
@echo Verifying version.c....
findstr %VERSION% ..\trunk\src\version.c %NULLOUT% || goto :wrongversion


@rem --- verify that everything is checked in
@echo Verifying that everything is checked in....
svn status %WHATSNEW% | findstr whatsnew %NULLOUT% && goto :notcheckedin
svn status ..\trunk\src | findstr trunk %NULLOUT% && goto :notcheckedin
svn status ..\trunk\makefile | findstr trunk %NULLOUT% && goto :notcheckedin


@rem --- remove all object directories
if not "%RESUME%"=="0" goto :skipremove
@echo Removing old objects...
if exist ..\trunk\obj rd /s/q ..\trunk\obj
:skipremove


@echo Verifying 32-bit Windows debug build....
pushd ..\trunk
call config 32
set ARCHOPTS=
set DEBUG=1
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=0
set OSD=
set PROFILER=
set SYMBOLS=1
set SYMLEVEL=1
set SUFFIX=
call :performbuild windows\mamed || goto :eof
popd

@echo Verifying validation....
..\trunk\mamed -valid %NULLOUT% || goto :validationerror

@echo Verifying 64-bit debug build....
pushd ..\trunk
call config 64
set ARCHOPTS=
set DEBUG=1
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=0
set OSD=
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
@rem call :performbuild windows\mame64d || goto :eof
popd

@echo Verifying 32-bit SDL debug build....
pushd ..\trunk
call config 32
set ARCHOPTS=
set DEBUG=1
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=0
set OSD=sdl
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
call :performbuild sdl\sdlmamed || goto :eof
popd

@echo Verifying 64-bit SDL debug build....
pushd ..\trunk
call config 64
set ARCHOPTS=
set DEBUG=1
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=0
set OSD=sdl
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
@rem call :performbuild sdl\sdlmame64d || goto :eof
popd

@echo Verifying 32-bit Windows release build....
pushd ..\trunk
call config 32
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
call :performbuild windows\mame || goto :eof
popd

@echo Verifying 64-bit Windows release build....
pushd ..\trunk
call config 64
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
@rem call :performbuild windows\mame64 || goto :eof
popd

@echo Verifying 32-bit SDL release build....
pushd ..\trunk
call config 32
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=sdl
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
call :performbuild sdl\sdlmame || goto :eof
popd

@echo Verifying 64-bit SDL release build....
pushd ..\trunk
call config 64
set ARCHOPTS=
set DEBUG=
set GTK_INSTALL_ROOT=
set MAP=
set OPTIMIZE=3
set OSD=sdl
set PROFILER=
set SYMBOLS=
set SYMLEVEL=
set SUFFIX=
@rem call :performbuild sdl\sdlmame64 || goto :eof
popd

set VALIDATED=1
@goto :eof




@rem -----------------------------------------------------------
@rem 	Error messages
@rem -----------------------------------------------------------

:usage
@echo Usage:
@echo   build ^<revision^> ^<primaryver^> ^<unum^> [resume]
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
