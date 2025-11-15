import os
import csv
import cmd

def main():
    print("Hello from gfs!")


def get_files_info(directory="."):

    print("Result for current directory:")

    for f in os.listdir(directory):
        fp = directory + "/" + f
        directory_content = f"- {f}: file_size={os.path.getsize(fp)} bytes, is_dir={os.path.isdir(fp)}"
        print(f"{directory_content}")


class MyCLI(cmd.Cmd):
    prompt = 'GFS ~ '
    intro = 'Welcome to GFS. Type "help" for available commands.'
    file = 'GFS.csv'

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_help(self, line):
        print("This is an application to manage your files like a graph system.")

    def do_print(self, arg):
        with open(self.file, 'r') as f:
            for line in f:
                if arg == 'all':
                    print(line)

    def do_tag(self, tag):
        with open(self.file, 'r') as f:
            for line in f:
                if ('t$ ' + tag) == line:
                    print(f't$ {tag} is a tag')
                    break
                else:
                    with open(self.file, 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(['t$ '+tag])
                    break

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == "__main__":
    main()
    # get_files_info()
    MyCLI().cmdloop()
