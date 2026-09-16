# Play without compiling

Players should not need Sanny Builder or a C# compiler.

## What they run

1. GTA San Andreas PC 1.0 (not Steam 3.0).
2. CLEO 4.4 so CLEO.asi sits next to gta_sa.exe.
3. COPY_TO_GAME.bat — asks for the game folder and copies ready files.

If prebuilt\*.cs exists for a pack, the tools copy that file. They do not compile.

## Maintainer

Compile once with Sanny, put the .cs in prebuilt\, commit it. Players only copy.
