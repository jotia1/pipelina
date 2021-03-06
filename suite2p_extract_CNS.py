import numpy as np
import sys
import os
from suite2p import run_s2p
import shutil
import glob
fnames=[sys.argv[1]]
final_frate=int(sys.argv[3]) # frame rate in Hz

# set your options for running
ops = np.load('./ops_1P_CNS.npy',allow_pickle=True).item()
data_path = os.path.normpath(sys.argv[2])

ops['nchannels'] = 1
ops['fs'] = final_frate
#ops['classifier_path'] = '~/Classifier_MW.npy'
#for file in glob.glob(os.path.join(data_path,'*.tif')):        
db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
	  'data_path': [data_path], # a list of folders with tiffs 
											 # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
	  'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
	  'tiff_list': fnames, # list of tiffs in folder * data_path *!
	  'save_folder': data_path+'/suite2p_'+os.path.basename(fnames[0])
	}
# run one experiment
#print(db)
try:
	os.mkdir(db['save_folder'])
except FileExistsError:
	print(db['save_folder'], "Continuing.")
opsEnd=run_s2p(ops=ops,db=db)