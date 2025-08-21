#!/usr/bin/env python3
"""
Install optional dependencies for enhanced benchmark functionality.
"""

import subprocess
import sys

def install_package(package_name):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"✓ Successfully installed {package_name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install {package_name}: {e}")
        return False

def main():
    print("Installing optional dependencies for enhanced benchmark functionality...")
    print("=" * 60)
    
    # Optional packages for better system information
    optional_packages = [
        "py-cpuinfo",  # For detailed CPU information
    ]
    
    success_count = 0
    for package in optional_packages:
        print(f"\nInstalling {package}...")
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Installation complete: {success_count}/{len(optional_packages)} packages installed successfully")
    
    if success_count == len(optional_packages):
        print("✓ All optional dependencies installed successfully!")
        print("  The benchmark will now provide more detailed CPU information.")
    else:
        print("⚠ Some optional dependencies failed to install.")
        print("  The benchmark will still work but with limited system information.")

if __name__ == "__main__":
    main()
