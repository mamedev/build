@echo Building x64 release version....

make TARGET=mame USE_SDL3=1 TOOLS=1 SEPARATE_BIN=1 PTR64=1 OPTIMIZE=3 SYMBOLS=1 SYMLEVEL=1 REGENIE=1 OVERRIDE_CC=clang OVERRIDE_CXX=clang++ OVERRIDE_AR=llvm-ar -j9 ARCHOPTS="-fuse-ld=lld -march=x86-64-v2 -fomit-frame-pointer"
make -f dist.mak PTR64=1 -j5

@echo Building arm64 release version....

make TARGET=mame USE_SDL3=1 TOOLS=1 SEPARATE_BIN=1 PTR64=1 OPTIMIZE=3 SYMBOLS=1 SYMLEVEL=1 REGENIE=1 OVERRIDE_CC=clang OVERRIDE_CXX=clang++ OVERRIDE_AR=llvm-ar -j9 ARCHOPTS="-fuse-ld=lld -march=armv8.2-a"
make -f dist.mak PTR64=1 -j5
