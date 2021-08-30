""" Given a fish's folder, run s2p on that full fish

The tifs in the specified fish folder will be processed with s2p and the result
saved to the output folder with the fish in a new folder prepended with s2p_

Takes 3 arguements:
fish_folder
output_folder
fps 
"""
import suite2p
import sys
import os
import datetime

GCAMP_TAUS = {
    'gcamp6f' : 0.7,
    'gcamp6s' : 1.4
}

def main():

    nplanes = 50
    gcamp_type = 'gcamp6s'
    if len(sys.argv) == 6:
        nplanes = int(sys.argv[4])
        gcamp_type = sys.argv[5]

    ## Check and collect arguments
    if len(sys.argv) < 4:
        print("Missing required arguments. Should be <fish_folder_name> <output_folder> <fps> <nplanes> <gcamp_type>")
        print("Example: python run_fish.py /QRISdata/Q4008/SPIM_120170/fish05/ /QRISdata/Q4008/s2p_output/ 2 50 gcamp6s")
        exit()
    print(f'Start time: {datetime.datetime.now()}')
    print("Args:", sys.argv)
    try:
        input_fish_folder = os.path.normpath(sys.argv[1])
        output_base_folder = os.path.normpath(sys.argv[2])
        fps = int(sys.argv[3])
    except:
        print(f'Error raised when trying to parse args: {sys.argv}')
        raise Exception('Error with input args.')

    ## Some sanity checks
    assert gcamp_type in GCAMP_TAUS.keys(), f"GCamp type: {gcamp_type} not recognised." 

    ## Define 1P ops for full fish
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
    ops['tau'] = GCAMP_TAUS.get(gcamp_type)
    ops['fs'] = fps / nplanes
    ops['nchannels'] = 1
    ops['nplanes'] = nplanes

    ## Define the db
    output_fish_folder = os.path.join(output_base_folder, os.path.basename(input_fish_folder))
    db = {'look_one_level_down': True, # whether to look in ALL subfolders when searching for tiffs
	  'data_path': [input_fish_folder], # a list of folders with tiffs 
											 # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
	  'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
	  'save_folder': output_fish_folder,
      #'classifier_path': "~/pipelina/classifierAG.npy",
	}

    ## Debugging 
    print(f'-------------  {os.path.basename(input_fish_folder)}  -------------')
    print(f'ops: {ops}')
    print(f'db: {db}')

    ## Run suite2p
    opsEnd=suite2p.run_s2p(ops=ops,db=db)

if __name__ == '__main__':
    main()