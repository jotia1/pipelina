""" zfish command script but specific for slices
"""
import paramiko
import os
import time
from pprint import pprint
import datetime
import logging
import sys

HPCHOSTNAME='awoonga.qriscloud.org.au'
USERNAME=os.getenv('UQUSERNAME')
VERBOSE=True
SLICE='slice'
FISH='fish'
JOBIDEXTENSION='[].awon'

## Each fish should produce 7 output files + a plane folder per plane
## F.npy, iscell.npy, Fneu.npy, spks.npy, ops.npy, stat.npy, Fall.npy, plane0
## so number planes * 8 is how big this should be per fish.
FILESPERSLICE = 8

# Seem to be the only fps values used
FPS2PLANES = {
    2 : 50,
    4 : 25
}

WAITTIME = 6 * 60 * 60
#WAITTIME = 45

def get_current_time():
    return datetime.datetime.now()



def main():

    if len(sys.argv) != 5:
        print('Program expects exactly 4 arguments, exiting.')
        print('Should be folder containing folders with tifs, output location, fps and expname.')
        print('e.g. python3 zfishcommand_slice.py /QRISdata/Q2396/SPIM_120170/Spontaneous /QRISdata/Q4008/zfish_s2p_output 2 expname')
        return

    exp_name = sys.argv[4]
    logging.basicConfig(filename=f'{exp_name}.log', level=logging.INFO)

    ## Once finished this will come from cmd line or somewhere else
    input_slice_folder = sys.argv[1]     #'/QRISdata/Q2396/SPIM_120170/Spontaneous'
    root_output_folder = sys.argv[2]    #'/QRISdata/Q4008/zfish_s2p_output'
    fps = sys.argv[3]

    logging.info('Started zfish SLICE command')
    logging.info(f'Time now: {get_current_time()}')
    logging.info(f'Supplied args: {sys.argv}')

    ssh = get_ssh_connection()

    ## Get a list of all slices
    ls_slice = f'ls {input_slice_folder}'
    all_slices = run_command(ssh, ls_slice)
    # ls results end in \n, need to strip away
    all_slices = [filename.strip() for filename in all_slices]

    incomplete_slices = all_slices.copy()
    array_job_ids = []

    remove_finished_slices(ssh, incomplete_slices, root_output_folder)
    
    ## Then start an array for all incomplete slices
    initial_id = start_slice_array(ssh, incomplete_slices, root_output_folder, fps, exp_name)
    if not initial_id:
        logging.warn("Failed to get an intial array id, quiting.")
        return
    array_job_ids.append(initial_id)
    logging.info(f'Array job started, now monitor {initial_id}')

    # Now monitor the jobs until done
    finished_slices = []
    while incomplete_slices:

        ## Some kind of time limiter to stop spamming awoonga
        time.sleep(WAITTIME) 

        logging.info(f'Check all slices again, time: {get_current_time()}')

        running_jobs = get_current_jobs(ssh)

        print(array_job_ids, 'Running: ', running_jobs)
        if array_job_ids[-1] in running_jobs:  # Array is still running, check back later
            logging.info(f'Array still running, jobid: {array_job_ids[-1]} is running, skip')
            continue  # wait time and check again

        # Array has stopped - remove any finished slices
        logging.info(f'Array stopped, number of incomplete slices before removal: {len(incomplete_slices)}')
        remove_finished_slices(ssh, incomplete_slices, root_output_folder)
        logging.info(f'Number of incomplte slices after removal: {len(incomplete_slices)}')

        if len(incomplete_slices) > 0:  # Any slices left to do
            logging.info(f'Still incomplete slices, restarting array.')
            array_job_ids.append(start_slice_array(ssh, incomplete_slices, root_output_folder, fps, exp_name))
            

    logging.info(f'No slices left, job done. Exiting.')



def remove_finished_slices(ssh, incomplete_slices, root_output_folder):
    """
    """
    # use the find command to get all files in output_folder
    find_command = f'find {root_output_folder}'
    logging.info(f'find command : {find_command}')
    stdin, stdout, stderr = ssh.exec_command(find_command)
    find_result = stdout.readlines()
    logging.debug(f'find_result: {find_result}')

    ## Count how many files exist for each slice
    counts = [0 for _ in range(len(incomplete_slices))]
    for filename in find_result:
        for i, slice in enumerate(incomplete_slices):
            if slice in filename:
                counts[i] += 1
                break

    logging.info(f'counts result: {counts}')
        
    # Any incomplete slices with the expected number of files are now complete
    finished_slices = []
    for i, count in enumerate(counts):
        if count == FILESPERSLICE:
            finished_slices.append(incomplete_slices[i])

    # Now actually remove finished slices from incomplete list
    for slice in finished_slices:
        incomplete_slices.remove(slice)
        logging.info(f'Finished and removing slice: {slice}')

    
    logging.info(f'Finished slices removed, {len(incomplete_slices)} left.')

    return incomplete_slices


