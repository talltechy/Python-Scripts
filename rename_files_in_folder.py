import logging
import logging.handlers
import os
import platform
import re
import subprocess
import sys


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    file_handler = logging.FileHandler('file_renamer.log')
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    if platform.system() == 'Linux':
        try:
            syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')
            syslog_handler.setFormatter(formatter)
            root_logger.addHandler(syslog_handler)
        except FileNotFoundError:
            pass
    elif platform.system() == 'Darwin':
        try:
            syslog_handler = logging.handlers.SysLogHandler(address='/var/run/syslog')
            syslog_handler.setFormatter(formatter)
            root_logger.addHandler(syslog_handler)
        except FileNotFoundError:
            pass
    elif platform.system() == 'Windows':
        try:
            nt_event_log_handler = logging.handlers.NTEventLogHandler("FileRenamer")
            nt_event_log_handler.setFormatter(formatter)
            root_logger.addHandler(nt_event_log_handler)
        except ImportError:
            print("win32api not found, please install it using: pip install pywin32", file=sys.stderr)
            user_input = input("Do you want to install the required package now? (yes/no): ").lower()
            while user_input not in ['yes', 'no']:
                user_input = input("Do you want to install the required package now? (yes/no): ").lower()

            if user_input == 'yes':
                subprocess.run([sys.executable, "-m", "pip", "install", "pywin32"])
            else:
                print("Please install the required package manually and run the script again.")
                sys.exit(1)


def sanitize_input(input_string):
    return input_string.strip()

def is_valid_directory(directory):
    sanitized_dir = sanitize_input(directory)
    if not os.path.isdir(sanitized_dir):
        print("Invalid directory. Please enter a valid directory.")
        return False, sanitized_dir
    return True, sanitized_dir

def is_valid_extension(extension):
    sanitized_ext = sanitize_input(extension)
    extension_pattern = r'^\.\w+$'
    if not re.match(extension_pattern, sanitized_ext):
        print("Invalid file extension. Please enter a valid file extension.")
        return False, sanitized_ext
    return True, sanitized_ext

def add_dot_if_needed(extension):
    if not extension.startswith('.'):
        extension = '.' + extension
    return extension

def get_user_input():
    is_valid, startdir = is_valid_directory(input("Enter start directory: "))
    while not is_valid:
        is_valid, startdir = is_valid_directory(input("Enter start directory: "))

    is_valid, old_extension = is_valid_extension(add_dot_if_needed(input('Enter file extension to rename: ')))
    while not is_valid:
        is_valid, old_extension = is_valid_extension(add_dot_if_needed(input('Enter file extension to rename: ')))

    is_valid, new_extension = is_valid_extension(add_dot_if_needed(input("Enter new file extension: ")))
    while not is_valid:
        is_valid, new_extension = is_valid_extension(add_dot_if_needed(input("Enter new file extension: ")))

    ignore_default_exclusions = input("Ignore default exclusions? (yes/no): ").lower()
    while ignore_default_exclusions not in ['yes', 'no']:
        ignore_default_exclusions = input("Ignore default exclusions? (yes/no): ").lower()

    ignore_default_exclusions = ignore_default_exclusions == 'yes'

    if not ignore_default_exclusions:
        custom_exclusions = input("Enter your own comma-separated exclusions, or leave blank for none: ").split(',')

        if custom_exclusions != ['']:
            overwrite_existing_exclusions = input("Overwrite existing exclusions? (yes/no): ").lower()
            while overwrite_existing_exclusions not in ['yes', 'no']:
                overwrite_existing_exclusions = input("Overwrite existing exclusions? (yes/no): ").lower()

            overwrite_existing_exclusions = overwrite_existing_exclusions == 'yes'
        else:
            overwrite_existing_exclusions = False

    else:
        custom_exclusions = []
        overwrite_existing_exclusions = False

    return startdir, old_extension, new_extension, ignore_default_exclusions, custom_exclusions, overwrite_existing_exclusions

def rename_files(startdir, old_extension, new_extension, ignore_default_exclusions, custom_exclusions, overwrite_existing_exclusions):
    default_exclude = [
        '.git', '.idea', 'target', '.pytest_cache', '.vscode', '__pycache__',
        'node_modules', '.DS_Store', '.svn', '.hg', 'CVS'
    ]

    if ignore_default_exclusions:
        exclude = []
    elif overwrite_existing_exclusions:
        exclude = custom_exclusions
    else:
        exclude = default_exclude + custom_exclusions

    for root, dirs, files in os.walk(startdir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for filename in files:
            if filename.endswith(old_extension):
                infilename = os.path.join(root, filename)
                newname = os.path.join(root, filename.replace(old_extension, new_extension))

                if not os.access(infilename, os.W_OK):
                    message = f"Permission denied to modify file: {infilename}"
                    print(message)
                    logging.warning(message)
                    continue

                try:
                    os.rename(infilename, newname)
                    message = f"Renamed file: {infilename} to {newname}"
                    print(message)
                    logging.info(message)
                except OSError as e:
                    message = f"Error occurred: {e}"
                    print(message)
                    logging.error(message)

def main():
    setup_logging()
    startdir, old_extension, new_extension, ignore_default_exclusions, custom_exclusions, overwrite_existing_exclusions = get_user_input()
    logging.info(f"Starting directory: {startdir}")
    logging.info(f"Old file extension: {old_extension}")
    logging.info(f"New file extension: {new_extension}")
    logging.info(f"Ignore default exclusions: {ignore_default_exclusions}")
    logging.info(f"Custom exclusions: {custom_exclusions}")
    logging.info(f"Overwrite existing exclusions: {overwrite_existing_exclusions}")
    rename_files(startdir, old_extension, new_extension, ignore_default_exclusions, custom_exclusions, overwrite_existing_exclusions)


if __name__ == "__main__":
    main()
