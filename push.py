#!/usr/bin/env python3
import sys
import subprocess
import os
from datetime import datetime, timezone

DEFAULT_GIT_NAME = "mohamed-zaitoon"
DEFAULT_GIT_EMAIL = "mohamedzaitoon01@gmail.com"

def run(cmd, cwd=None, silent=False, check=False):
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
            # أبين للمستخدم بوضوح إن فيه فشل وأطلع بنفس كود الخطأ
            print("\n‼️ Command failed:", cmd)
            sys.exit(p.returncode)
        return p.returncode, output
    except Exception as e:
        print(f"Error running command {cmd}: {e}")
        if check:
            sys.exit(1)
        return 1, ""

def ensure_git_identity():
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
    """لو الريموت SSH هنحوّله لHTTPS. ولن نحوّل HTTPS إلى SSH نهائيًا."""
    current = get_remote_url()
    if not current:
        # مفيش remote اسمه origin — نضيفه لو اتبعت لنا واحد
        if expected_https:
            run(f"git remote add origin {expected_https}", check=True)
        return

    if current.startswith("git@github.com:"):
        # حوّل SSH إلى HTTPS بنفس الريبو
        # git@github.com:USER/REPO.git -> https://github.com/USER/REPO.git
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
    # امنع تحذير safe.directory
    run(f"git config --global --add safe.directory \"{project_dir}\"", silent=True)

    ensure_git_identity()

    # ثبّت إن الريموت HTTPS (لا تحوّل أبداً لSSH)
    # لو حابب تثبت عنوان HTTPS معيّن، مرره كمتغير بيئة GIT_REMOTE
    expected = os.environ.get("GIT_REMOTE", "").strip()
    ensure_https_remote(expected_https=expected)

    # لو مفيش تغييرات، اخرج بهدوء
    code, changes = run("git status --porcelain", silent=True)
    if code != 0:
        sys.exit(code)
    if not changes.strip():
        print("No changes to commit.")
        sys.exit(0)

    # add + commit
    run("git add -A", check=True)
    utc_time = datetime.now(timezone.utc).strftime("UTC %Y-%m-%d %H:%M:%S")
    commit_msg = f"Commit {utc_time}"
    # في حال لا يوجد شيء للإضافة بعد add -A، commit سيرجع non-zero؛ نعالجه بلطف
    code, _ = run(f'git commit -m "{commit_msg}"', silent=False)
    if code != 0:
        # لو مفيش تغييرات فعلية بعد add، نكمل push عادي
        _, _ = run("git diff --cached --name-only", silent=True)

    # ادفع على نفس الفرع
    branch = git_current_branch()
    # لو معاك PAT وتريد تمنع الـ prompt، تقدر تمرّره في ENV باسم GH_TOKEN
    # سكربت هيستخدم الـ remote الحالي (HTTPS). Git Credential Manager هيكفي عادةً.
    push_cmd = f"git push -u origin {branch}"
    code, _ = run(push_cmd)
    if code != 0:
        print("\n❌ Push failed.")
        print("تلميحات سريعة:")
        print("  • تأكد إن الـ remote HTTPS صحيح:", get_remote_url() or expected or "<no remote>")
        print("  • لو أول مرة، Git هيطلب تسجيل دخول. استخدم Username + PAT بدل الباسورد.")
        print("  • لتعيين الريموت صراحةً:")
        print("      git remote set-url origin https://github.com/mohamed-zaitoon/apputils.git")
        print("  • توليد PAT: GitHub → Settings → Developer settings → Personal access tokens")
        sys.exit(code)

    print("✅ Push completed successfully.")

if __name__ == '__main__':
    main()
