from paramiko import SSHClient
import multiprocessing as MP
from scp import SCPClient
import argparse
import random
import os

THREAD_LIMIT = 6
sem = MP.Semaphore(THREAD_LIMIT)

def download_p2p_file(user, server, password, remotepath, localdest):
    sem.acquire()
    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname=server, username=user, password=password)
    # SCPCLient takes a paramiko transport as its only argument
    scp = SCPClient(ssh.get_transport())
    scp.get(remotepath, localdest)
    scp.close()
    sem.release()

def main(args):
    print(args)
    remote_paths = []
    with open(args["files"], 'r') as file_list:
        for this_file in file_list:
            boxname = this_file.split('.')[0]
            remote_paths.append(os.path.join(args["remotedir"], boxname, this_file.rstrip()))
    chosen_remote_paths = random.sample(remote_paths, args["n"])
    print("Chosen files: {0}".format(chosen_remote_paths))
    processes = []
    for idx, remote_file_path in enumerate(chosen_remote_paths, 1):
        print("{0}/{1} -> Fetching {2} now..".format(idx, args["n"], remote_file_path))
        task = MP.Process(target=download_p2p_file, args=(args["user"], args["server"], args["password"], remote_file_path, args["downloaddir"]))
        task.start()
        processes.append(task)
    # wait for tasks for finish
    for task in processes:
        while task.is_alive():
            pass


if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--user", type=str)
    CLI.add_argument("--server", type=str)
    CLI.add_argument("--password", type=str)
    CLI.add_argument("--remotedir", type=str)
    CLI.add_argument("--files", type=str)
    CLI.add_argument("--downloaddir", type=str)
    CLI.add_argument("-n", type=int)
    args = vars(CLI.parse_args())
    main(args)