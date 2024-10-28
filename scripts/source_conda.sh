#!/bin/bash

if which conda 2>&1 1>/dev/null
then
    conda_sh_path=$(conda info --base)/etc/profile.d/conda.sh
else
    conda_sh_path=${HOME}/anaconda3/etc/profile.d/conda.sh
fi

. ${conda_sh_path}; conda activate ${ENV_NAME}
