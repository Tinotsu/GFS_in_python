#!/usr/bin/env python3

import argparse
import subprocess
import os
import csv

BASE = os.path.expanduser("~/.config/gfs/")
file = os.path.join(BASE, "gfs.txt")
sha_file = os.path.join(BASE, "sha.txt")
temp_file = os.path.join(BASE, "temp.txt")

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

def clean_file():
    result = check_status()
    lost = result[3]
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    new_line = []
                    if line[0] not in lost:
                        for obj in line:
                            if obj not in lost:
                                new_line.append(obj)
                        writer.writerow(new_line)
    os.replace(temp_file, file)
    write_sha()

def check_status():
    moved_file = {}
    renamed_file = {}
    okay_file = []
    lost_file = []
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
                            lost_file.append(obj)
    return moved_file, renamed_file, okay_file, lost_file

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

parser = argparse.ArgumentParser(
    prog='gfs',
    epilog='Manage files and tags stored in gfs.txt.',
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    '-p', '--print', type=str,
    help=(
        "Display information from the gfs database:\n"
        "  all       → print every line from gfs.txt\n"
        "  tag       → list all tags (entries whose first element has no '.')\n"
        "  file      → list all files (entries whose first element contains a '.')\n"
        "  *.ext      → list all files with this extension and their tags\n"
        "  filename  → show the stored path and tags for this file\n"
        "If the argument is not a file, not a tag, and not a known type, an error is printed."
    )
)

parser.add_argument(
    '-d', '--delete', type=str, nargs='*',
    help=(
        "Delete tags. Behavior depends on arguments:\n"
        "  delete TAG1 TAG2 ...     → remove these tags everywhere\n"
        "  delete file1 TAG ...     → remove tags only from specified file(s)\n"
        "File arguments must contain a '.', and only tags are removed."
    )
)

parser.add_argument(
    '-t', '--tag', type=str, nargs='*',
    help=(
        "Assign tags to files. Mixed input allowed:\n"
        "  gfs -t file1 file2 TAG1 TAG2\n"
        "Files are detected by '.', tags by absence of '.'.\n"
        "Missing files or tags are automatically created in gfs.txt."
    )
)

parser.add_argument(
    '-m', '--merge', type=str, nargs=2,
    help=(
        "Rename a tag:\n"
        "  gfs -m old_tag new_tag\n"
        "Files cannot be merged (arguments containing '.' are rejected).\n"
        "Fails if old_tag does not exist."
    )
)

parser.add_argument(
    '-s', '--status', action='store_true',
    help=(
        "Check current state of all files in gfs.txt:\n"
        "  moved   → path stored in gfs.txt is wrong, but file exists elsewhere\n"
        "  renamed → filename changed but SHA256 matches a known entry\n"
        "  okay    → file exists at stored path\n"
        "  lost    → file does not exist anywhere"
    )
)

parser.add_argument(
    '-r', '--repair', action='store_true',
    help=(
        "Fix moved and renamed files.\n"
        "Moved files: update path.\n"
        "Renamed files: update file name using SHA256.\n"
        "Does not handle cases where a file was both moved AND renamed."
    )
)

parser.add_argument(
    '-c', '--clean', action='store_true',
    help=(
        "Remove lost or deleted files from the database and regenerate sha.txt."
    )
)
 
args = parser.parse_args()

def init():
    if not os.path.isdir(BASE):
        os.makedirs(BASE, exist_ok=True)
    required = [file, sha_file]
    for f in required:
        if not os.path.isfile(f):
            with open(f,'w') as fp:
                pass
init()
if args.repair:
    repair_file()

if args.clean:
    clean_file()

if args.status:
    result_status = check_status()
    if result_status[0]:
        moved = result_status[0]
        print(f"files moved:")
        for wrong, actual in moved.items():
            print(f"- {wrong} is actually at {actual}")
    if result_status[1]:
        renamed = result_status[1]
        print(f"files renamed:")
        for wrong, name_actual in renamed.items():
            name_wrong = get_file_name(wrong)
            print(f"- {name_wrong} is now named {name_actual}")
    if result_status[2]:
        okay = result_status[2]
        print(f"files okay:")
        for file in okay:
            print(f"- {file}")
    if result_status[3]:
        lost = result_status[3]
        print(f"Lost or deleted files:")
        for file in lost:
            print(f"- {file}")

