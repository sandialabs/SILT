@echo off
REM Do not move this file from this directory or else silt program will not launch
set script_dir=%~dp0
echo "Note: Closing this window will close the silt application as well."
call conda run -p %script_dir% silt

@if %ERRORLEVEL% neq 0 (
    @echo "Error: Couldn't launch silt application"
    @echo "Please move this file back to the original folder and try again.
    timeout 300
    exit /b 1
)