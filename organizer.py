path = "/mnt/z/onomaai/data/clip/다온/제가 산건 땅이지 남자가 아닌데요"

import os 

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

for new_path in os.listdir(path):
    new_path = path + "/" +  new_path
    page = 1
    for psd in all_clips:
        if psd.split("/")[8] == new_path.split("/")[8]:
            os.system("mv \"" + psd + "\"" + " " + "\"" + new_path + "/" + f"{page}.psd" + "\"")
            page += 1