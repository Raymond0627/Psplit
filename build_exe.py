"""PyInstaller build script to create standalone Windows executable."""

import os
import sys
import subprocess
import shutil
import customtkinter

def build():
    ctk_path = os.path.dirname(customtkinter.__file__)
    print(f"CustomTkinter location: {ctk_path}")

    # Separator for PyInstaller --add-data on Windows is ';'
    add_data_ctk = f"{ctk_path};customtkinter"
    add_data_icon_ico = "icon.ico;."
    add_data_icon_png = "icon.png;."

    excludes = [
        "torch", "torchvision", "torchaudio", 
        "pandas", "scipy", "matplotlib", 
        "IPython", "jupyter", "notebook",
        "pytest", "unittest"
    ]
    exclude_args = []
    for ex in excludes:
        exclude_args.extend(["--exclude-module", ex])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=Lumeed_QSplit",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--icon=icon.ico",
        f"--add-data={add_data_ctk}",
        f"--add-data={add_data_icon_ico}",
        f"--add-data={add_data_icon_png}",
        "--collect-all=zxingcpp",
        "--collect-all=fitz",
        *exclude_args,
        "main.py"
    ]

    print("\nRunning PyInstaller command:")
    print(" ".join(cmd))
    print("\nBuilding executable... This may take a minute...")
    
    res = subprocess.run(cmd)
    if res.returncode == 0:
        print("\n" + "=" * 60)
        print("BUILD SUCCESSFUL!")
        print("Executable generated in: dist/Lumeed_QSplit/Lumeed_QSplit.exe")
        print("=" * 60)
    else:
        print("\nBUILD FAILED with returncode:", res.returncode)

if __name__ == "__main__":
    build()
