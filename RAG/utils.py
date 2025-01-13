import os

def find_txt_files(folder_path, include_subfolders=True):
    txt_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.txt'):
                if include_subfolders:
                    txt_files.append(os.path.join(root, file))
                else:
                    txt_files.append(file)
    return txt_files

import os

def find_folders(folder_path):
    folders = []
    for root, dirs, files in os.walk(folder_path):
        for dir_name in dirs:
            # folders.append(os.path.join(root, dir_name))
            folders.append(dir_name)
    return folders