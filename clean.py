#!/usr/bin/env python3
import os
import shutil

def remove_dir(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
        print(f"Removed: {path}")

def remove_file(path):
    if os.path.isfile(path):
        os.remove(path)
        print(f"Removed: {path}")

def find_and_remove_iml_files():
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.iml'):
                os.remove(os.path.join(root, file))

def remove_dot_dirs():
    for entry in os.listdir('.'):
        if entry.startswith('.') and os.path.isdir(entry) and entry != '.git':
            remove_dir(entry)

def main():
    remove_dir('.gradle')
    remove_dir('.kotlin')
    remove_dir('build')
    remove_dir('library/build')
    remove_dir('app/.cxx')
    remove_dir('app/build')
    remove_file('local.properties')
    remove_file('versioncode.properties')
    remove_dir('.idea')
    find_and_remove_iml_files()
    remove_dot_dirs()
    print("Clean completed.")

if __name__ == '__main__':
    main()
