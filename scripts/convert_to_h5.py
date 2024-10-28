#################################################################
# Sandia National Labs
# Date: 09-22-2020
# Author: Kelsie Larson
# Department: 05346
# Contact: kmlarso@sandia.gov
#
# Sample script for converting a PIL-readable image (tif,
# jpeg, png, etc.) to H5-formatted file.
#################################################################

from PIL import Image
import numpy as np
import h5py
import sys
import matplotlib.pyplot as plt

# Increases PIL default image size
Image.MAX_IMAGE_PIXELS = 60000 * 60000

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

    # Open the image
    img = Image.open(input_file)

    # Convert to greyscale (not necessary)
    #if img.mode == 'RGB':
    #    img = img.convert('L')

    # Print the image array shape
    print ("Image shape: {}".format(np.array(img).shape))
    
    # Write the image data to an H5 formatted file
    # The data is written to a dataset called "data"
    # with an attribute "color_mode".
    with h5py.File(output_file, 'w') as fid:
        dataset = fid.create_dataset("data", data=np.array(img))
        dataset.attrs['color_mode'] = img.mode
        
    
def usage(caller):
    """Usage statement"""
    print ("")
    print ("USAGE:")
    print ("{} <input_image_file> <output_image_file>".format(caller))
    print ("  <input_image_file> (str):    path to input image file")
    print ("  <output_image_file> (str):   path to output h5 file")
    print ("")

    
if __name__ == "__main__":
    main(sys.argv)
    
