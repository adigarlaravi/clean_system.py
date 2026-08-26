"""
SELF-CLEANING SYSTEM - Remove unnecessary files and keep project clean
Run this periodically to maintain project hygiene
"""

import os
import shutil
import glob
from pathlib import Path

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🧹 CREDIT RISK AI - SELF CLEANING SYSTEM 🧹              ║
║                                                               ║
║     Removing unnecessary files to keep project clean         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def clean_pycache():
    """Remove all __pycache__ directories"""
    print("\n[1] Cleaning __pycache__ directories...")
    count = 0
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                dir_path = os.path.join(root, dir_name)
                try:
                    shutil.rmtree(dir_path)
                    print(f"  Removed: {dir_path}")
                    count += 1
                except:
                    pass
    print(f"  Removed {count} __pycache__ directories")

def clean_pyc_files():
    """Remove all .pyc files"""
    print("\n[2] Cleaning .pyc files...")
    count = 0
    for pyc_file in glob.glob("**/*.pyc", recursive=True):
        try:
            os.remove(pyc_file)
            print(f"  Removed: {pyc_file}")
            count += 1
        except:
            pass
    print(f"  Removed {count} .pyc files")

def clean_temp_files():
    """Remove temporary files"""
    print("\n[3] Cleaning temporary files...")
    patterns = ["*.log", "*.tmp", "*.bak", "*.py~", "*.swp", "*.cache"]
    count = 0
    
    for pattern in patterns:
        for file_path in glob.glob(f"**/{pattern}", recursive=True):
            try:
                os.remove(file_path)
                print(f"  Removed: {file_path}")
                count += 1
            except:
                pass
    print(f"  Removed {count} temporary files")

def clean_empty_dirs():
    """Remove empty directories"""
    print("\n[4] Removing empty directories...")
    count = 0
    for root, dirs, files in os.walk(".", topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"  Removed empty dir: {dir_path}")
                    count += 1
            except:
                pass
    print(f"  Removed {count} empty directories")

def clean_venv_cache():
    """Clean venv cache (optional - careful!)"""
    print("\n[5] Cleaning venv cache...")
    venv_cache_dirs = [
        "venv/Lib/site-packages/__pycache__",
        "venv/Scripts/__pycache__",
    ]
    
    count = 0
    for cache_dir in venv_cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"  Removed: {cache_dir}")
                count += 1
            except:
                pass
    print(f"  Cleaned {count} venv cache directories")

def clean_jupyter_cache():
    """Clean Jupyter notebook cache"""
    print("\n[6] Cleaning Jupyter cache...")
    jupyter_dirs = [
        ".ipynb_checkpoints",
        "**/.ipynb_checkpoints",
    ]
    
    count = 0
    for pattern in jupyter_dirs:
        for dir_path in glob.glob(f"**/{pattern}", recursive=True):
            try:
                shutil.rmtree(dir_path)
                print(f"  Removed: {dir_path}")
                count += 1
            except:
                pass
    print(f"  Removed {count} Jupyter cache directories")

def clean_pytest_cache():
    """Clean pytest cache"""
    print("\n[7] Cleaning pytest cache...")
    pytest_dirs = [".pytest_cache", ".coverage", "htmlcov"]
    
    count = 0
    for dir_name in pytest_dirs:
        if os.path.exists(dir_name):
            try:
                if os.path.isdir(dir_name):
                    shutil.rmtree(dir_name)
                else:
                    os.remove(dir_name)
                print(f"  Removed: {dir_name}")
                count += 1
            except:
                pass
    print(f"  Removed {count} pytest cache items")

def clean_model_backups():
    """Clean old model backups (keep only latest 3)"""
    print("\n[8] Cleaning old model backups...")
    model_files = glob.glob("models/*.pkl") + glob.glob("models/*.json")
    
    if len(model_files) > 5:
        # Sort by modification time
        model_files.sort(key=os.path.getmtime)
        to_delete = model_files[:-3]  # Keep latest 3
        
        for file_path in to_delete:
            try:
                os.remove(file_path)
                print(f"  Removed old model: {file_path}")
            except:
                pass
        print(f"  Removed {len(to_delete)} old model files")
    else:
        print(f"  Only {len(model_files)} models - keeping all")

def show_disk_usage():
    """Show disk usage before and after"""
    print("\n[9] Checking disk usage...")
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        print(f"  Free space: {free // (2**30)} GB")
        print(f"  Used space: {used // (2**30)} GB")
    except:
        pass

def clean_logs():
    """Clean old log files"""
    print("\n[10] Cleaning old log files...")
    log_files = glob.glob("logs/*.log")
    
    count = 0
    for log_file in log_files:
        try:
            # Keep only last 5 log files
            if len(log_files) > 5:
                os.remove(log_file)
                print(f"  Removed old log: {log_file}")
                count += 1
        except:
            pass
    print(f"  Removed {count} old log files")

def create_cleanup_bat():
    """Create Windows batch file for easy cleaning"""
    cleanup_bat_content = '''@echo off
title Credit Risk AI - Cleaner
color 0E
echo ========================================
echo    Cleaning Credit Risk AI System
echo ========================================
echo.
call venv\\Scripts\\activate
python clean_system.py
echo.
echo ========================================
echo    Cleaning Complete!
echo ========================================
pause
'''
    
    with open("CLEAN_NOW.bat", "w", encoding="utf-8") as f:
        f.write(cleanup_bat_content)
    print("\n[+] Created CLEAN_NOW.bat - Double-click to clean anytime!")

def main():
    print_banner()
    
    confirm = input("\nThis will remove all cache and temporary files. Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Cancelled.")
        return
    
    # Run all cleaning functions
    clean_pycache()
    clean_pyc_files()
    clean_temp_files()
    clean_empty_dirs()
    clean_venv_cache()
    clean_jupyter_cache()
    clean_pytest_cache()
    clean_model_backups()
    clean_logs()
    show_disk_usage()
    create_cleanup_bat()
    
    print("\n" + "="*60)
    print("🧹 CLEANING COMPLETE!")
    print("="*60)
    print("\nYour project is now clean and optimized!")
    print("Run 'python clean_system.py' again anytime to clean.")
    print("\nDouble-click CLEAN_NOW.bat for one-click cleaning!")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
    
