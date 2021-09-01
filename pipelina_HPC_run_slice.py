""" HPC_run_slice.py
Build the pbs script for running a slice array

"""
from subprocess import call
import sys
import glob
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('slices_file_path', help="Absolute path to a file with a list of absolute paths to slices")
parser.add_argument('output_directory', help="Path where output fish folders should be placed")
parser.add_argument('s2p_config_json', help="Path to a json file containing ops for suite2p")
args = parser.parse_args()


slices_filename = os.path.normpath(args.slices_file_path)
output_folder = os.path.normpath(args.output_directory)

# Filename will be in format f'incomplete_slices_{exp_name}.txt'
expname = slices_filename.split('_')[2].strip('.txt')

## Define variables needed for file
users_school = os.getenv('UQSCHOOL') #'UQ-EAIT-ITEE' # likely UQ-QBI or UQ-SCI-SBMS

with open(slices_filename, 'r') as f:
    num_files = len(f.readlines())

## Build pbs script 
file_contents = f"""#!/bin/bash
#PBS -N {expname}
#PBS -A {users_school}
#PBS -l select=1:ncpus=12:mem=110GB:vmem=110GB
#PBS -l walltime=00:05:00
#PBS -j oe
#PBS -k doe
#PBS -J 1-{num_files}


module load anaconda
source activate suite2p

single_slice=`cat {slices_filename} | head -n ${{PBS_ARRAY_INDEX}} | tail -n 1`

echo $single_slice

/usr/local/bin/recall_medici $single_slice

python ~/pipelina/pipelina_run_slice.py $single_slice {output_folder} {args.s2p_config_json}
"""


## Write pbs script to disk
pbs_filename = 'pipelina_HPC_run_slice.pbs'
with open(pbs_filename, 'w') as fp:
    fp.write(file_contents)


## Launch the HPC job
job_string = f"qsub {pbs_filename}"
print(job_string)
call([job_string],shell=True)