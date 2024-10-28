import numpy as np
import matplotlib.pyplot as plt

plt.ion()

from skimage import data
from skimage.transform import pyramid_gaussian
from skimage.color import rgb2gray
import h5py

from scipy.ndimage import gaussian_filter

import blkflt

ifile = "astronaut.h5"
ofile = "output.h5"
downscale = 2
sigma = 2 * downscale / 6.0
radius = 3

image = rgb2gray(data.astronaut())
with h5py.File(ifile, "w") as h5:
    h5["image"] = image

with h5py.File(ifile, "r") as h5_image:
    blkflt.block_filter_to_file(h5_image["image"], ofile, blocksize=64, sigma=sigma, radius=radius)

with h5py.File(ifile, "r") as h5_image:
    output = blkflt.block_filter(h5_image["image"], sigma=sigma, blocksize=64, radius=radius)

output = output[::downscale, ::downscale]


#pyramid = tuple(pyramid_gaussian(image, downscale=2, max_layer=1))
output_full = gaussian_filter(image, sigma=sigma, radius=radius)[
    ::downscale, ::downscale
]

with h5py.File(ofile, "r") as h5_image:
    output_file = h5_image["image"][()]

dval = output_file - output_full
print(np.max(abs(dval)) / np.max(abs(output)))

dval = output_file - output
print(np.max(abs(dval)) / np.max(abs(output)))

#plt.close("all")
#fig = plt.figure()
#plt.subplot(1, 3, 1)
#plt.imshow(output_full)
#plt.subplot(1, 3, 2)
#plt.imshow(output_file)
#plt.subplot(1, 3, 3)
#plt.imshow(dval)
#
#
