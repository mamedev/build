---
name: Pre-release smoke test
about: Release preparation task tracking
title: 'Smoke test: MAME 0.xxx pre-release'
labels: ''
assignees: ''

---

# Windows arm64 (clang, UCRT, Win32 OSD, Debug)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `bgfx`, `opengl`, `gdi`)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametinyd.exe` and `mamevirtuald.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows arm64 (clang, UCRT, Win32 OSD, Release)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `bgfx`, `opengl`, `gdi`)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametiny.exe` and `mamevirtual.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x64 (GCC, MSVCRT, Win32 OSD, Debug)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `bgfx`, `opengl`, `gdi`)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametinyd.exe` and `mamevirtuald.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x64 (GCC, MSVCRT, Win32 OSD, Release)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `bgfx`, `opengl`, `gdi`)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametiny.exe` and `mamevirtual.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x64 (GCC, MSVCRT, SDL OSD, Debug)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (requires `-enable_touch` – double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`sdl`, `wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`bgfx`, `opengl`, `accel`, `soft`)
- [ ] All `-keyboardprovider` modules (`sdl`, `dinput`)
- [ ] All `-mouseprovider` modules (`sdl`)
- [ ] All `-joystickprovider` modules (`sdl`, `winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`sdlmametinyd.exe` and `sdlmamevirtuald.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x64 (GCC, MSVCRT, SDL OSD, Release)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (requires `-enable_touch` – double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`sdl`, `wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`bgfx`, `opengl`, `accel`, `soft`)
- [ ] All `-keyboardprovider` modules (`sdl`, `dinput`)
- [ ] All `-mouseprovider` modules (`sdl`)
- [ ] All `-joystickprovider` modules (`sdl`, `winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`sdlmametiny.exe` and `sdlmamevirtual.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x86 (GCC, MSVCRT, Win32 OSD, Debug)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `opengl`, `gdi`, but not `bgfx` as ImGui has assertion failures with x87 maths)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametinyd.exe` and `mamevirtuald.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x86 (GCC, MSVCRT, Win32 OSD, Release)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`d3d`, `bgfx`, `opengl`, `gdi`)
- [ ] All `-keyboardprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-mouseprovider` modules (`rawinput`, `dinput`, `win32`)
- [ ] All `-joystickprovider` modules (`winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`mametiny.exe` and `mamevirtual.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x86 (GCC, MSVCRT, SDL OSD, Debug)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (requires `-enable_touch` – double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`sdl`, `wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`opengl`, `accel`, `soft`, but not `bgfx` as ImGui has assertion failures with x87 maths)
- [ ] All `-keyboardprovider` modules (`sdl`, `dinput`)
- [ ] All `-mouseprovider` modules (`sdl`)
- [ ] All `-joystickprovider` modules (`sdl`, `winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`sdlmametinyd.exe` and `sdlmamevirtuald.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)

# Windows x86 (GCC, MSVCRT, SDL OSD, Release)

- [ ] System and software selection menus, mouse-driven and using keyboard/game controller (accessed by starting MAME without specifying a system name)
- [ ] Basic internal UI functionality (menus, slider, clickable DIP switches, etc.)
- [ ] Selecting media from the File Manager menu works, using both loose files and software lists
- [ ] Touch input (requires `-enable_touch` – double-tap to select, vertical swipe to scroll, horizontal swipe to adjust, etc.)
- [ ] Interactive artwork
- [ ] Basic debugger functionality, mouse-driven and command interface
- [ ] Lua scripting functionality (e.g. autofire plugin, input macro plugin, script-dependent internal layouts)
- [ ] Recompiling CPUs (e.g. MIPS III, PowerPC, Hyperstone E1), including stepping in debugger
- [ ] All `-sound` modules (`sdl`, `wasapi`, `xaudio2`, `portaudio`)
- [ ] All `-video` modules (`bgfx`, `opengl`, `accel`, `soft`)
- [ ] All `-keyboardprovider` modules (`sdl`, `dinput`)
- [ ] All `-mouseprovider` modules (`sdl`)
- [ ] All `-joystickprovider` modules (`sdl`, `winhybrid`, `xinput`, `dinput`)
- [ ] Subset builds (`sdlmametiny.exe` and `sdlmamevirtual.exe`) more or less work
- [ ] CHD CD read (e.g. run a Konami GV game)
- [ ] CHD hard disk read (e.g. boot an OS on a computer)
- [ ] CHD hard disk write (e.g. boot an OS on a computer, modify a file, and test that the modification persists after exiting and starting MAME again)
- [ ] Floppy disk functionality (e.g. run a home computer game from a floppy)
