path = "/mnt/z/onomaai/data/psd/다온/제가 산건 땅이지 남자가 아닌데요"
new_path = "/mnt/z/onomaai/data/clip/다온/제가 산건 땅이지 남자가 아닌데요"

import os 
from tqdm import tqdm

#get all the psd files in the directory and its subdirectories

def get_all_clip_files(path):
    clip_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".clip"):
                clip_files.append(os.path.join(root, file))
    return clip_files

#put psds in the new episode folders

all_clips = get_all_clip_files(path)

for new_file in tqdm(os.listdir(new_path)):
    new_dir = new_path + "/" +  new_file
    page = 1
    for clip in tqdm(all_clips):
        if clip.split("/")[8] == new_dir.split("/")[8]:
            os.system("mv \"" + clip + "\"" + " " + "\"" + new_dir + "/" + f"{page}.clip" + "\"")
            page += 1