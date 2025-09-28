#!/usr/bin/env python3
import shutil
import sys
import subprocess
import os
import re
from datetime import datetime, timezone

DEFAULT_GIT_NAME = "mohamed-zaitoon"
DEFAULT_GIT_EMAIL = "mohamedzaitoon01@gmail.com"

def run_command(cmd, cwd=None, silent=False):
    try:
        process = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            shell=True, universal_newlines=True
        )
        output = ""
        for line in process.stdout:
            if not silent:
                print(line, end='')
            output += line
        process.wait()
        return process.returncode, output
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        return 1, ""

def ensure_git_identity():
    _, name = run_command("git config --global user.name", silent=True)
    _, email = run_command("git config --global user.email", silent=True)
    if not name.strip():
        run_command(f"git config --global user.name '{DEFAULT_GIT_NAME}'")
    if not email.strip():
        run_command(f"git config --global user.email '{DEFAULT_GIT_EMAIL}'")

def convert_https_to_ssh(https_url):
    match = re.match(r"https://github\.com/(.+?)/(.+?)(\.git)?$", https_url)
    if match:
        username = match.group(1)
        repo = match.group(2)
        return f"git@github.com:{username}/{repo}.git"
    return None

def check_and_fix_remote(project_dir):
    _, remote_url = run_command("git remote get-url origin", cwd=project_dir, silent=True)
    remote_url = remote_url.strip()
    if remote_url.startswith("https://"):
        ssh_url = convert_https_to_ssh(remote_url)
        if ssh_url:
            run_command(f"git remote set-url origin {ssh_url}", cwd=project_dir)

def main():
    project_dir = os.getcwd()
    run_command(f"git config --global --add safe.directory {project_dir}")
    ensure_git_identity()
    check_and_fix_remote(project_dir)

    _, output = run_command("git status --porcelain", cwd=project_dir, silent=True)
    if not output.strip():
        print("No changes to commit.")
        sys.exit(0)

    run_command("git add -A", cwd=project_dir)
    utc_time = datetime.now(timezone.utc).strftime("UTC %Y-%m-%d %H:%M:%S")
    commit_msg = f"Commit {utc_time}"
    run_command(f'git commit -m "{commit_msg}"', cwd=project_dir)
    run_command("git push origin HEAD", cwd=project_dir)
    print("Push completed.")

if __name__ == '__main__':
    main()
