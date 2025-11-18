import argparse
import subprocess
import os
import csv

file = 'gfs.txt'
temp_file = 'temp.txt'
sha_file = 'sha.txt'

parser = argparse.ArgumentParser(
        prog='gfs',
        epilog='this is a program to help you manage your files',
        )

parser.add_argument('-p', '--print', type=str,
                    help="If tag: print all the tags \n \
                            If *.type (like .mp3 or .pdf): print the tags's file with this type \n \
                            If [tag]: print the files's tag \n \
                            If [file]: print the tags's file \n \
                            ") 
parser.add_argument('-t', '--tag', type=str, nargs='*', help='The tag(s) you want to add')
parser.add_argument('-d', '--delete', type=str, nargs='*', help='The tag(s) you want to delete')
parser.add_argument('-f', '--file', type=str, nargs='*',\
        help='The file(s) you want to one or multiple tags')
parser.add_argument('-m', '--merge', type=str, nargs=2,\
        help='Merge the name of a tag. The first element is the old name and the second the one.')
parser.add_argument('-a', '--arg_tester', nargs='*')
parser.add_argument('-st', '--status')
parser.add_argument('-sha', '--get_sha')

args = parser.parse_args()

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
    return file_path

def find_renamed(obj):
    list_file_dir = os.listdir()
    result = None
    for file_dir in list_file_dir:
        if os.path.isfile(file_dir):
            with open(sha_file, newline='') as f:
                list_file_sha = csv.reader(f)
                for file_sha in list_file_sha:
                    sha_file_dir = get_sha(file_dir)
                    if sha_file_dir == file_sha[1]:
                        result = file_dir
    return result


def write_sha():
    with open(file, newline='') as infile, \
            open(sha_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    if '.' in line[0]:
                        row = get_sha(line[0])
                        new_row = [line[0], row]
                        writer.writerow(new_row)
    
if args.arg_tester:
    result =get_sha(args.arg_tester[0]) 
    print(result)

if args.status:
    with open(file, newline='') as f:
        reader = csv.reader(f)
        for line in reader:
            obj = line[0]
            if '.' in obj:
                exists = os.path.exists(obj)
                if exists:
                    print(f'file {obj} exists')
                else:
                    print(f'file {obj} not here \n')
                    moved = find_moved(obj)
                    if moved:
                        print(f'your file is here: {moved}')
                    else:
                        modified = find_renamed(obj)
                        print(obj,' modified in ',modified)

if args.print :
    arg = None
    if '.' in args.print:
        arg = get_full_path(args.print)
    else:
        arg = args.print
    with open(file, newline='') as f:
        reader = csv.reader(f)
        if 'tag' == args.print:
                for line in reader:
                    if '.' not in line[0]:
                        print(line[0])
        elif 'all' == args.print:
            for line in reader:
                print(line)
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


        else:
            v = False
            for line in reader:
                if arg == line[0]:
                    v = True
                    for obj in line:
                        if obj != line[0]:
                            print(f"~ {obj}")
            if v == False:
                print(f"{arg} is neither a tag nor a file")

if args.tag is not None:
    for tag in args.tag:
        v = True 
        if '.' in tag:
            v = False
            print('A tag cannot contain "."')
        with open(file, 'r', newline='') as f:
            for line in f:
                if tag == line.strip():
                    v = False
                    print(f'{tag} is already a tag')
        if v is True:
            add_obj(tag)

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

if args.file is not None:
    list_tag = []
    list_file = []
    for arg in args.file:
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
