#!/bin/sh

copyfiles()
{
	cp "${1}/${3}.sym" "${2}/"
	cp "../build/whatsnew/whatsnew_${5}.txt" "${2}/whatsnew.txt"

	for dir in artwork bgfx hlsl plugins samples ; do
		mkdir -p "${2}/${dir}"
		cp -r ${dir}/* "${2}/${dir}/"
	done

	echo "Packing ${4}"
	pushd "${2}"
	7za a -mx=9 -y -r -t7z -sfx7z.sfx "../../../${4}"
	popd
}

if [ "$#" -ne 1 ] ; then
	echo "Put build number as parameter"
	exit 1
fi

echo "Starting release of MAME ${1} ..."

echo "Remove old release directories ..."
rm -rf build/release/src
rm -f build/release/*.zip build/release/*.exe build/release/*.xml build/release/*.txt build/release/*SUMS

echo "Creating release directories ..."
mkdir -p "build/release/src"
mkdir -p "build/release/x64/Release/mame"
cp "../build/whatsnew/whatsnew_${1}.txt" "build/release/"

echo "Copy files MAME 64-bit Release build ..."
copyfiles "build/mingw-gcc/bin/x64/Release" "build/release/x64/Release/mame" "mame64" "mame${1}b_64bit.exe" "${1}"

echo "Cloning MAME source ..."
git clone . --branch "mame${1}" --depth=1 "build/release/src"
rm -rf "build/release/src/.git"

echo "Creating 7zip source archive ..."
pushd "build/release/src"
7za a -mx=9 -y -r -t7z -sfx7z.sfx "../mame${1}s.exe" *
popd

echo "Creating XML system list ..."
"build/mingw-gcc/bin/x64/Release/mame64.exe" -listxml > "mame${1}.xml"
7za a -mpass=4 -mfb=255 -y -tzip "build/release/mame${1}lx.zip" "mame${1}.xml"

echo "Calculating digests ..."
pushd "build/release"
sha1sum "mame${1}b_64bit.exe" "mame${1}lx.zip" "mame${1}s.exe" "whatsnew_${1}.txt" > SHA1SUMS
sha256sum "mame${1}b_64bit.exe" "mame${1}lx.zip" "mame${1}s.exe" "whatsnew_${1}.txt" > SHA256SUMS
popd

echo "Finished creating release ..."
