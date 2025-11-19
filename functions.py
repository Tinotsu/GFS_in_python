import argparse
import subprocess
import os
import csv

file = 'gfs.txt'
temp_file = 'temp.txt'
sha_file = 'sha.txt'

def add_obj(obj):
    with open(file, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([obj])

def get_full_path(obj):
    full_path = str(os.getcwd() + '/' + obj)
    if os.path.exists(full_path):
        return full_path
    return None

def get_ext(obj):
    rev_ext = []
    rev_obj = obj[::-1]
    for c in rev_obj:
        if c == '.':
            break
        rev_ext.append(c)
    ext = ''.join(rev_ext[::-1])
    return ext

def get_sha(file):
    sha = subprocess.check_output(["sha256sum", file], text=True)
    return sha.split()[0]

def is_empty(file):
    empty = subprocess.check_output(["cat", file], text=True)
    if empty:
        return False
    else:
        return True

def get_file_name(obj):
    rev_text = []
    rev_obj = obj[::-1]
    for c in rev_obj:
        if c == '/':
            break
        rev_text.append(c)
    file = ''.join(rev_text[::-1])
    return file

def find_moved(file):
    path = os.path.expanduser("~/")
    file_name = get_file_name(file)
    file_path = subprocess.check_output(['find', path, '-name', file_name], text=True)
    list_file_path = file_path.split()
    if len(list_file_path) >= 1:
        return list_file_path[0]
    # Maybe find a better way to check if it the right one...

def find_renamed(obj):
    list_file_dir = os.listdir()
    result = None
    for file_dir in list_file_dir:
        if os.path.isfile(file_dir) and not is_empty(file_dir):
            with open(sha_file, newline='') as f:
                list_sha = csv.reader(f)
                for sha in list_sha:
                    sha_file_dir = get_sha(file_dir)
                    if sha_file_dir == sha[1]:
                        result = file_dir
                        return result

def file_exists(file):
    if not os.path.isfile(file):
        return False
    else:
        return True

def write_sha():
    with open(file, newline='') as infile, \
            open(sha_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    if '.' in line[0] and file_exists(line[0]):
                        row = get_sha(line[0])
                        new_row = [line[0], row]
                        writer.writerow(new_row)

def check_status():
    moved_file = {}
    renamed_file = {}
    okay_file = []
    with open(file, newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            obj = line[0]
            if '.' in obj:
                exists = os.path.exists(obj)
                if exists:
                    okay_file.append(obj)
                else:
                    moved = find_moved(obj)
                    if moved:
                        moved_file[obj] = moved
                    else:
                        renamed = find_renamed(obj)
                        if renamed:
                            renamed_file[obj] = renamed
                        else:
                            return
    return moved_file, renamed_file, okay_file

def repair_moved(moved):
    list_new_line=[]
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    new_line=[]
                    for ele in line:
                        if '.' in ele:
                            if ele in moved:
                                new_line.append(moved[ele])
                            else:
                                new_line.append(ele)
                        else:
                            new_line.append(ele)
                    if new_line not in list_new_line:
                        list_new_line.append(new_line)
                for row in list_new_line:
                    writer.writerow(row)
    os.replace(temp_file, file)

def repair_renamed(renamed):
    list_new_line=[]
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    new_line=[]
                    for ele in line:
                        if '.' in ele:
                            if ele in renamed:
                                new_line.append(get_full_path(renamed[ele]))
                            else:
                                new_line.append(ele)
                        else:
                            new_line.append(ele)
                    if new_line not in list_new_line:
                        list_new_line.append(new_line)
                for row in list_new_line:
                    writer.writerow(row)
    os.replace(temp_file, file)
                
def repair_file():
    result_status = check_status()
    moved = result_status[0]
    renamed = result_status[1]
    list_new_line=[]
    if moved:
        repair_moved(moved)
    if renamed:
        repair_renamed(renamed)

