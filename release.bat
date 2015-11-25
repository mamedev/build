@echo OFF
IF "%1"=="" goto :error
@echo Starting release of MAME %1 ...
@echo Remove old release directories ...
rm -r -f build\release
@echo Creating release directories ...
@mkdir build\release\src 2> nul 
@mkdir build\release\x32\Debug\mame 2> nul 
@mkdir build\release\x32\Release\mame 2> nul 
@mkdir build\release\x64\Release\mame 2> nul 
copy ..\build\whatsnew\whatsnew_%1.txt build\release\. /Y > nul
@echo Copy files MAME 32-bit Debug build ...
call :copyfiles build\mingw-gcc\bin\x32\Debug build\release\x32\Debug\mame mamed mame%1b_debug.exe %1
@echo Copy files MAME 32-bit Release build ...
call :copyfiles build\mingw-gcc\bin\x32\Release build\release\x32\Release\mame mame mame%1b.exe %1
@echo Copy files MAME 64-bit Release build ...
call :copyfiles build\mingw-gcc\bin\x64\Release build\release\x64\Release\mame mame64 mame%1b_64bit.exe %1

@echo Downloading MAME source ....
git clone https://github.com/mamedev/mame.git  --branch mame%1  --depth=1 build\release\src
rm -r -f build\release\src\.git
pushd build\release\src

@echo Creating 7zip source archive....
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\mame%1s.exe * 
@echo Creating raw source ZIP....
7za a -mx=0 -y -r -tzip ..\mame.zip * 
popd

pushd build\release
@echo Creating final source ZIP....
7za a -mpass=4 -mfb=255 -y -tzip mame%1s.zip mame.zip 
del mame.zip
popd 
@echo Finished creating release....
goto :eof

:error
echo Put build number as parameter
goto :eof

:copyfiles
copy %1\%3.exe %2\. /Y > nul
copy %1\%3.sym %2\. /Y > nul
copy ..\build\whatsnew\whatsnew_%5.txt %2\whatsnew.txt /Y > nul
copy %1\chdman.exe %2\. /Y > nul
copy %1\ldverify.exe %2\. /Y > nul
copy %1\ldresample.exe %2\. /Y > nul
copy %1\romcmp.exe %2\. /Y > nul
copy %1\jedutil.exe %2\. /Y > nul
copy %1\ledutil.exe %2\. /Y > nul
copy %1\unidasm.exe %2\. /Y > nul
copy %1\nltool.exe  %2\. /Y > nul
copy %1\nlwav.exe  %2\. /Y > nul
copy %1\castool.exe %2\. /Y > nul
copy %1\floptool.exe %2\. /Y > nul 
copy %1\imgtool.exe %2\. /Y > nul 

7za x ..\build\mamedirs.zip -o%2 >nul

mkdir %2\docs 2> nul
xcopy docs\* %2\docs /s /i > nul
mkdir %2\hash 2> nul
xcopy hash\* %2\hash /s /i > nul 
mkdir %2\hlsl 2> nul
xcopy hlsl\* %2\hlsl /s /i > nul
mkdir %2\nl_examples 2> nul
xcopy  nl_examples\* %2\nl_examples /s /i > nul
mkdir %2\samples 2> nul
xcopy samples\* %2\samples /s /i > nul
mkdir %2\artwork 2> nul
xcopy artwork\* %2\artwork /s /i > nul

strip %2\*.exe
echo Packing %4
pushd %2
7za a -mx=9 -y -r -t7z -sfx7z.sfx ..\..\..\%4 >nul
popd

