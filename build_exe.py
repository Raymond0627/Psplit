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
        "--name=Folio",
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
        print("Executable generated in: dist/Folio/Folio.exe")
        print("=" * 60)

        # Look for Inno Setup compiler
        iscc_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            shutil.which("ISCC.exe") or ""
        ]
        iscc = next((p for p in iscc_paths if p and os.path.exists(p)), None)
        if iscc and os.path.exists("installer.iss"):
            print("\nFound Inno Setup compiler! Creating setup installer (.exe)...")
            res_iscc = subprocess.run([iscc, "installer.iss"])
            if res_iscc.returncode == 0:
                print("Setup installer created in: dist/installer/Folio_Setup.exe")
            else:
                print("Inno Setup compilation failed with code:", res_iscc.returncode)
    else:
        print("\nBUILD FAILED with returncode:", res.returncode)

if __name__ == "__main__":
    build()
