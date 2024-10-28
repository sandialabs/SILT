@echo off

set script_dir=%~dp0
echo "Running Tests"

call conda run -p %script_dir% pytest %script_dir%silt/test

@if %ERRORLEVEL% neq 0 (
    @echo "Error: Running Tests Failed."
    @echo "Please move this file back to the original folder and try again.
)

timeout 60
exit /b 1
