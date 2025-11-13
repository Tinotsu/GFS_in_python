import os
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

    def do_hello(self, line):
        """Print a greeting."""
        print("Hello, World!")

    def do_help(self, line):
        print("This is an application to manage your files like a graph system.")

    def do_quit(self, line):
        """Exit the CLI."""
        return True

if __name__ == "__main__":
    main()
    # get_files_info()
    MyCLI().cmdloop()
