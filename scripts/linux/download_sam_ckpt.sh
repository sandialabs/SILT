#!/bin/bash

parent_path=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )

echo $parent_path

ckpt_folder=$parent_path/../../silt/src/silt/segmentation/sam_ckpts/

echo $ckpt_folder

# medium sized: l model
ckpt_url=https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth

# largest: h model
# https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
# smallest: b model
# https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth

wget $ckpt_url -P $ckpt_folder
