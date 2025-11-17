import argparse
import os
import csv

file = 'gfs.txt'
temp_file = 'temp.txt'

parser = argparse.ArgumentParser(
        prog='gfs',
        epilog='this is a program to help you manage your files',
        )

parser.add_argument('-p', '--print') 
parser.add_argument('-t', '--tag', type=str, nargs='*', help='The tag(s) you want to add')
parser.add_argument('-d', '--delete', type=str, nargs='*', help='The tag(s) you want to delete')
parser.add_argument('-f', '--file', type=str, nargs='*', help='The file(s) you want to one or multiple tags')
parser.add_argument('-a', '--arg_tester', nargs='*')

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

if args.arg_tester:
    for arg in args.arg_tester:
        print(f'- {arg}')
        print(get_full_path(arg))
    # print(args.arg_tester)

if args.print :
    with open(file, newline='') as f:
        for line in f:
            print(line)

if args.tag is not None:
    for tag in args.tag:
        v = True 
        with open(file, 'r', newline='') as f:
            for line in f:
                if tag == line.strip():
                    v = False
                    print(f'{tag} is already a tag')
        if v is True:
            add_obj(tag)

if args.delete is not None:
    for tag in args.delete:
        if '.' in tag:
            print(f'{arg} is not a tag')
        else:
            with open(file, newline='') as infile, \
                    open(temp_file, 'w', newline='') as outfile:
                        reader = csv.reader(infile)
                        writer = csv.writer(outfile)
                        for line in reader:
                            temp_list = []
                            obj = line[0]
                            if '.' in obj:
                                for obj_item in line:
                                    print(obj_item)
                                    if obj_item not in args.delete:
                                        print(obj_item)
                                        temp_list.append(obj_item)
                                if temp_list:
                                    writer.writerow(temp_list)
#           os.replace(temp_file, file)

# NOT WORKS, NEED TO DELETE THE TAG IN THE FILE LIST
    with open(file, newline='') as infile, \
            open(temp_file, 'w', newline='') as outfile:
                reader = csv.reader(infile)
                writer = csv.writer(outfile)
                for line in reader:
                    obj = line[0]
                    if obj not in args.delete:
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
