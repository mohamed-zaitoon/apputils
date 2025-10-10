#!/usr/bin/env python3
import sys
import subprocess
import os
import platform
from datetime import datetime, timezone

DEFAULT_GIT_NAME = "mohamed-zaitoon"
DEFAULT_GIT_EMAIL = "mohamedzaitoon01@gmail.com"

def run(cmd, cwd=None, silent=False, check=False):
    """Run a shell command and return (exit_code, output)."""
    try:
        p = subprocess.Popen(
            cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            shell=True, universal_newlines=True
        )
        out = []
        for line in p.stdout:
            if not silent:
                print(line, end="")
            out.append(line)
        p.wait()
        output = "".join(out)
        if check and p.returncode != 0:
            print("\n‼️ Command failed:", cmd)
            sys.exit(p.returncode)
        return p.returncode, output
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        if check:
            sys.exit(1)
        return 1, ""

def detect_system():
    """Detect operating system name for logging."""
    system = platform.system().lower()
    if "linux" in system:
        if "ANDROID_ROOT" in os.environ or "TERMUX_VERSION" in os.environ:
            return "Android (Termux)"
        return "Linux"
    elif "windows" in system:
        return "Windows"
    elif "darwin" in system:
        return "macOS"
    else:
        return "Unknown"

def ensure_git_identity():
    """Ensure git global user.name and user.email are set."""
    _, name = run("git config --global user.name", silent=True)
    _, email = run("git config --global user.email", silent=True)
    if not name.strip():
        run(f"git config --global user.name \"{DEFAULT_GIT_NAME}\"", check=True)
    if not email.strip():
        run(f"git config --global user.email \"{DEFAULT_GIT_EMAIL}\"", check=True)

def get_remote_url():
    code, url = run("git remote get-url origin", silent=True)
    return url.strip() if code == 0 else ""

def ensure_https_remote(expected_https=None):
    """Ensure remote 'origin' is HTTPS."""
    current = get_remote_url()
    if not current:
        if expected_https:
            run(f"git remote add origin {expected_https}", check=True)
        return
    if current.startswith("git@github.com:"):
        tail = current.split("git@github.com:")[-1]
        if tail.endswith(".git"):
            tail = tail[:-4]
        https_url = f"https://github.com/{tail}.git"
        run(f"git remote set-url origin {https_url}", check=True)

def git_current_branch():
    _, br = run("git rev-parse --abbrev-ref HEAD", silent=True)
    return (br or "").strip() or "main"

def main():
    project_dir = os.getcwd()
    system_name = detect_system()

    run(f"git config --global --add safe.directory \"{project_dir}\"", silent=True)
    ensure_git_identity()

    expected = os.environ.get("GIT_REMOTE", "").strip()
    ensure_https_remote(expected_https=expected)

    print(f"\n🖥️ Detected system: {system_name}")
    print("🔄 Checking for local changes...")
    code, changes = run("git status --porcelain", silent=True)
    has_local_changes = bool(changes.strip())

    if has_local_changes:
        print("💾 Stashing local uncommitted changes...")
        run("git stash save --include-untracked 'Auto stash before pull'", check=True)

    print("\n🌍 Fetching latest changes from remote...")
    run("git fetch --all", check=True)

    branch = git_current_branch()
    print(f"📦 Current branch: {branch}")

    print("\n⬇️ Pulling latest changes with rebase...")
    code, _ = run(f"git pull --rebase origin {branch}")

    if code != 0:
        print("\n❌ Pull (rebase) failed.")
        print("Try resolving conflicts manually, then run:")
        print("  git rebase --continue")
        sys.exit(code)

    if has_local_changes:
        print("\n♻️ Restoring stashed local changes...")
        code, _ = run("git stash pop")
        if code != 0:
            print("\n⚠️ Conflicts occurred while restoring local changes.")
            print("Please resolve them manually and commit your fixes.")
            sys.exit(1)

    utc_time = datetime.now(timezone.utc).strftime("UTC %Y-%m-%d %H:%M:%S")
    print(f"\n✅ Pull (with rebase) completed successfully at {utc_time}")
    print(f"📡 Device: {system_name}")
    sys.exit(0)

if __name__ == '__main__':
    main()
