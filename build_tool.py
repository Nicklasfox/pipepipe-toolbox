#!/usr/bin/env python3
"""
Build script for PipePipe Metadata Tool
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    try:
        import tkinter
        print("✓ tkinter is available")
    except ImportError:
        print("✗ tkinter is not available")
        return False
    
    try:
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ yt-dlp is available: {result.stdout.strip()}")
        else:
            print("✗ yt-dlp is not working properly")
            return False
    except FileNotFoundError:
        print("✗ yt-dlp is not installed")
        return False
    
    try:
        import PyInstaller
        print(f"✓ PyInstaller is available")
    except ImportError:
        print("✗ PyInstaller is not installed")
        print("Install with: pip install pyinstaller")
        return False
    
    return True

def clean_build():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  Removed: {dir_name}")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Run PyInstaller
    cmd = ['pyinstaller', 'pipepipe_tool.spec']
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("✗ Build failed!")
        print("Error output:")
        print(result.stderr)
        return False
    
    print("✓ Build completed successfully!")
    
    # Check if executable was created
    exe_path = os.path.join('dist', 'PipePipe_Metadata_Tool.exe')
    if os.path.exists(exe_path):
        size = os.path.getsize(exe_path)
        print(f"✓ Executable created: {exe_path} ({size:,} bytes)")
        return True
    else:
        print("✗ Executable not found in expected location")
        return False

def create_distribution():
    """Create distribution package"""
    print("Creating distribution package...")
    
    timestamp = datetime.now().strftime("%Y%m%d")
    dist_name = f"PipePipe_Metadata_Tool_v1.0_{timestamp}"
    
    # Create distribution directory
    dist_dir = f"dist/{dist_name}"
    os.makedirs(dist_dir, exist_ok=True)
    
    # Copy files
    files_to_copy = [
        ('dist/PipePipe_Metadata_Tool.exe', f'{dist_dir}/PipePipe_Metadata_Tool.exe'),
        ('README.md', f'{dist_dir}/README.md'),
        ('LICENSE', f'{dist_dir}/LICENSE'),
        ('CHANGELOG.md', f'{dist_dir}/CHANGELOG.md'),
        ('requirements.txt', f'{dist_dir}/requirements.txt')
    ]
    
    for src, dst in files_to_copy:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  Copied: {src} -> {dst}")
    
    # Create zip archive
    archive_name = f"{dist_name}.zip"
    shutil.make_archive(f"dist/{dist_name}", 'zip', f"dist/{dist_name}")
    
    # Also create a standalone executable copy in dist root for GitHub Actions
    if os.path.exists('dist/PipePipe_Metadata_Tool.exe'):
        print("  ✓ Standalone executable ready for release")
    
    if os.path.exists(f"dist/{archive_name}"):
        size = os.path.getsize(f"dist/{archive_name}")
        print(f"✓ Distribution package created: dist/{archive_name} ({size:,} bytes)")
        return True
    else:
        print("✗ Failed to create distribution package")
        return False

def main():
    """Main build process"""
    print("PipePipe Metadata Tool - Build Script")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\n✗ Build failed - missing dependencies")
        sys.exit(1)
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable():
        print("\n✗ Build failed")
        sys.exit(1)
    
    # Create distribution
    if not create_distribution():
        print("\n✗ Distribution creation failed")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("✓ Build completed successfully!")
    print("\nFiles created:")
    print("  - dist/PipePipe_Metadata_Tool.exe")
    print("  - dist/PipePipe_Metadata_Tool_v1.0_*.zip")
    print("\nReady for distribution!")

if __name__ == "__main__":
    main()
