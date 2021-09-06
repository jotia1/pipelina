""" HPC_run_fish.py
Build the pbs script for running a single fish 

"""
from subprocess import call
import sys
import os
import argparse



parser = argparse.ArgumentParser()
parser.add_argument('fish_abs_path', help="Absolute path to the directory with .tif files")
parser.add_argument('output_directory', help="Absolute path to this fish's individual output folder")
parser.add_argument('s2p_config_json', help="Path to a json file containing ops for suite2p")
args = parser.parse_args()

fish_folder = os.path.normpath(args.fish_abs_path)
fish_output_folder = os.path.normpath(args.output_directory)
fish_num = os.path.basename(fish_folder).split('fish')[1].split('_')[0]

## Define variables needed for file
users_school = os.getenv('UQSCHOOL')

## Build pbs script 
file_contents = f"""#!/bin/bash
#PBS -N pplna{fish_num}
#PBS -A {users_school}
#PBS -l select=1:ncpus=12:mem=110GB:vmem=110GB
#PBS -l walltime=24:00:00
#PBS -j oe
#PBS -k doe
#PBS -m abe
#PBS -M uqjarno4@uq.edu.au


module load anaconda
source activate suite2p

for fish_tif in `ls {fish_folder}/*.tif`; do
    /usr/local/bin/recall_medici $fish_tif
done

echo pipelina_run_fish.py {fish_folder} {fish_output_folder} {args.s2p_config_json}
python ~/pipelina/pipelina_run_fish.py {fish_folder} {fish_output_folder} {args.s2p_config_json}
"""


## Write pbs script to disk
pbs_filename = 'pipelina_HPC_run_fish.pbs'
with open(pbs_filename, 'w') as fp:
    fp.write(file_contents)


## Launch the HPC job
job_string = f"qsub {pbs_filename}"
call([job_string],shell=True)