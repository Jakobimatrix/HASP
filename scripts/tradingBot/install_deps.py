#!/usr/bin/env python3
"""
Robust installer:
- Creates venv next to this script
- Installs only missing packages
- Optional upgrades
- Optional Playwright install
"""

import os
import subprocess
import sys
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(BASE_DIR, "venv")

REQUIRED = [
    "requests",
    "beautifulsoup4",
    "pandas",
    "tabulate",
    "playwright",
]


def run(cmd):
    print(">>", " ".join(cmd))
    subprocess.check_call(cmd)


def create_venv():
    if not os.path.isdir(VENV_DIR):
        print(f"Creating virtual environment: {VENV_DIR}")
        run([sys.executable, "-m", "venv", VENV_DIR])
    else:
        print("venv already exists")


def get_venv_python():
    if os.name == "nt":
        return os.path.join(VENV_DIR, "Scripts", "python.exe")
    return os.path.join(VENV_DIR, "bin", "python")


def get_installed_packages(python):
    result = subprocess.check_output(
        [python, "-m", "pip", "freeze"],
        text=True
    )
    return {line.split("==")[0].lower() for line in result.splitlines()}

def ensure_pip(python):
    try:
        subprocess.check_call([python, "-m", "pip", "--version"],
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print("pip missing in venv, installing via ensurepip...")
        run([python, "-m", "ensurepip", "--upgrade"])
        
def recreate_venv():
    print("Recreating broken venv...")
    subprocess.check_call(["rm", "-rf", VENV_DIR])
    create_venv()

def install_packages(python, upgrade=False):
    print("Upgrading pip...")
    try:
        ensure_pip(venv_python)
    except Exception:
        recreate_venv()
        venv_python = get_venv_python()
        ensure_pip(venv_python)
        
    run([python, "-m", "pip", "install", "--upgrade", "pip"])

    installed = get_installed_packages(python)

    to_install = []
    for pkg in REQUIRED:
        if upgrade or pkg.lower() not in installed:
            to_install.append(pkg)

    if not to_install:
        print("All packages already installed.")
        return

    print("Installing:", ", ".join(to_install))
    run([python, "-m", "pip", "install", *to_install])


def install_playwright(python, skip=False):
    if skip:
        print("Skipping Playwright browser install.")
        return

    print("Ensuring Playwright browsers are installed...")
    run([python, "-m", "playwright", "install"])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--upgrade", action="store_true",
                        help="Upgrade all packages")
    parser.add_argument("--skip-playwright", action="store_true",
                        help="Skip browser install")
    return parser.parse_args()


def main():
    args = parse_args()

    create_venv()
    venv_python = get_venv_python()

    install_packages(venv_python, upgrade=args.upgrade)
    install_playwright(venv_python, skip=args.skip_playwright)

    print("\nSetup complete.")
    print(f"Use: {venv_python} your_script.py")


if __name__ == "__main__":
    main()

