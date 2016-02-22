@echo off
for /f "delims=" %%a in ('git -C ../mame describe --tags --abbrev^=0') do @set LAST_TAG=%%a
git -C ../mame log --reverse %LAST_TAG%..HEAD > temp.log
makewn temp.log > whatsnew.txt