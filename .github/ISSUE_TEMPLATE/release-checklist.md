---
name: Release checklist
about: Release preparation task tracking
title: 'Release: MAME 0.xxx'
labels: ''
assignees: ''

---

# Create release branch

- [ ] Pull latest `master` branch, and run `make cleansrc`
- [ ] Check differences, manually clean up anything broken (useful to check `git diff -b` as well as `git diff` to see changes that affect things other than whitespace)
- [ ] Do a full build with `DEBUG=1 TOOLS=1` to ensure changes compile/validate
- [ ] Check software lists against DTD: `for x in hash/*.xml ; do xmllint --noout --valid "$x" ; done`
- [ ] Check software hash files’ XML structure: `for x in hash/*.hsi ; do xmllint --noout "$x" ; done`
- [ ] Commit changes and push to `master` branch
- [ ] Create release branch and push to GitHub
- [ ] Push branch point to `master` branch on GitLab and SourceForge
- [ ] Create new version on MAME Testers with anticipated release date (last Wednesday of following month, 00:00:00Z), marked unreleased

# Run build matrix

In addition to the basic coverage provided by GitHub Actions, MAME needs to be built and tested across a representative spectrum of configurations.

For the following configurations, ensure a build compiles, links and validates, `-listxml` output validates, and basic functionality works:
- [ ] x86-64, MinGW, GCC, debug, SDL OSD, with Qt debugger, without tools
- [ ] x86-64, MinGW, GCC, debug, SDL OSD, with Qt debugger, with tools, `tiny` subtarget
- [ ] x86-64, MinGW, GCC, debug, SDL OSD, with Qt debugger, with tools, `virtual` subtarget
- [ ] x86-64, MinGW, GCC, debug, Win32 OSD, without tools
- [ ] x86-64, MinGW, GCC, debug, Win32 OSD, with tools, `tiny` subtarget
- [ ] x86-64, MinGW, GCC, debug, Win32 OSD, with tools, `virtual` subtarget
- [ ] x86-64, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, without tools
- [ ] x86-64, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, with tools, `tiny` subtarget
- [ ] x86-64, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, with tools, `virtual` subtarget
- [ ] x86-64, MinGW, GCC, non-debug, Win32 OSD, without tools
- [ ] x86-64, MinGW, GCC, non-debug, Win32 OSD, with tools, `tiny` subtarget
- [ ] x86-64, MinGW, GCC, non-debug, Win32 OSD, with tools, `virtual` subtarget

For the following configurations, ensure a build compiles, links and validates, and basic functionality works:
- [ ] i686, MinGW, GCC, debug, SDL OSD, with Qt debugger, without tools
- [ ] i686, MinGW, GCC, debug, SDL OSD, with Qt debugger, with tools, `tiny` subtarget
- [ ] i686, MinGW, GCC, debug, SDL OSD, with Qt debugger, with tools, `virtual` subtarget
- [ ] i686, MinGW, GCC, debug, Win32 OSD, without tools
- [ ] i686, MinGW, GCC, debug, Win32 OSD, with tools, `tiny` subtarget
- [ ] i686, MinGW, GCC, debug, Win32 OSD, with tools, `virtual` subtarget
- [ ] i686, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, without tools
- [ ] i686, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, with tools, `tiny` subtarget
- [ ] i686, MinGW, GCC, non-debug, SDL OSD, with Qt debugger, with tools, `virtual` subtarget
- [ ] i686, MinGW, GCC, non-debug, Win32 OSD, without tools
- [ ] i686, MinGW, GCC, non-debug, Win32 OSD, with tools, `tiny` subtarget
- [ ] i686, MinGW, GCC, non-debug, Win32 OSD, with tools, `virtual` subtarget

For the following configurations, ensure a build compiles, links and validates, `-listxml` output validates, minimaws ORM check passes, and basic functionality works:
- [ ] x86-64, Linux, clang, libc++, debug, without tools
- [ ] x86-64, Linux, clang, libc++, debug, with tools, `tiny` subtarget
- [ ] x86-64, Linux, clang, libc++, debug, with tools, `virtual` subtarget
- [ ] x86-64, Linux, GCC, libstdc++, debug, with tools
- [ ] x86-64, Linux, GCC, libstdc++, debug, without tools, `tiny` subtarget
- [ ] x86-64, Linux, GCC, libstdc++, debug, without tools, `virtual` subtarget
- [ ] x86-64, Linux, clang, libc++, non-debug, without tools
- [ ] x86-64, Linux, clang, libc++, non-debug, with tools, `tiny` subtarget
- [ ] x86-64, Linux, clang, libc++, non-debug, with tools, `virtual` subtarget
- [ ] x86-64, Linux, GCC, libstdc++, non-debug, with tools
- [ ] x86-64, Linux, GCC, libstdc++, non-debug, without tools, `tiny` subtarget
- [ ] x86-64, Linux, GCC, libstdc++, non-debug, without tools, `virtual` subtarget

For the following configurations, ensure a build compiles:
- [ ] i686, Linux, GCC, libstdc++, debug, with tools
- [ ] i686, Linux, GCC, libstdc++, non-debug, with tools

# Generate preliminary release notes

