""" zfish command script
"""
from types import DynamicClassAttribute
import paramiko
import os
import time
from pprint import pprint
import datetime, timedelta
import logging

HPCHOSTNAME='awoonga.qriscloud.org.au'
USERNAME="uqjarno4"
VERBOSE=True

## Each fish should produce 7 output files + a plane folder per plane
## F.npy, iscell.npy, Fneu.npy, spks.npy, ops.npy, stat.npy, Fall.npy, plane0
## so number planes * 8 is how big this should be per fish.
FILESPERFISH = 8

# Seem to be the only fps values used
FPS2PLANES = {
    2 : 50,
    4 : 25
}

WAITTIME = 6 * 60 * 60


def get_current_time():
    # Add +10 for Brisbane time
    return datetime.datetime.now() + datetime.timedelta(hours=10)


class Fish:
    def __init__(self, base_fish_folder, parent_fish_folder, fps, root_output_folder):
        self.base_fish_folder = base_fish_folder
        self.parent_fish_folder = parent_fish_folder
        self.fps = fps
        self.root_output_folder = root_output_folder
        self.jobids = []

    def get_absolute_path(self):
        return os.path.join(self.parent_fish_folder, self.base_fish_folder)

    def get_output_folder(self):
        """ Return the fish specific output folder in the root_output_folder
        """
        return os.path.join(self.root_output_folder, self.base_fish_folder)

    def add_jobid(self, jobid):
        self.jobids.append(jobid)

    def latest_job_id(self):
        return self.jobids[-1]

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f'Fish({self.base_fish_folder}, {self.jobids})'

def main():

    logging.basicConfig(filename='zfish_log.log', level=logging.INFO)

    ## Once finished this will come from cmd line or somewhere else
    input_fish_folder = '/QRISdata/Q2396/SPIM_120170/Spontaneous'
    root_output_folder = '/QRISdata/Q4008/zfish_s2p_output'
    fps = 2

    logging.info('Started zfish command')
    logging.info(f'Time now: {get_current_time()}')

    ssh = get_ssh_connection()

    ## Get a list of all fish
    ls_fish = f'ls {input_fish_folder}'
    all_fish = run_command(ssh, ls_fish)
    # ls results end in \n, need to strip away
    all_fish = [filename.strip() for filename in all_fish]

    ## Good fish indexes
    # Only test on the good fish NOTE: Already offset by -1
    good_fish_idxs = [4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 18, 19, 20, 22, 23, 25, 26, 27, 28, 29]
    all_fish = [all_fish[idx] for idx in good_fish_idxs]

    ## TODO : remove, for testing only use a few fish
    #all_fish = all_fish[4:7]

    count = 0
    ## Start a job for all fish
    incomplete_fish = []
    for base_fish_folder in all_fish:

        fish = Fish(base_fish_folder, input_fish_folder, fps, root_output_folder)
        incomplete_fish.append(fish) # Build list of fish left to compute for

        start_fish_job(ssh, fish)
    
    logging.info('Jobs started, now monitor')

    # Now monitor the jobs until done
    finished_fish = []
    while incomplete_fish:

        logging.info(f'Check all fish again, time: {get_current_time()}')

        running_jobs = get_current_jobs(ssh)

        for fish in incomplete_fish:

            ## Fish is still computing
            if fish.latest_job_id() in running_jobs:
                logging.info(f'Fish with jobid: {fish.latest_job_id()} is running, skip')
                continue

            ## If fish has finished
            if fish_finished_computing(ssh, fish):
                finished_fish.append(fish)
                logging.info(f'Fish finished: {fish}')
                continue

            logging.info('--------------------------   DEBUG   ------------------------------')
            logging.info(f'-------  job: {fish.latest_job_id()} not in currently running jobs but also not finished')
            logging.info(f'fish: {fish}')
            logging.info('Restarting fish')

            ## restart fish
            jobid = start_fish_job(ssh, fish)
            if not jobid:
                logging.warning('Error starting fish, could not get jobid')


        ## Remove finished fish from list of fish left
        [incomplete_fish.remove(fish) for fish in finished_fish]

        ## Some kind of time limiter to stop spamming awoonga
        time.sleep(WAITTIME) # wait an hour



def start_fish_job(ssh, fish):

    launch_job = f'python ~/pipelina/HPC_run_fish.py {fish.get_absolute_path()} {fish.root_output_folder} {fish.fps}'
    #print(f'Launch job: {launch_job}')

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
        #print(f'------ OUTPUT for sending job command: {output}')
        jobid = output.split('.')[0]
        if '.awonmgr' in output and jobid.isdigit():
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
        if '.awonmgr2' in line:
            jobid = line.split('.awonmgr2')[0]
            running_jobs.append(jobid)
    
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
