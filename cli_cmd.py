import os
import csv
import cmd

class MyCLI(cmd.Cmd):
    prompt = 'GFS ~ '
    intro = 'Welcome to GFS. Type "help" for available commands.'
    file = 'GFS.csv'
    temp_file = 'temp.csv'

    def do_help(self, line):
        print("This is an application to manage your files like a graph system.")

    def do_print(self, arg):
        with open(self.file, 'r') as f:
            for line in f:
                if arg == 'all':
                    print(line)

    def do_tag(self, tag):
        def add_tag(tag):
            with open(self.file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([tag])
        with open(self.file, 'r', newline='') as f:
            for line in f:
                if tag == line.strip():
                    print(f"{tag} is already a tag.")
                    return
            add_tag(tag)

    def do_delete(self, arg):
        with open(self.file, newline='') as infile, \
                open(self.temp_file, 'w', newline='') as outfile:
                    reader = csv.reader(infile)
                    writer = csv.writer(outfile)
                    for line in reader:
                        obj = ''.join(line)
                        if obj != arg:
                            writer.writerow(line)
        os.replace(self.temp_file, self.file)

    def do_add(self, arg):
        file = os.getcwd() + '/' + arg
        # check if file exists

    def do_quit(self, line):
        return True

if __name__ == "__main__":
    MyCLI().cmdloop()