- [ ] Pull latest release branch from `mame` repository and latest `master` branch from `build` repository
- [ ] In `build` repository, run script to scrape commits and pull requests, e.g. `python3 makewn.py -c ../mame -u <user> -o whatsnew/whatsnew_0124.txt`
- [ ] Get `-listxml` output from previous release from a download mirror
- [ ] Generate `-listxml` output with a preliminary build from the release branch
- [ ] In `build` repository, run script to identify added/promoted/renamed/removed machines, e.g. `python3 newdrivers.py mame0123.xml new.xml | tee -a whatsnew/whatsnew_0124.txt`
- [ ] Copy resolved bugs from [MAME Testers change log page](https://mametesters.org/changelog_page.php) to relevant section in release notes
- [ ] Before any editing, commit generated release notes for reference

# Prepare release notes

- [ ] Reconcile added/promoted systems and software with credits in commit messages and pull request descriptions, moving entries to the relevant sections at the top, and sorting correctly
- [ ] Check commit log for `language` folder and list updated translation in the relevant section at the top
- [ ] Sort resolved bugs and edit descriptions
- [ ] Summarise merged pull requests, making verb tense consistent
- [ ] Standardise contributor names
- [ ] Strategically use non-breaking spaces to hopefully avoid line breaks at inopportune points
- [ ] Add anticipated release date to top line
- [ ] Commit changes, push to `master` branch, and let people know it’s ready for proof-reading

# Build release

- [ ] Pull latest release branch
- [ ] In `build` repository, scrape latest commits, do a final check of release notes, commit changes, and push to `master` branch
- [ ] Ensure version is updated in `android-project/app/src/main/AndroidManifest.xml` (two lines), `docs/source/conf.py` (two lines), and `makefile` (two lines)
- [ ] Ensure there are no uncommitted changes on release branch
- [ ] Create signed, annotated tag for release, e.g. `git tag -s -m"MAME 0.124" mame0124`
- [ ] Clone `mame` repository into a clean directory and check out release tag, e.g. `git clone -b mame0124 mame mame-release`
- [ ] In new clone, double-check that `git describe` and `git log -1` show what’s expected
- [ ] Use commands from `build-release.bat` in `build` repository to build 64-bit release binaries, e.g. `(MINGW64=/mingw64 MINGW32= make TARGET=mame TOOLS=1 SEPARATE_BIN=1 PTR64=1 OPTIMIZE=3 SYMBOLS=1 SYMLEVEL=1 REGENIE=1 -j9 ARCHOPTS="-fomit-frame-pointer -fuse-ld=lld" OVERRIDE_AR=llvm-ar && make -f dist.mak PTR64=1 -j5) |& tee ../build64.log`
- [ ] Check build log for anything suspicious
- [ ] Double-check that `build` repository is up-to-date
- [ ] Use `release.sh` from `build` repository to package release, e.g. `bash ../build/release.sh 0124`

# Prepare media

- [ ] Add previous release to `oldrel.php`
- [ ] Copy release notes to `releases` folder
- [ ] Create release announcement post in `posts`
- [ ] Add content from release notes above the “Source changes” heading to release announcement below the `<!--more-->` tag, adding HTML markup for formatting
- [ ] Ensure MAME Testers bug numbers, GitHub pull request and issue numbers, and anything else relevant are linked correctly
- [ ] Use `<tt>` formatting for literal code, command-line options, etc.
- [ ] Write executive summary above the `<!--more-->` tag – aim for at least three paragraphs of content, call out a few interesting or notable changes
- [ ] Put release announcement post in a simple HTML wrapper, preview it, and check for HTML syntax/nesting errors
- [ ] Commit changes to web site pages
- [ ] Convert executive summary to UBB flavours for forum.mamedev.org, forums.bannister.org, and mameworld.info, and markdown flavours for reddit and GitHub, and check previews

# Upload assets for release

- [ ] Push release tag to GitHub, GitLab and SourceForge
- [ ] Push tagged release revision to `master` branch on GitLab and SourceForge
- [ ] Pull latest `master` branch from GitHub, merge release tag, and push to `master` branch on GitHub
- [ ] Delete release branch on GitHub
- [ ] Create draft release on GitHub and upload assets
- [ ] From another browser instance, download assets from draft release
- [ ] Use `7za t` to test integrity of downloaded archives
- [ ] Verify SHA1 and SHA256 digests, e.g. `sha1sum -c < SHA1SUMS` and `sha256sum -c < SHA256SUMS`
- [ ] Set timestamp on assets to midnight UTC for release date, e.g. `TZ=utc touch -t 201909040000 0.213/* 0.213`
- [ ] Upload assets, to SourceForge FRS, e.g. `rsync -avzhc --progress -e ssh 0.124 frs.sf.net:/home/frs/project/mame/mame/`

# Publish release

- [ ] Mark current version as released on MAME Testers, and update with actual release date
- [ ] Publish release on GitHub
- [ ] Push web site changes to `master` branch and wait for static pages to be regenerated
- [ ] Check HTML and RSS pages, ensure a few links work
- [ ] Create forum threads on forum.mamedev.org, forums.bannister.org, and mameworld.info
- [ ] Create reddit posts on [r/MAME](https://www.reddit.com/r/MAME/), [r/emulation](https://www.reddit.com/r/emulation/) and [r/cade](https://www.reddit.com/r/cade/)
- [ ] Create a new, pinned [GitHub Discussion](https://github.com/orgs/mamedev/discussions/categories/announcements) in the Announcements category, and unpin the previous release announcement discussion
- [ ] Update version number in topic on #mame on Libera IRC
- [ ] Update system driver source file list on MAME Testers (use `scripts/xslt/list-system-sources.xslt` to generate the list)
