#!/bin/bash
echo "Running pre-installation script..."

# echo "Please make sure segment-anything ckpts were already downloaded before tarring, or else tar again"

# SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# echo $PREFIX
# echo $SCRIPT_DIR
# echo $CONDA_PREFIX
# echo $RECIPE_DIR  # none shown

# Set current directory to this file's parent dir
cd "$(dirname "$0")"

# zip -r silt.zip ../../silt
tar -zcvf silt.tar.gz ../../../silt

# windows
# tar.exe -a -cf silt.zip srcDir
# SET SCRIPT_DIR=%~dp0
# SET OUTPUT_ZIP=%SCRIPT_DIR%target_directory.zip
# powershell -Command "Compress-Archive -Path '%TARGET_DIR%\*' -DestinationPath '%OUTPUT_ZIP%'"

echo "Done tarring silt/ directory"
echo "Done with pre-installation script"
