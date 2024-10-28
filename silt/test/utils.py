import h5py
import numpy as np
import pytest

from silt import pyramid_preprocessing
from PyQt5.QtWidgets import QGraphicsItem

@pytest.fixture()
def param_default():
    param = {
                "image_key": "data",
                "input_image": "data",
                "output_destination":"pyramid",
                "target":"test",
                "blocksize":500,
                "downsample":2,
                "sigma":4,
                "radius":3,
                "max_length":1024
            }
        
    return param

@pytest.fixture()
def param_small():
    param = {
                "image_key": "data",
                "input_image": "data",
                "output_destination":"pyramid",
                "target":"test",
                "blocksize":20,
                "downsample":2,
                "sigma":4,
                "radius":3,
                "max_length":5
            }
        
    return param

def generate_image(filename, M = 100, N = 100):
    blocksize = 500

    with h5py.File(filename,'w') as h5_file:

        h5_file.create_dataset("data",shape=(M,N),dtype="float64")
        index = 0
        total = int(np.ceil(M/blocksize)*np.ceil(N/blocksize))
        for row in range(0,M,blocksize):
            for col in range(0,N,blocksize):
                row_low = row
                row_hgh = min(row+blocksize,M)
                col_low = col
                col_hgh = min(col+blocksize,N)
                
                h5_file["data"][row_low:row_hgh,
                                col_low:col_hgh] = row + col
                
                # print(f"{index+1}/{total}")
                index += 1

def generate_image_small(filename):
    M=N=20

    with h5py.File(filename,'w') as h5_file:
        h5_file.create_dataset("data",shape=(M,N),dtype="float64")
        small_array = [[(i+j) for i in range(0,M)] for j in range(0,N)]
        h5_file["data"][:] = small_array

def generate_pyramid(path, params): 
    pyramid_preprocessing.generate_pyramid(
        file_path = path,
        image_key = params["image_key"],
        downsample = params["downsample"],
        sigma = params["sigma"],
        radius = params["radius"],
        blocksize = params["blocksize"],
        max_length = params["max_length"],
        no_pyramid = False)

class DummyQGraphicsItem(QGraphicsItem):
    """
    Represents base grid to draw all polygon items on.
    """
    def __init__(self,
                 parent=None):
        
        super(DummyQGraphicsItem, self).__init__(parent)
    
    def boundingRect(self):
        pass

    def paint(self, painter, option, widget=None):
        pass