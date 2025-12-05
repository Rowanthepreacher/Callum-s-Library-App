"""
Build script to create a standalone executable for Callum's Library App
"""

import subprocess
import sys
from pathlib import Path

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("Building Callum's Library Management System...")
    print("-" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # PyInstaller command - use sys.executable to call it as a module
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=CallumsLibrary",
        "--windowed",  # No console window
        "--onefile",   # Single executable
        "--icon=NONE",  # Can add an icon later if desired
        "--add-data=README.md;.",  # Include README
        "library_app.py"
    ]
    
    print("\nRunning PyInstaller...")
    print(" ".join(cmd))
    print()
    
    try:
        subprocess.check_call(cmd)
        print("\n" + "=" * 50)
        print("BUILD SUCCESSFUL!")
        print("=" * 50)
        print("\nYour executable is located at:")
        print(f"  dist/CallumsLibrary.exe")
        print("\nYou can now:")
        print("  1. Copy CallumsLibrary.exe to any location")
        print("  2. Double-click to run (no Python required)")
        print("  3. The database and covers folder will be created")
        print("     in the same directory as the executable")
        print("\nNote: The executable may take a moment to start on first run")
        
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print("BUILD FAILED!")
        print("=" * 50)
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure all dependencies are installed")
        print("  2. Check for any error messages above")
        print("  3. Try running: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    # Change to script directory
    script_dir = Path(__file__).parent
    import os
    os.chdir(script_dir)
    
    build_executable()
