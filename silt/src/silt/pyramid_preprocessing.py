import h5py
import logging
import numpy as np
import sys

from PyQt5.QtCore import pyqtSignal
from scipy.ndimage import gaussian_filter

def generate_pyramid(file_path: str, 
                     image_key: str = "data", 
                     downsample = 2,
                     sigma = None,
                     radius = 3,
                     blocksize = 2**12,
                     max_length = 1024,
                     progress_callback: pyqtSignal = None,
                     no_pyramid: bool = False):
    """
    Given a path to an h5 file, generates an image pyramid in the group "pyramid" within the
    same file.
    """
    if sigma is None:
        sigma = 2 * downsample / 6.0

    with h5py.File(file_path, "a") as h5_image:
        # Find the length of the longest side
        length = max(h5_image[image_key].shape)

        # Determine number of pyramid levels, based on size of original image
        # If the user has selected to not generate the pyramid, keep the number of levels at 0.
        levels = 0
        if not no_pyramid:
            while length > max_length:
                length = length // downsample
                levels += 1

        h5_image.attrs["max_level"] = levels

        if levels == 0:
            # If there's only one level, simply grab the min and max instead of iterating
            h5_image.attrs["image_min"] = np.min(h5_image[image_key])
            h5_image.attrs["image_max"] = np.max(h5_image[image_key])

            return

        if "pyramid" in h5_image:
            logging.info("Pyramid already exists")
            # del h5_image["pyramid"] # useful for debugging
            return

        h5_image.create_group("pyramid")

        for i in range(0, levels):
            logging.info(f"Pyramid level: {i+1}/{levels}")

            if i == 0:
                # Generate initial level from original image, calculating min and max image values as well
                image_min, image_max = block_filter_to_pyramid(
                    input_image=h5_image[image_key],
                    output_destination=h5_image["pyramid"],
                    target=f"{1}",
                    blocksize=blocksize,
                    downsample=downsample,
                    sigma=sigma,
                    radius=radius,
                    progress_callback=progress_callback,
                )

                h5_image.attrs["image_min"] = image_min
                h5_image.attrs["image_max"] = image_max
            else:
                block_filter_to_pyramid(
                    input_image=h5_image["pyramid"][f"{i}"],
                    output_destination=h5_image["pyramid"],
                    target=f"{i+1}",
                    blocksize=blocksize,
                    downsample=downsample,
                    sigma=sigma,
                    radius=radius,
                    progress_callback=progress_callback,
                )


def block_filter_to_pyramid(
    input_image: h5py.Dataset,
    output_destination: h5py.Group,
    target: str,
    blocksize: int=64,
    downsample: int=2,
    sigma: int=None,
    radius: int=3,
    progress_callback: pyqtSignal = None,
):
    """
    Generates a level of the image pyramid.

    Given an input image and an output destination/target, downsamples the image 
    and saves to the group.
    """
    
    dim = len(input_image.shape)
    if dim > 3 or dim < 2:
        sys.exit("Image not shaped properly: ", dim)

    M, N = input_image.shape[:2]

    # Determine new image size
    if M % 2 == 0:
        M_output = M // 2
    else:
        M_output = M // 2 + 1
    if N % 2 == 0:
        N_output = N // 2
    else:
        N_output = N // 2 + 1

    if dim == 3:
        target_shape = (M_output, N_output, input_image.shape[2])
    else:
        target_shape = (M_output, N_output)

    output_destination.create_dataset(
        target, shape=target_shape, dtype=input_image.dtype
    )

    image_min = None
    image_max = None

    index = 0
    total = int(np.ceil(M / blocksize) * np.ceil(N / blocksize))

    if progress_callback is not None:
        progress_callback.emit((index,total))

    for row in range(0, M, blocksize):
        for col in range(0, N, blocksize):

            m_low = radius + min(row - radius, 0)
            m_hgh = max(min(M - (row + blocksize + radius), radius), 0)
            n_low = radius + min(col - radius, 0)
            n_hgh = max(min(N - (col + blocksize + radius), radius), 0)

            # If three channels (color)
            if dim == 3:
                # Slice with buffer
                input_slice = input_image[
                    row - m_low : row + blocksize + m_hgh,
                    col - n_low : col + blocksize + n_hgh,
                    :,
                ]

                rval = gaussian_filter(
                    input_slice,
                    sigma=(sigma, sigma, 0),
                    radius=radius,
                )

                rval = rval[
                    m_low : rval.shape[0] - m_hgh, 
                    n_low : rval.shape[1] - n_hgh, 
                    :
                ]

                rval = rval[::downsample, ::downsample]

                output_destination[target][
                    row // downsample : row // downsample + rval.shape[0],
                    col // downsample : col // downsample + rval.shape[1],
                    :,
                ] = rval
            # Two channels (greyscale)
            else:
                # Slice with buffer
                input_slice = input_image[
                    row - m_low : row + blocksize + m_hgh,
                    col - n_low : col + blocksize + n_hgh,
                ]

                rval = gaussian_filter(
                    input_slice,
                    sigma=sigma,
                    radius=radius,
                )

                rval = rval[
                    m_low : rval.shape[0] - m_hgh, 
                    n_low : rval.shape[1] - n_hgh
                ]

                rval = rval[::downsample, ::downsample]

                output_destination[target][
                    row // downsample : row // downsample + rval.shape[0],
                    col // downsample : col // downsample + rval.shape[1],
                ] = rval

            index += 1

            if progress_callback is not None:
                progress_callback.emit((index,total))

            logging.info(f"Block: {index}/{total}")

            # Find min and max
            min_val = np.min(input_slice)
            max_val = np.max(input_slice)

            if image_min == None or image_max == None:
                image_min = min_val
                image_max = max_val
            else:
                image_min = min(image_min, min_val)
                image_max = max(image_max, max_val)

    return image_min, image_max


def usage(caller):
    """Usage statement"""
    print("")
    print("USAGE:")
    print("{} <image_path> <image_key>".format(caller))
    print("  <image_path> (str):    path to the input h5 file")
    print("  <image_key> (str):   key of the original image data in the h5 file.")
    print("")


if __name__ == "__main__":
    """
    Generate an image pyramid within a given h5 file.
    The pyramid will be generated within a group named "pyramid" in the same h5 file.
    Each level of the pyramid is labeled with it's level, i.e. '1', '2', etc.
    """
    if len(sys.argv) <= 2 or len(sys.argv) > 4:
        print("INPUT ERROR.")
        usage(sys.argv[0])

    file_path = sys.argv[1]
    image_key = sys.argv[2]

    generate_pyramid(file_path, image_key)
