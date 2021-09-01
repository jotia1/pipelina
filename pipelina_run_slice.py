import argparse
import json
import suite2p
import os

parser = argparse.ArgumentParser()
parser.add_argument('slice_abs_path', help="Absolute path to the directory with .tif files")
parser.add_argument('output_directory', help="Path where output fish folders should be placed")
parser.add_argument('s2p_config_json', help="Path to a json file containing ops for suite2p")
args = parser.parse_args()

print(args.slice_abs_path, args.output_directory, args.s2p_config_json)

## Load s2p file
with open(args.s2p_config_json, 'r') as fp:
    input_ops = json.loads(fp.read())


input_slice_folder = os.path.normpath(args.slice_abs_path)
output_base_folder = os.path.normpath(args.output_directory)

## Define 1P ops for full fish
ops = suite2p.default_ops()
ops.update(input_ops)

## Define the db
output_slice_folder = os.path.join(output_base_folder, os.path.basename(input_slice_folder))
db = {'look_one_level_down': False, # whether to look in ALL subfolders when searching for tiffs
    'data_path': [input_slice_folder], # a list of folders with tiffs 
                                            # (or folder of folders with tiffs if look_one_level_down is True, or subfolders is not empty)         
    'fast_disk': os.environ["TMPDIR"], # string which specifies where the binary file will be stored (should be an SSD)
    'tiff_list': [input_slice_folder], # list of tiffs in folder * data_path *!
    'save_folder': output_slice_folder,
    #'classifier_path': "~/pipelina/classifierAG.npy",
}

## Debugging 
print(f'-------------  {os.path.basename(input_slice_folder)}  -------------')
print(f'ops: {ops}')
print(f'db: {db}')

try:
	os.mkdir(db['save_folder'])
except FileExistsError:
	print('save folder existed:', db['save_folder'], "Continuing.")

## Run suite2p
opsEnd=suite2p.run_s2p(ops=ops,db=db)