if args.print :
    arg = args.print
    with open(file, newline='') as f:
        reader = csv.reader(f)
        if 'tag' == args.print:
                for line in reader:
                    if '.' not in line[0]:
                        print(line[0])
        elif 'file' == args.print:
            for line in reader:
                if '.' in line[0]:
                    print(line[0])
        elif 'all' == args.print:
            for line in reader:
                print(', '.join(line))
        elif '*.' in args.print:
            ext=get_ext(args.print)
            for line in reader:
                obj = line[0]
                if '.' in obj:
                    ext_obj=get_ext(obj)
                    if ext_obj == ext:
                        tag_list = []
                        for tag in line:
                            if tag != obj:
                                tag_list.append(tag)
                        print(f"{obj}: {', '.join(tag_list)}")
        elif '.' in arg and get_full_path(arg) is None:
            print(f'{arg} is not a file')
        elif '.' in arg:
            v = False
            for line in reader:
                if get_file_name(arg) == get_file_name(line[0]):
                    v = True
                    print(f'Path: {line[0]}')
                    print('Tag:')
                    for obj in line:
                        if obj != line[0]:
                            print(f"    ~ {obj}")
            if v is False:
                print(f"{arg} has no tag")
        else:
            v = False
            for line in reader:
                if arg == line[0]:
                    v = True
                    for item in line:
                        if item != line[0]:
                            print('~',item)
            if v == False:
                print(f"{arg} is neither a tag nor a file")

if args.merge is not None:
    v = True
    for arg in args.merge:
        if '.' in arg:
            v = False
            print("You can't merge file")
    with open(file, newline='') as f:
        reader = csv.reader(f)
        arg_exists = False
        for line in reader:
            if line[0] == args.merge[0]:
                arg_exists = True
        if arg_exists is False:
            v = False
            print(f"The tag {args.merge[0]} doesn't exists")
    if v:
        with open(file, newline='') as infile, \
                open(temp_file, 'w', newline='') as outfile:
                    reader = csv.reader(infile)
                    writer = csv.writer(outfile)
                    for line in reader:
                        obj = args.merge[0]
                        temp_line=[]
                        for row_obj in line:
                            if row_obj == obj:
                                temp_line.append(args.merge[1])
                            else:
                                temp_line.append(row_obj)
                        writer.writerow(temp_line)
        os.replace(temp_file, file)

if args.delete is not None:
    temp_list = []
    list_full_path = []
    delete_everywhere = True
    for arg in args.delete:
        if '.' in arg:
            delete_everywhere = False
            list_full_path.append(get_full_path(arg))
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    obj = line[0]
                    if '.' in obj:
                        if delete_everywhere or obj in list_full_path:
                            temp_row=[]
                            for row_obj in line:
                                if row_obj not in args.delete:
                                    temp_row.append(row_obj)
                            if len(temp_row) > 1:
                                temp_list.append(temp_row)
                        else:
                            temp_list.append(line)
                    elif delete_everywhere:
                        if obj not in args.delete:
                            temp_list.append(line)
                        else:
                            print(f'{obj} to delete')
                    elif line[0] in args.delete:
                        temp_row=[]
                        for row_obj in line:
                            if row_obj not in list_full_path:
                                temp_row.append(row_obj)
                        if len(temp_row) > 0 and temp_row not in temp_list:
                            temp_list.append(temp_row)
                    else:
                        temp_list.append(line)
                for line in temp_list:
                    writer.writerow(line)
    os.replace(temp_file, file)

if args.tag is not None:
    list_tag = []
    list_file = []
    for arg in args.tag:
        if '.' in arg and get_full_path(arg) is None:
            print(f'{arg} is not a file')
        else:
            if '.' in arg:# it's a file
                arg = get_full_path(arg)
            v = True
            with open(file, newline='') as f:
                reader = csv.reader(f)
                for line in reader:
                    obj_line = line[0]
                    if arg == obj_line:
                        v = False
                if v == True:
                    add_obj(arg)
                if '.' in arg:# it's a file
                    list_file.append(arg)
                else:# it's a tag
                    list_tag.append(arg)
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for i, line in enumerate(reader):
                    if line[0] in list_tag:
                        for obj in list_file:
                            if obj not in line:
                                line.append(obj)
                    elif line[0] in list_file:
                        for tag in list_tag:
                            if tag not in line:
                                line.append(tag)
                    writer.writerow(line)
    os.replace(temp_file, file)
    write_sha()
