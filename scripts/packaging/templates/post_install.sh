#!/bin/bash
echo "Running post-installation script..."

BASE_CONDA_PATH=$(conda info --base)

source "$BASE_CONDA_PATH/etc/profile.d/conda.sh"
conda activate "$PREFIX"

tar -xzvf silt.tar.gz
rm silt.tar.gz

# Check if the environment is activated
if [ $? -eq 0 ]; then
    echo "Conda environment activated successfully."

    # Access the directory included in temp_extra_files
    if [ -d "$PREFIX/silt" ]; then
        echo "Found silt directory"
        ls "$PREFIX/silt"
        # Perform operations on the directory
    else
        echo "silt directory not found"
        exit 1
    fi

else
    echo "Failed to activate Conda environment."
    exit 1
fi

# Uncomment the following when integrating segment-anything model:
# - also remember to uncomment the torch dependencies in the env .yaml file
# download sam ckpts

# install segment anything for segmentation
# pip install git+https://github.com/facebookresearch/segment-anything.git

pip install ./silt

if [ $? -eq 0 ]; then
    echo "pip installed silt successfully"
else
    echo "FAILED to pip install silt"
    exit 1
fi

echo "Done with post-installation script"