def start_slice_array(ssh, incomplete_slices, output_folder, fps, exp_name):

    ## Create a list of slices to do
    contents = '\n'.join(incomplete_slices)
    incomplete_slices_filename = f'incomplete_slices_{exp_name}.txt'
    with open(incomplete_slices_filename, 'w') as f:
        f.write(contents)

    ## Send over to cluster
    ftp_client = ssh.open_sftp()
    ftp_client.put(incomplete_slices_filename, incomplete_slices_filename)

    ## Launch and check array
    launch_job = f'python ~/pipelina/HPC_run_slice.py {incomplete_slices_filename} {output_folder} {fps}'
    print('To start: ', launch_job)
    # Actually send job to awoonga
    stdin, stdout, stderr = ssh.exec_command(launch_job)

    # If successful there shouldn't be anything in the error output (stderr)
    any_errors = stderr.readlines()
    if any_errors:
        logging.warning(f'--------- Got text on stderr: {any_errors}')
    else:
        # There was nothing on stderr, so seems good, try and get the jobid
        output = stdout.readlines()[0]
        print(f'------ OUTPUT for sending job command: {output}')
        jobid = output.split(JOBIDEXTENSION)[0]
        print(jobid)
        if JOBIDEXTENSION in output and jobid.isdigit():
            logging.info(f"ArrayID: {jobid}")
            return jobid
        else:
            logging.warning(f'-------- Issue with Jobid parsing \n -------- Got output: {output}')
            return None

    return None # failed to get job_id
    



def start_slice_job(ssh, fish):
    raise NotImplementedError

    launch_job = f'python ~/pipelina/HPC_run_slice.py {fish.get_absolute_path()} {fish.root_output_folder} {fish.fps}'
    print(f'Launch job: {launch_job}')
    #return

    # Actually send job to awoonga
    stdin, stdout, stderr = ssh.exec_command(launch_job)

    # If successful there shouldn't be anything in the error output (stderr)
    any_errors = stderr.readlines()
    if any_errors:
        logging.warning(f'--------- Got text on stderr: {any_errors}')
        return None
    else:
        # There was nothing on stderr, so seems good, try and get the jobid
        output = stdout.readlines()[0]
        print(f'------ OUTPUT for sending job command: {output}')
        jobid = output.split('.')[0]
        if JOBIDEXTENSION in output and jobid.isdigit():
            logging.info(f"JobID: {jobid} for fish: {fish.base_fish_folder}")
            fish.add_jobid(jobid)
            return jobid
        else:
            logging.warning(f'-------- Issue with Jobid parsing for fish: {fish.base_fish_folder}\n -------- Got output: {output}')
            return None

def get_current_jobs(ssh):
    """ Given the ssh object return a list of all current jobs running 
    """
    stdin, stdout, stderr = ssh.exec_command('qstat')

    running_jobs = []
    for line in stdout.readlines():
        print('line: ', line)
        if JOBIDEXTENSION in line:
            jobid = line.split(JOBIDEXTENSION)[0]
            running_jobs.append(jobid)
    
    print('all found jobs:', running_jobs)
    return running_jobs

def run_command(ssh, command):
    """
    """
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.readlines()


def fish_finished_computing(ssh, fish):
    """ Check if a given fish has finished
    """
    find_command = f'find {fish.get_output_folder()}'
    logging.info(f'find command : {find_command}')
    stdin, stdout, stderr = ssh.exec_command(find_command)
    find_result = stdout.readlines()

    num_files_found = len(find_result)

    nplanes = FPS2PLANES.get(fish.fps)
    total_files_expected = (nplanes * FILESPERFISH) + 1 # +1 for the original directory
    
    logging.info(f'Checking if fish is finished, expected number files: {total_files_expected}, found: {num_files_found}')

    return total_files_expected == num_files_found



def get_ssh_connection():
    ## connect to awoonga
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(HPCHOSTNAME, username=USERNAME)
    return ssh
    
if __name__ == '__main__':
    main()
