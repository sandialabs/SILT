import h5py
import numpy as np
from PIL import Image

import blkflt

ifile = "example.h5"
image_key = "data"

blkflt.generate_pyramid(ifile, image_key, verbose=True)

with h5py.File(ifile, "r") as h5_image:
    output_original = h5_image[image_key].size
    print('original size: ', output_original)
    print(h5_image["pyramid"].keys())
    for key in h5_image["pyramid"].keys():
        print(key + " size: " + str(h5_image["pyramid"][key].size))
