""" Given a slice, run s2p on that slice

The processed slice will be saved into the output folder with .tif removed and s2p prepended

Takes 3 arguements:
slice_name
output_folder
fps 
"""
import suite2p
import sys
import os
import datetime

def main():

    ## Check and collect arguments
    if len(sys.argv) != 4:
        print("Missing required arguments. Should be <slice_name> <output_folder> <fps>")
        print("Example: python run_slice.py /QRISdata/Q4008/Preprocessed/Spontaneous/slice_etc.tif /QRISdata/Q4008/s2p_output/ 2")
        exit()
    print(f'Start time: {datetime.datetime.now()}')
    print("Args:", sys.argv)
    try:
        slice_name = os.path.normpath(sys.argv[1])
        output_base_folder = os.path.normpath(sys.argv[2])
        fps = int(sys.argv[3])
    except:
        print(f'Error raised when trying to parse args: {sys.argv}')
        raise Exception('Error with input args.')


    ## Define 1P ops for full fish
    nplanes = 1  # Note different from run_fish.py
    ops = suite2p.default_ops()
    ops['1Preg'] = True
    ops['pre_smooth'] = 2
    ops['spatial_taper'] = 5
    ops['diameter'] = (3,4)
    ops['threshold_scaling'] = 0.5
    ops['max_iterations'] = 100
    ops['inner_neuropil_radius'] = 1
    ops['min_neuropil_pixels'] = 1
    ops['sparse_mode'] = False
    ops['spikedetect'] = False
    ops['smooth_sigma'] = 4
    ops['high_pass'] = 30
    ops['save_mat'] = 1
    ops['batch_size'] = 2000
    ops['tau'] = 1.4  #Make sure to change this value depending on GCaMP6s or GCaMP6f!
    ops['fs'] = fps / nplanes
    ops['nchannels'] = 1
    ops['nplanes'] = nplanes

    ## Define the db
    output_fish_folder = os.path.join(output_base_folder, os.path.basename(slice_name))
    db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
	  'data_path': [slice_name], # a list of folders with tiffs 
											 # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
	  'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
	  'tiff_list': [slice_name], # list of tiffs in folder * data_path *!
      'save_folder': output_fish_folder,
      #'classifier_path': "~/pipelina/classifierAG.npy",
	}

    ## Debugging 
    print(f'-------------  {os.path.basename(slice_name)}  -------------')
    print(f'ops: {ops}')
    print(f'db: {db}')

    ## Run suite2p
    opsEnd=suite2p.run_s2p(ops=ops,db=db)

if __name__ == '__main__':
    main()