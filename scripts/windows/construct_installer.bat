@echo off
REM Please provide a command line argument with a conda env name that has constructor installed.

set curr_script_dir=%~dp0

@ REM Change to main repo directory
cd /d %curr_script_dir%..\..


if not defined PKG_DIR (
    @echo "Please define the PKG_DIR env variable"
    exit /b 1
)

set PKG_DIR=.\%PKG_DIR%
del /s /f /q  %PKG_DIR%
mkdir %PKG_DIR% 2>nul

set env_name=%1

if "%env_name%"=="" (
    echo "No command line env_name specified, using 'constructor' as default"
    set env_name=constructor
)

echo Activating conda environment: %env_name%

@REM doesn't activate env properly if one is already on, so deactivate
call conda deactivate
call activate %env_name%

if %ERRORLEVEL% neq 0 (
    echo "Error: Couldn't activate conda environment %env_name%."
    echo "Please provide a command line argument with a conda env name that has constructor installed. (default: constructor)"
    call conda env list
    call conda deactivate
    exit /b 1
)

call scripts\packaging\templates\pre_install.bat

call python scripts\packaging\make_constructor_package.py -O %PKG_DIR%

call conda deactivate
if %ERRORLEVEL% neq 0 (
    echo "Error: Couldn't build installer. make_constructor_package.py failed."
    exit /b 1
)


