import h5py
import logging
import numpy as np

from scipy.ndimage import gaussian_filter

logging.basicConfig(level=logging.INFO)

def block_filter(image, blocksize=64, sigma=None, radius=None):
    n = radius
    output = np.zeros(image.shape, dtype=image.dtype)
    M, N = image.shape
    for row in range(0, M, blocksize):
        for col in range(0, N, blocksize):
            m_low = n + min(row - n, 0)
            m_hgh = max(min(M - (row + blocksize + n), n), 0)
            n_low = n + min(col - n, 0)
            n_hgh = max(min(N - (col + blocksize + n), n), 0)

            input_image = image[
                row - m_low : row + blocksize + m_hgh,
                col - n_low : col + blocksize + n_hgh,
            ]

            rval = gaussian_filter(input_image, sigma=sigma, radius=n)
            rval = rval[m_low : rval.shape[0] - m_hgh, n_low : rval.shape[1] - n_hgh]
            output[row : row + blocksize, col : col + blocksize] = rval
    return output

def block_filter_to_file(
        image, filename, blocksize=64, downsample=2, sigma=None, radius=None
):
    M, N = image.shape

    if M % 2 == 0:
        M_output = M // 2
    else:
        M_output = M // 2 + 1
    if N % 2 == 0:
        N_output = N // 2
    else:
        N_output = N // 2 + 1

    with h5py.File(filename, "w") as h5_file:
        h5_file.create_dataset("image", shape=(M_output, N_output), dtype=image.dtype)

        n = radius
        index = 0
        total = int(np.ceil(M/blocksize)*np.ceil(N/blocksize))
        for row in range(0, M, blocksize):
            for col in range(0, N, blocksize):
                m_low = n + min(row - n, 0)
                m_hgh = max(min(M - (row + blocksize + n), n), 0)
                n_low = n + min(col - n, 0)
                n_hgh = max(min(N - (col + blocksize + n), n), 0)

                input_image = image[
                    row - m_low : row + blocksize + m_hgh,
                    col - n_low : col + blocksize + n_hgh,
                ]

                rval = gaussian_filter(input_image, sigma=sigma, radius=n)
                rval = rval[
                    m_low : rval.shape[0] - m_hgh, n_low : rval.shape[1] - n_hgh
                ]
                rval = rval[::downsample, ::downsample]
                h5_file["image"][
                    row // downsample : row // downsample + rval.shape[0],
                    col // downsample : col // downsample + rval.shape[1],
                ] = rval

                logging.info(f"{index+1}/{total}")
                index += 1

def generate_pyramid(file_name, image_key):
    downscale = 2
    sigma = 2 * downscale / 6.0
    radius = 3
    blocksize=2**15

    with h5py.File(file_name, "a") as h5_image:
        # Calculate number of levels based on typical 1080 resolution
        levels = 3
        # Find the length of the longest side
        length = max(h5_image[image_key].shape)

        logging.info('length: ', length)

        levels = 0
        while length > 1:
            length = length // downscale
            levels += 1

        logging.info('levels: ', levels)

        if "pyramid" in h5_image:
            logging.info("Pyramid already exists")
            return
        
        h5_image.create_group("pyramid")

        for i in range(0, levels):
            if i == 0:
                # if the first level, pull from the original image
                input_image=h5_image[image_key]
            else:
                input_image=h5_image["pyramid"][f"l_{i}"]

            block_filter_to_pyramid(input_image=input_image,
                                output_destination=h5_image["pyramid"],
                                target=f"l_{i+1}",
                                blocksize=blocksize,
                                sigma=sigma,
                                radius=radius)
            
            logging.info(f"Pyramid level: {i+1}/{levels}")
                
def block_filter_to_pyramid(
        input_image, output_destination, target, blocksize=64, downsample=2, sigma=None, radius=None
):
    M, N = input_image.shape

    if M % 2 == 0:
        M_output = M // 2
    else:
        M_output = M // 2 + 1
    if N % 2 == 0:
        N_output = N // 2
    else:
        N_output = N // 2 + 1

    output_destination.create_dataset(target, shape=(M_output, N_output), dtype=input_image.dtype)

    n = radius

    index = 0
    total = int(np.ceil(M/blocksize)*np.ceil(N/blocksize))
    for row in range(0, M, blocksize):
        for col in range(0, N, blocksize):
            m_low = n + min(row - n, 0)
            m_hgh = max(min(M - (row + blocksize + n), n), 0)
            n_low = n + min(col - n, 0)
            n_hgh = max(min(N - (col + blocksize + n), n), 0)

            input_image = input_image[
                row - m_low : row + blocksize + m_hgh,
                col - n_low : col + blocksize + n_hgh,
            ]

            rval = gaussian_filter(input_image, sigma=sigma, radius=n)
            rval = rval[
                m_low : rval.shape[0] - m_hgh, n_low : rval.shape[1] - n_hgh
            ]
            rval = rval[::downsample, ::downsample]
            output_destination[target][
                row // downsample : row // downsample + rval.shape[0],
                col // downsample : col // downsample + rval.shape[1],
            ] = rval

            logging.info(f"Block: {index+1}/{total}")
            index += 1
