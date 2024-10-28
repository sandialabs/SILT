@echo off
setlocal enabledelayedexpansion

if not defined TARBALL_NAME (
    @echo "Please define the TARBALL_NAME and PKG_DIR env variables"
    exit /b 1
)

if not defined PKG_DIR (
    @echo "Please define the TARBALL_NAME and PKG_DIR env variables"
    exit /b 1
)

:: Initialize variables
set curr_script_dir=%~dp0

@ REM Change to main repo directory
cd /d %curr_script_dir%..\..

set tmpDir=%TEMP%\%TARBALL_NAME%
set pkgDir=%PKG_DIR%
set suffix=
set tarballName=%TARBALL_NAME%

:: Parse command line arguments
:parse_args
if "%~1"=="" goto args_parsed
if "%~1"=="-p" (
    set pkgDir=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-s" (
    set suffix=%~2
    shift
    shift
    goto parse_args
)
if "%~1"=="-t" (
    set tarballName=%~2
    shift
    shift
    goto parse_args
)
shift
goto parse_args

:args_parsed

:: Update variables if suffix is provided
if not "%suffix%"=="" (
    set tmpDir=%tmpDir%-%suffix%
    set pkgDir=%pkgDir%-%suffix%
    set tarballName=%tarballName%-%suffix%
)
:: Remove and recreate temporary directory
if exist "%tmpDir%" rd /s /q "%tmpDir%"
mkdir "%tmpDir%"
mkdir "%tmpDir%\scripts"
mkdir "%tmpDir%\test"

:: Copy files to temporary directory

for %%f in (%pkgDir%\silt*.exe) do (
    xcopy %%f "%tmpDir%\"
)
xcopy "Makefile" "%tmpDir%\"
xcopy /s "silt\test" "%tmpDir%\test"
xcopy "scripts\source_conda.sh" "%tmpDir%\scripts\"

del "%tarballName%.tar.gz" 2>nul

:: Create tarball (requires tar for Windows)
:: You can use a tool like 7-Zip if tar is not available
for %%F in ("%tmpDir%") do set "baseName=%%~nxF"

@REM tar -C "%TEMP%" --exclude='test\__pycache__' --exclude='test\.pytest_cache' -cvzf "%tarballName%.tar.gz" %baseName%
tar -C "%tmpDir%" --exclude='test\__pycache__' --exclude='test\.pytest_cache' -cvzf "%tarballName%.tar.gz" .

:: Remove temporary directory
if exist "%tmpDir%" rd /s /q "%tmpDir%"

endlocal

