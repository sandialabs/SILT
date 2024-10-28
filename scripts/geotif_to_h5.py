#################################################################
# Sandia National Labs
# Date: 10-22-2021
# Author: Kelsie Larson
# Department: 6321
# Contact: kmlarso@sandia.gov
#
# Sample script for converting a geotif image to a H5-formatted
# file.  Call from command line using:
# python geotif_to_h5.py <input_file.tif> <output_file.h5>
#################################################################

import rasterio as rio
import h5py
import numpy as np
import sys

def main(argv):
    """Main program to convert a PIL-readable image to H5 file."""
    if len(argv) == 1:
        usage(argv[0])
        sys.exit()
    
    elif len(argv) > 3:
        print ("INPUT ERROR.")
        usage(argv[0])
        sys.exit()

    # Get the input arguments from the command line
    input_file = argv[1]
    output_file = argv[2]

    # Open the image file
    fid = rio.open(input_file)
    
    # Get the geo transform
    geo_transform = np.array(fid.transform).reshape((3, 3))
    
    # Get the image
    img = fid.read()
    color_mode = "L"
    if len(img.shape) > 2:
        img = np.moveaxis(img, 0, -1)
        if img.shape[-1] == 3:
            color_mode = "RGB"
        elif img.shape[-1] == 1:
            img = img.reshape(img.shape[:2])
        else:
            exception_str = ("Incorrect number of image channels. "
                             f"Inputted image has {img.shape[-1]} "
                             "channels. Acceptable values are 1 or "
                             "3 channels.")
            raise InputError(exception_str, "ERROR: Input")
    
    # Print the image array shape
    print ("Image shape: {}".format(np.array(img).shape))

    # Write the image data to an H5 formatted file
    # The data is written to a dataset called "data"
    # with an attribute "color_mode".
    with h5py.File(output_file, 'w') as fid:
        dataset_img = fid.create_dataset("data", data=np.array(img))
        dataset_img.attrs['color_mode'] = color_mode
        dataset_geo = fid.create_dataset("geotransform", data=geo_transform)
        dataset_geo.attrs['units'] = "decimal degrees"


def usage(caller):
    """Usage statement"""
    print ("")
    print ("USAGE:")
    print ("{} <input_image_file> <output_image_file>".format(caller))
    print ("  <input_image_file> (str):    path to input image file")
    print ("  <output_image_file> (str):   path to output h5 file")
    print ("")


class InputError(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

if __name__ == "__main__":
    main(sys.argv)
