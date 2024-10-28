@echo off
REM Please provide a command line argument with a conda env name that has constructor installed.

set PKG_DIR=pkg-output
set TARBALL_NAME=silt-pkg

set arg1=%1
set arg2=%2

set curr_script_dir=%~dp0


@ REM Change to main repo directory
cd /d %curr_script_dir%

if "%arg1%" == "constructor" (

    echo "Constructing Installer"

    call .\scripts\windows\construct_installer.bat %arg2%

) else if "%arg1%" == "tarball_with_tests" (

    echo "Tarballing installation with tests"
    call .\scripts\windows\make_tarball_with_tests.bat

) else (
    echo "Invalid option: %arg1%. Either specify 'constructor' or 'tarball_with_tests' as the first cmd line argument."
)
exit


