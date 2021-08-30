""" HPC_run_slice.py
Build the pbs script for running a slice array

"""
from subprocess import call
import sys
import glob
import os


if len(sys.argv) != 4:
    print("Missing required arguments. Should be <incomplete_slices_filename> <output_folder> <fps>")
    print("Example: python HPC_run_slice.py slices_filename /QRISdata/Q4008/zfish_s2p_slice_output 2")
    exit()
print("Args:", sys.argv)

slice_filename = os.path.normpath(sys.argv[1])
output_folder = os.path.normpath(sys.argv[2])
fps = sys.argv[3]
# Filename will be in format f'incomplete_slices_{exp_name}.txt'
expname = slice_filename.split('_')[2].strip('.txt')

## Define variables needed for file
users_school = os.getenv('UQSCHOOL') #'UQ-EAIT-ITEE' # likely UQ-QBI or UQ-SCI-SBMS

with open(slice_filename, 'r') as f:
    num_files = len(f.readlines())

## Build pbs script 
file_contents = f"""#!/bin/bash
#PBS -N {expname}
#PBS -A {users_school}
#PBS -l select=1:ncpus=12:mem=110GB:vmem=110GB
#PBS -l walltime=05:00:00
#PBS -j oe
#PBS -k doe
#PBS -J 1-{num_files}


module load anaconda
source activate suite2p

single_slice=`cat {slice_filename} | head -n ${{PBS_ARRAY_INDEX}} | tail -n 1`

echo $single_slice

/usr/local/bin/recall_medici $single_slice

python ~/pipelina/suite2p_extract_CNS.py $single_slice {output_folder} {fps}
"""


## Write pbs script to disk
pbs_filename = 'HPC_run_slice.pbs'
with open(pbs_filename, 'w') as fp:
    fp.write(file_contents)


## Launch the HPC job
job_string = f"qsub {pbs_filename}"
print(job_string)
call([job_string],shell=True)