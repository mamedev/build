@echo Building 32-bit release version....
 
make TARGET=mame TOOLS=1 SEPARATE_BIN=1 PTR64=0 OPTIMIZE=3 SYMBOLS=1 SYMLEVEL=1 REGENIE=1 -j9 ARCHOPTS="-fuse-ld=lld -msse2 -mfpmath=sse"
make -f dist.mak PTR64=0

@echo Building 64-bit release version....
 
make TARGET=mame TOOLS=1 SEPARATE_BIN=1 PTR64=1 OPTIMIZE=3 SYMBOLS=1 SYMLEVEL=1 REGENIE=1 -j9 ARCHOPTS="-fomit-frame-pointer -fuse-ld=lld" OVERRIDE_AR=llvm-ar
make -f dist.mak PTR64=1
