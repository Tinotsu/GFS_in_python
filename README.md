# gfs — File and Tag Manager for Linux

## Presentation

This is my first program in Python, so it may contain some bugs.
I made this program to practice Python for a Boot.dev personal project, taking inspiration from [tsmu.org](https://tsmu.org).
GFS stands for Graph File System — the idea is to search files using their attributes.
If you have any remarks or suggestions, feel free to tell me!
:)

`gfs` is a lightweight command-line tool for managing files and tagging them.
It keeps a persistent database of files, tags, and SHA256 checksums so it can detect moved, renamed, or lost files.

The database is **global** and stored in:

```
~/.config/gfs/gfs.txt
~/.config/gfs/sha.txt
```

You can run `gfs` from **any directory** on your machine.

---

## Requirements

* Linux system
* Python 3 installed
* `sha256sum` and `find` available (standard on all Linux distributions)

---

## Installation

1. Download `gfs.py`
2. Move it into your user binary directory:

   ```
   mv gfs.py ~/.local/bin/
   ```
3. Rename it to `gfs`:

   ```
   mv ~/.local/bin/gfs.py ~/.local/bin/gfs
   ```
4. Make it executable:

   ```
   chmod +x ~/.local/bin/gfs
   ```

If `~/.local/bin` is in your `$PATH` (default on most distros), `gfs` is now available everywhere:

```
gfs -h
```

---

## How the Database Works

`gfs` uses permanent storage in:

```
~/.config/gfs/
```

The script automatically creates this directory and the required files if they do not exist.

* **gfs.txt** contains entries in CSV format
  Each line looks like:

  ```
  file_or_tag, value1, value2, ...
  ```

* Entries containing a dot (`.`) are treated as **files**

* Entries without a dot are treated as **tags**

* **sha.txt** stores pairs:

  ```
  <filepath>, <sha256>
  ```

  and is regenerated automatically when needed.

---

## Commands

### Print (`-p`, `--print`)

Show information stored in the database.

```
gfs -p all        # print all database content
gfs -p tag        # list all tags
gfs -p file       # list all tracked files
gfs -p .mp3       # list .mp3 files with their tags
gfs -p somefile.pdf
```

Behavior:

* File names are matched by extension or by filename
* Tags are listed for each file
* Error printed if argument is unknown

---

### Tag (`-t`, `--tag`)

Assign tags to files.

```
gfs -t file1 file2 TAG1 TAG2
```

Rules:

* Arguments containing `.` are treated as **files**
* Arguments without `.` are **tags**
* Missing files or tags are automatically added to the database

Example:

```
gfs -t song.mp3 music chill
```

---

### Delete (`-d`, `--delete`)

Remove tags.

Two modes:

1. Delete a tag globally:

   ```
   gfs -d tag1 tag2
   ```

2. Delete tags only from specific file(s):

   ```
   gfs -d file1 tag1 tag2
   ```

Files must contain a dot.

---

### Merge (`-m`, `--merge`)

Rename a tag.

```
gfs -m old_tag new_tag
```

* Works only for tags
* Files cannot be merged
* Fails if the old tag does not exist

---

### Status (`-s`, `--status`)

Analyze the state of all stored files:

```
gfs -s
```

Reports:

* **moved** — file path incorrect, but file found elsewhere
* **renamed** — file name changed but SHA256 matches
* **okay** — file exists where expected
* **lost** — file not found anywhere

---

### Repair (`-r`, `--repair`)

Automatically fix moved and renamed files.

```
gfs -r
```

* Updates paths of moved files
* Updates filenames using SHA256
* Does not repair files that were *both* moved and renamed

---

### Clean (`-c`, `--clean`)

Remove entries for files that are lost or deleted.

```
gfs -c
```

Also regenerates `sha.txt`.

---

## Notes

* The database is **global** and always stored in `~/.config/gfs/`
* You can run `gfs` from **any directory**
* No root permissions required
* Use extensions (`.pdf`, `.mp3`, etc.) to filter files

---

## Example Workflow

```
gfs -t todo.txt work important
gfs -p file
gfs -s
gfs -r
gfs -c
```

---

## License

You may modify or redistribute this program freely.

