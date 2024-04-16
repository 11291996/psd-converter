import os
import multiprocessing

#one has to use sudo to transfer files to the destination

def rsync_file(file, path, destination):
    os.system(f"rsync -avh \"{os.path.join(path, file)}\" \"{destination}/\"")

if __name__ == "__main__":
    path = path = "/mnt/f/paneah/dataset/청풍/웨폰 크리에이터"
    destination = "/mnt/z/onomaai/data/clip/청풍/웨폰 크리에이터"

    num_processes = multiprocessing.cpu_count()

    file_list = os.listdir(path)

    # Create a process pool
    pool = multiprocessing.Pool(processes=num_processes)

    # Start rsync for each file using multiple processes
    for file in file_list:
        pool.apply_async(rsync_file, args=(file, path, destination))

    # Close the pool to release resources
    pool.close()
    pool.join()