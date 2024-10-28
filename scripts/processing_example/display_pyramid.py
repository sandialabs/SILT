import h5py
import numpy as np
from PIL import Image

"""
Saves all levels of image pyramid to seperate jpegs
"""

ifile = "example.h5"
image_key = "data"

with h5py.File(ifile, "r") as h5_image:
    output_original = h5_image[image_key].size
    print('original size: ', output_original)
    print(h5_image["pyramid"].keys())
    for key in h5_image["pyramid"].keys():
        print(key + " size: " + str(h5_image["pyramid"][key].size))

        # Save to disk
        im = Image.fromarray(h5_image["pyramid"][key][()]).convert('RGB')
        im.save(f"{key}.jpeg")
