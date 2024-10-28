setlocal

@SET SCRIPT_DIR=%~dp0
@SET TARGET_DIR=%SCRIPT_DIR%..\..\..\silt
@SET OUTPUT_ZIP=%SCRIPT_DIR%silt.tar.gz

@echo Zipping %TARGET_DIR% directory into %OUTPUT_ZIP%

@REM Change current working directory to parent dir of this script
@REM set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

@REM Delete zip if one already exists
del %OUTPUT_ZIP% 2>nul

@REM Create zip file
@REM powershell -Command "Compress-Archive -Path '%TARGET_DIR%\*' -DestinationPath '%OUTPUT_ZIP%'"

tar -cvf %OUTPUT_ZIP% -C %TARGET_DIR% .

endlocal