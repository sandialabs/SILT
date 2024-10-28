@echo off
REM cd: C:\Users\<user>\AppData\Local\silt\conda-meta
REM "PREFIX: C:\Users\<user>\AppData\Local\silt"

cd /d %PREFIX%

call ".\Lib\venv\scripts\nt\activate.bat" .

mkdir ".\silt"

echo Unzipping "%PREFIX%\silt.tar.gz" into "%PREFIX%\silt"
tar -xf ".\silt.tar.gz" -C ".\silt"

REM Uncomment the following when integrating segment-anything model (download_sam_ckpt.bat is unfinished):

REM pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118  @REM too big to include in env.yaml
REM call "%PREFIX%\download_sam_ckpt.bat"
REM pip install git+https://github.com/facebookresearch/segment-anything.git

pip install ".\silt"

IF %ERRORLEVEL% EQU 0 (
    echo pip installed silt successfully
) ELSE (
    echo FAILED to pip install silt
    exit /b 1
)

call ".\run_tests.bat"

del silt.tar.gz

echo Done with post-installation script
