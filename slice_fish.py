import numpy as np
from ScanImageTiffReader import ScanImageTiffReader
from tifffile import imread, imsave
import glob
import sys
import os

## Hardcoded image sizes
RAWTIFFX = 540
RAWTIFFY = 640
NUMFRAMESPERTIFF = 6172

def slice_fish(input_fish_folder, output_base_folder, nplanes):
    """
    """
    all_raw_tiffs = glob.glob(input_fish_folder + '/*.tif')
    # The indexing belows requires tiffs are loaded in order of imaging time
    all_raw_tiffs.sort()    
    result = [np.ndarray((0, RAWTIFFX, RAWTIFFY)) for _ in range(nplanes)]

    ## Go through tiffs collecting frames for each slice
    for i, f in enumerate(all_raw_tiffs):
        print(f'Load tiff {f}')
        tiff_data = ScanImageTiffReader(f).data()
        for frame_idx in range(nplanes):
            offset = (nplanes - (i * NUMFRAMESPERTIFF)+ frame_idx) % nplanes # Hmm, should be the offset of each start within a tiff?
            slice_data = tiff_data[offset::nplanes, :, :].copy()
            result[frame_idx] = np.concatenate((result[frame_idx], slice_data), axis=0)
        del tiff_data
    
    ## Save all the slices 
    for slice_idx, slice in enumerate(result):
        slice_filename = os.path.join(output_base_folder, f'slice{slice_idx}_{os.path.basename(input_fish_folder)}')
        print(f'Try saving: {slice_filename}')
        imsave(slice_filename, slice)


def main():
    """ Given a folder with tiffs from a single fish,
    slice the fish into multiple planes and save the results
    to the ouput folder.
    """
        ## Check and collect arguments
    if len(sys.argv) != 4:
        print("Missing required arguments. Should be <fish_folder_name> <output_folder> <nPlanes>")
        print("Example: python slice_fish.py /QRISdata/Q4008/SPIM_120170/fish05/ /QRISdata/Q4008/sliced_fish_output/ 50")
        exit()
    print("Args:", sys.argv)
    try:
        input_fish_folder = os.path.normpath(sys.argv[1])
        output_base_folder = os.path.normpath(sys.argv[2])
        nplanes = int(sys.argv[3])
    except:
        print(f'Error raised when trying to parse args: {sys.argv}')
        raise Exception('Error with input args.')

    slice_fish(input_fish_folder, output_base_folder, nplanes)


if __name__ == '__main__':
    main()