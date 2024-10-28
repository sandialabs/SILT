import h5py
import numpy as np

filename="example.h5"
M=70000
N=70000
blocksize = 2**15

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
                             col_low:col_hgh] = np.random.randint(low=0, 
                                                                  high=255, 
                                                                  size=(row_hgh-row_low,
                                                                    col_hgh-col_low))
            
            print(f"{index+1}/{total}")
            index += 1
        # end for col
    # end for row
# end with
