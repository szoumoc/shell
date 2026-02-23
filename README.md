# Custom Python Shell

A minimal Unix-like shell implemented in Python.

## Features

### Built-in Commands

- `echo` – Print arguments to standard output  
- `type` – Identify whether a command is a shell builtin or an executable  
- `exit` – Exit the shell and write history (if configured)  
- `pwd` – Print current working directory  
- `cd` – Change current working directory  
- `history` – Display and manage command history  

### External Commands

Any executable available in the system `PATH` can be executed:

```bash
$ ls
$ python3 script.py
$ git status