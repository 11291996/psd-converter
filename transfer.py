import os
import multiprocessing

#one has to use sudo to transfer files to the destination

def rsync_file(file, path, destination):
    os.system(f"rsync -avh \"{os.path.join(path, file)}\" \"{destination}/\"")

if __name__ == "__main__":
    path = path = "/mnt/f/paneah/dataset/다온/그 던전의 S급 시한부 영애/그던전 원고 선화 (원본)"
    destination = "/mnt/z/onomaai/data/psd/다온/그 던전의 S급 시한부 영애/color"

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