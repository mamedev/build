@echo off

@rem
@rem This file is intended to be called "config.cmd" and should live in the root
@rem directory next to the MAME makefile. Copy this template there and modify
@rem the directory paths and environment variables below to suit your preferences.
@rem Then call config.cmd with one of the following parameters:
@rem
@rem    config 32       Set up for 32-bit mingw builds
@rem    config 64       Set up for 64-bit mingw builds
@rem    config v32      Set up for 32-bit Visual Studio builds
@rem    config v64      Set up for 64-bit Visual Studio builds
@rem

@rem Ensure we have a valid target
if not "%1"=="32" if not "%1"=="64" if not "%1"=="v32" if not "%1"=="v64" echo Error, unknown target. Must be '32', '64', 'v32', or 'v64'.

@rem Configure this to point to the directory holding the mingw64-w32/mingw64-w64 directories
set MINGWPATH=d:\tools

@rem Cofnigure this to point to the base of the GTK drop
@rem set GTK_INSTALL_ROOT=d:\tools\gtk+-bundle_2.20.0-20100406_win32
set GTK_INSTALL_ROOT=

@rem The path to MSVC is derived from VS90COMNTOOLS which should already be present
set VCPATH=%VS90COMNTOOLS%\..\..\vc

@rem The path to the DirectX SDK (needed for MSVC)
set DXSDKPATH=d:\tools\dxsdk

@rem Configure this to point to your SVN directory
set SVNPATH=d:\tools\svn-win32-1.4.6\bin

@rem Configure this to point to your editor's binary path
set EDITORPATH=%ProgramFiles(x86)%\Metrowerks\Codewarrior\bin

@rem Configure this to point to any other paths you wish to include
set OTHERPATH=d:\tools\7za;c:\perl64\bin

@rem Reset variables to their default value (I like to have profiles and maps)
set PROFILER=1
set SYMBOLS=1
set SYMLEVEL=1
set MAP=
set PATH=%BASEPATH%
set INCLUDE=
set LIB=
set LIBPATH=
set MSVC_BUILD=

@rem ----------------------> END USER CONFIGURATION <---------------------------------

@rem Create a BASEPATH pointing to all the non-compiler paths
set BASEPATH=%EDITORPATH%;%SVNPATH%;%OTHERPATH%;%WINDIR%\system32;%WINDIR%

@rem 32-bit mingw case: gray on black
if "%1"=="32" color 07 & set PATH=%MINGWPATH%\mingw64-w32\bin;%MINGWPATH%\mingw64-w32\opt\bin;%PATH%;%GTK_INSTALL_ROOT%\bin& echo Configured for mingw64 32-bit

@rem 64-bit mingw case: gray on blue
if "%1"=="64" color 17 & set PATH=%MINGWPATH%\mingw64-w64\bin;%MINGWPATH%\mingw64-w64\opt\bin;%PATH%;%GTK_INSTALL_ROOT%\bin& echo Configured for mingw64 64-bit

@rem 32-bit VC case: yellow on black
if "%1"=="v32" color 0e & set MSVC_BUILD=1 & call "%VCPATH%\vcvarsall.bat" x86
if "%1"=="v32" set INCLUDE=%INCLUDE%;%DXSDKPATH%\include& set LIB=%DXSDKPATH%\lib\x86;%LIB%& set PATH=%PATH%;%MINGWPATH%\mingw64-w32\bin;%MINGWPATH%\mingw64-w32\opt\bin

@rem 64-bit VC case: yellow on blue
if "%1"=="v64" color 1e & set MSVC_BUILD=1 & call "%VCPATH%\vcvarsall.bat" amd64
if "%1"=="v64" set INCLUDE=%INCLUDE%;%DXSDKPATH%\include& set LIB=%DXSDKPATH%\lib\x64;%LIB%& set PATH=%PATH%;%MINGWPATH%\mingw64-w64\bin;%MINGWPATH%\mingw64-w64\opt\bin
