import sys
import os
import readline

builtins = ["echo", "type", "exit", "pwd", "history"]
history_list = []
length_of_history_before_append = 0



#path to history file
histfile = os.environ.get("HISTFILE")
if histfile and os.path.exists(histfile):
    try:
        with open(histfile, "r") as f:
            for line in f:
                h_line = line.rstrip("\r\n")
                if h_line:
                    history_list.append(h_line)
                    if "readline" in sys.modules:
                        readline.add_history(h_line)
    except Exception:
        pass

def get_executables() -> dict[str, str]:
    import os

    path = os.environ.get("PATH", "")
    if path:
        executables = {}
        for dir in path.split(os.pathsep):
            if os.path.isdir(dir):
                for file in os.listdir(dir):
                    full_path = os.path.join(dir, file)
                    if os.access(full_path, os.X_OK) and not os.path.isdir(full_path):
                        executables[file] = full_path
        return executables
    return {}


def run_command(command: str, args: list[str]) -> str:
    import subprocess

    result = subprocess.run([command] + args, capture_output=True, text=True)
    return result.stdout.strip() if result.stdout else result.stderr.strip()

def get_history() -> list[str]:
    return history_list

def get_cwd() -> str:
    import os

    return os.getcwd()


def change_dir(dir: str) -> None:
    import os

    if dir == "~":
        dir = os.environ.get("HOME", "")

    try:
        os.chdir(dir)
    except FileNotFoundError:
        print(f"cd: {dir}: No such file or directory")


def parse(text: str) -> list[str]:
    import shlex

    return shlex.split(text, posix=True) if text else []

AUTOCOMPLETE_ARRAY = builtins.copy()
path = os.environ.get("PATH", "")
directories = path.split(os.pathsep) if path else []
for directory in directories:
    if os.path.exists(directory):
        dir_list = os.listdir(directory)
        AUTOCOMPLETE_ARRAY += dir_list

def completer(text, state):
    
    options = [cmd + " " for cmd in AUTOCOMPLETE_ARRAY if cmd.startswith(text)]
    return options[state] if state < len(options) else None

def display_matches_hook(substitution, matches, longest_match_length):
    print()
    clean_matches = [m.rstrip() for m in matches]
    print("  ".join(clean_matches))
    print("$ " + readline.get_line_buffer(), end="")
    sys.stdout.flush()

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")
readline.set_completer_delims(" \t\n;")
readline.set_completion_display_matches_hook(display_matches_hook)
#uparrow and downarrow should navigate through the history list, so we can use
readline.parse_and_bind("set editing-mode emacs")



def main():
    execs = get_executables()
    while True:
        #sys.stdout.write("$ ") moved this to the input function, since input will automatically print the prompt and wait for user input, so we can just use input("$ ") to get the user input and print the prompt at the same time.
        #mainly did this so that readline can properly handle the user input and the prompt, since readline will automatically move the cursor to the end of the line when the user types something, so if we use sys.stdout.write("$ ") and then call input(), the prompt will be printed before the user input, which can cause issues with readline's handling of the input. By using input("$ "), we ensure that the prompt is printed at the same time as the user input, allowing readline to properly handle the input and the prompt together.
        # the pipe and redirection operators are handled by os.system, so we don't need to implement them here. If the user input contains ">" or "1>", we can just pass the entire command to os.system, lets implement that logic at the beginning of the while loop in main().


        user_input = input("$ ")
        if "|" in user_input:
            os.system(user_input)
            continue

        # implementation of os.system for redirection and pipes.
        # i will get back here later to implement the logic for redirection and pipes, but for now, if the user input contains ">" or "1>", we can just pass the entire command to os.system, since os.system will handle the redirection and pipes for us.

        if ">" in user_input or "1>" in user_input:
            os.system(user_input)
            continue

        parsed_user_input = parse(user_input)
        if not parsed_user_input:
            continue

        command = parsed_user_input[0]
        arguments = parsed_user_input[1:] if len(parsed_user_input) > 1 else []

        if command == "exit":
            history_list.append("exit")
            # write history to file if HISTFILE is set
            if histfile:
                try:
                    with open(histfile, "w") as f:
                        for cmd in history_list:
                            f.write(cmd + "\n")
                except Exception:
                    pass
            break
        elif command == "echo":
            history_list.append(" ".join([command] + arguments))
            print(" ".join(arguments))
        elif command == "history":
            # record this history invocation
            history_list.append(" ".join([command] + arguments))
            if arguments:
                if arguments[0].isdigit():
                    number_of_commands = int(arguments[0])
                    # compute slice start index so we can print absolute indices
                    start = max(0, len(history_list) - number_of_commands)
                    for idx in range(start, len(history_list)):
                        print(f"{idx+1:4d}  {history_list[idx]}")
                elif arguments[0] == "-r":
                    file_to_read = arguments[1] if len(arguments) > 1 else None
                    if file_to_read and os.path.isfile(file_to_read):
                        with open(file_to_read, "r") as f:
                            for line in f:
                                history_line = line.strip("\r\n")
                                if history_line:
                                    history_list.append(history_line)
                                    if "readline" in sys.modules:
                                        readline.add_history(history_line)
                elif arguments[0] == "-w":
                    file_to_write = arguments[1] if len(arguments) > 1 else None
                    if file_to_write:
                        with open(file_to_write, "w") as f:
                            for cmd in history_list:
                                f.write(cmd + "\n")
                elif arguments[0] == "-a":
                    file_to_append = arguments[1] if len(arguments) > 1 else None
                    global length_of_history_before_append
                    if file_to_append:
                        with open(file_to_append, "a") as f:
                            for cmd in history_list[length_of_history_before_append:]:
                                f.write(cmd + "\n")
                            length_of_history_before_append = len(history_list)
            else:
                for idx, cmd in enumerate(get_history(), 0):
                    print(f"{idx+1:4d}  {cmd}")

        elif command == "type":
            provided_command = arguments[0]
            if provided_command in builtins:
                history_list.append(" ".join([command] + [provided_command]))
                print(f"{provided_command} is a shell builtin")
            elif provided_command in execs:
                history_list.append(" ".join([command] + [provided_command]))
                print(f"{provided_command} is {execs[provided_command]}")
            else:
                history_list.append(" ".join([command] + [provided_command]))
                print(f"{provided_command}: not found")
        elif command == "pwd":
            history_list.append("pwd")
            print(get_cwd())
        elif command == "cd":
            history_list.append(" ".join([command] + arguments))
            change_dir(arguments[0])
        elif command in execs:
            history_list.append(" ".join([command] + arguments))
            print(run_command(command, arguments))
        else:
            history_list.append(command)
            print(f"{command}: command not found")





if __name__ == "__main__":
    main()