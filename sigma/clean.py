import os
import sys
import shutil
import glob
import time
import datetime
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Define colors
SUCCESS = Fore.GREEN
ERROR = Fore.RED
WARNING = Fore.YELLOW
INFO = Fore.CYAN
HEADER = Fore.YELLOW
COMMAND = Fore.GREEN
DESCRIPTION = Fore.WHITE

def get_sigmaos_root():
    """Returns the path to the SigmaOS root directory"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(package_dir))

def format_bytes(size):
    """Format bytes to human-readable form"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def clean_logs(days=None, simulate=False):
    """Clean log files older than specified days"""
    logs_dir = os.path.join(get_sigmaos_root(), "logs")
    
    if not os.path.exists(logs_dir):
        print(f"{WARNING}No logs directory found.{Style.RESET_ALL}")
        return 0
    
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    
    if not log_files:
        print(f"{WARNING}No log files found to clean.{Style.RESET_ALL}")
        return 0
    
    deleted_count = 0
    deleted_size = 0
    now = time.time()
    
    print(f"{HEADER}Cleaning log files:{Style.RESET_ALL}")
    
    for log_file in log_files:
        file_age_days = (now - os.path.getmtime(log_file)) / (60 * 60 * 24)
        file_size = os.path.getsize(log_file)
        
        if days is None or file_age_days >= days:
            if simulate:
                print(f"{INFO}Would delete: {os.path.basename(log_file)} - {format_bytes(file_size)} - {file_age_days:.1f} days old{Style.RESET_ALL}")
                deleted_count += 1
                deleted_size += file_size
            else:
                try:
                    os.remove(log_file)
                    print(f"{SUCCESS}Deleted: {os.path.basename(log_file)} - {format_bytes(file_size)} - {file_age_days:.1f} days old{Style.RESET_ALL}")
                    deleted_count += 1
                    deleted_size += file_size
                except Exception as e:
                    print(f"{ERROR}Error deleting {log_file}: {e}{Style.RESET_ALL}")
    
    if deleted_count > 0:
        print(f"{SUCCESS}Deleted {deleted_count} log files ({format_bytes(deleted_size)}){' (simulated)' if simulate else ''}{Style.RESET_ALL}")
    else:
        print(f"{INFO}No log files were old enough to delete.{Style.RESET_ALL}")
    
    return deleted_count

def clean_temp_files(simulate=False):
    """Clean temporary files in the SigmaOS directory"""
    sigmaos_root = get_sigmaos_root()
    
    temp_patterns = [
        os.path.join(sigmaos_root, "*.tmp"),
        os.path.join(sigmaos_root, "*.temp"),
        os.path.join(sigmaos_root, "temp*.*"),
        os.path.join(sigmaos_root, "tmp*.*"),
        os.path.join(sigmaos_root, "*.~*"),
        os.path.join(sigmaos_root, "*.__*"),
    ]
    
    temp_files = []
    for pattern in temp_patterns:
        temp_files.extend(glob.glob(pattern))
    
    if not temp_files:
        print(f"{WARNING}No temporary files found to clean.{Style.RESET_ALL}")
        return 0
    
    deleted_count = 0
    deleted_size = 0
    
    print(f"{HEADER}Cleaning temporary files:{Style.RESET_ALL}")
    
    for temp_file in temp_files:
        file_size = os.path.getsize(temp_file)
        
        if simulate:
            print(f"{INFO}Would delete: {os.path.basename(temp_file)} - {format_bytes(file_size)}{Style.RESET_ALL}")
            deleted_count += 1
            deleted_size += file_size
        else:
            try:
                os.remove(temp_file)
                print(f"{SUCCESS}Deleted: {os.path.basename(temp_file)} - {format_bytes(file_size)}{Style.RESET_ALL}")
                deleted_count += 1
                deleted_size += file_size
            except Exception as e:
                print(f"{ERROR}Error deleting {temp_file}: {e}{Style.RESET_ALL}")
    
    if deleted_count > 0:
        print(f"{SUCCESS}Deleted {deleted_count} temporary files ({format_bytes(deleted_size)}){' (simulated)' if simulate else ''}{Style.RESET_ALL}")
    else:
        print(f"{INFO}No temporary files were found.{Style.RESET_ALL}")
    
    return deleted_count

def clean_package_cache(simulate=False):
    """Clean package cache files"""
    packages_dir = os.path.join(get_sigmaos_root(), "packages")
    
    if not os.path.exists(packages_dir):
        print(f"{WARNING}No packages directory found.{Style.RESET_ALL}")
        return 0
    
    # Look for cache directories and __pycache__ in all packages
    cache_patterns = [
        os.path.join(packages_dir, "*", "__pycache__"),
        os.path.join(packages_dir, "*", "*.pyc"),
        os.path.join(packages_dir, "*", "cache"),
        os.path.join(packages_dir, "*", ".cache"),
        os.path.join(packages_dir, "*", "tmp"),
        os.path.join(packages_dir, "*", "temp"),
    ]
    
    deleted_count = 0
    deleted_size = 0
    
    print(f"{HEADER}Cleaning package cache:{Style.RESET_ALL}")
    
    # Handle directories like __pycache__
    for pattern in cache_patterns:
        for item in glob.glob(pattern):
            if os.path.isdir(item):
                dir_size = 0
                for dirpath, dirnames, filenames in os.walk(item):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        dir_size += os.path.getsize(fp)
                
                if simulate:
                    print(f"{INFO}Would delete directory: {item} - {format_bytes(dir_size)}{Style.RESET_ALL}")
                    deleted_count += 1
                    deleted_size += dir_size
                else:
                    try:
                        shutil.rmtree(item)
                        print(f"{SUCCESS}Deleted directory: {item} - {format_bytes(dir_size)}{Style.RESET_ALL}")
                        deleted_count += 1
                        deleted_size += dir_size
                    except Exception as e:
                        print(f"{ERROR}Error deleting directory {item}: {e}{Style.RESET_ALL}")
            elif os.path.isfile(item):
                file_size = os.path.getsize(item)
                
                if simulate:
                    print(f"{INFO}Would delete file: {item} - {format_bytes(file_size)}{Style.RESET_ALL}")
                    deleted_count += 1
                    deleted_size += file_size
                else:
                    try:
                        os.remove(item)
                        print(f"{SUCCESS}Deleted file: {item} - {format_bytes(file_size)}{Style.RESET_ALL}")
                        deleted_count += 1
                        deleted_size += file_size
                    except Exception as e:
                        print(f"{ERROR}Error deleting file {item}: {e}{Style.RESET_ALL}")
    
    if deleted_count > 0:
        print(f"{SUCCESS}Cleaned {deleted_count} package cache items ({format_bytes(deleted_size)}){' (simulated)' if simulate else ''}{Style.RESET_ALL}")
    else:
        print(f"{INFO}No package cache items were found.{Style.RESET_ALL}")
    
    return deleted_count

def check_disk_space():
    """Check disk space and show usage"""
    sigmaos_root = get_sigmaos_root()
    
    try:
        import psutil
        disk_usage = psutil.disk_usage(sigmaos_root)
        
        total = format_bytes(disk_usage.total)
        used = format_bytes(disk_usage.used)
        free = format_bytes(disk_usage.free)
        percent = disk_usage.percent
        
        print(f"{HEADER}Disk Space:{Style.RESET_ALL}")
        print(f"{INFO}Total:{Style.RESET_ALL} {total}")
        print(f"{INFO}Used:{Style.RESET_ALL} {used} ({percent}%)")
        print(f"{INFO}Free:{Style.RESET_ALL} {free}")
        
        # Warning if disk space is low
        if percent >= 90:
            print(f"{ERROR}Warning: Disk space is critically low!{Style.RESET_ALL}")
        elif percent >= 80:
            print(f"{WARNING}Warning: Disk space is running low.{Style.RESET_ALL}")
        
    except ImportError:
        print(f"{ERROR}psutil module is required for disk space check.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{ERROR}Error checking disk space: {e}{Style.RESET_ALL}")

def show_help():
    """Show help for clean commands"""
    print(f"\n{HEADER}System Cleaning Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.clean{DESCRIPTION} - Clean all temporary files")
    print(f"{COMMAND}  sigma.clean logs [days]{DESCRIPTION} - Clean logs older than X days (default: all)")
    print(f"{COMMAND}  sigma.clean temp{DESCRIPTION} - Clean temporary files")
    print(f"{COMMAND}  sigma.clean cache{DESCRIPTION} - Clean package cache")
    print(f"{COMMAND}  sigma.clean space{DESCRIPTION} - Check disk space")
    print(f"{COMMAND}  sigma.clean simulate{DESCRIPTION} - Show what would be cleaned without actually deleting")
    print()

def main():
    """Main entry point for clean module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Default behavior: clean everything
        print(f"{HEADER}SigmaOS Cleanup Utility{Style.RESET_ALL}")
        print(f"{INFO}Starting cleanup process...{Style.RESET_ALL}")
        
        total_deleted = 0
        total_deleted += clean_logs()
        total_deleted += clean_temp_files()
        total_deleted += clean_package_cache()
        
        if total_deleted > 0:
            print(f"\n{SUCCESS}Cleanup completed successfully. Removed {total_deleted} items.{Style.RESET_ALL}")
        else:
            print(f"\n{WARNING}No items found to clean up.{Style.RESET_ALL}")
            
        check_disk_space()
        return
    
    command = args[0].lower()
    simulate = False
    
    # Check if simulation mode is requested
    if command == "simulate":
        simulate = True
        if len(args) > 1:
            command = args[1].lower()
        else:
            # Default behavior in simulate mode
            print(f"{HEADER}SigmaOS Cleanup Utility (SIMULATION MODE){Style.RESET_ALL}")
            print(f"{INFO}Simulating cleanup process...{Style.RESET_ALL}")
            
            total_deleted = 0
            total_deleted += clean_logs(simulate=True)
            total_deleted += clean_temp_files(simulate=True)
            total_deleted += clean_package_cache(simulate=True)
            
            if total_deleted > 0:
                print(f"\n{SUCCESS}Simulation completed. Would remove {total_deleted} items.{Style.RESET_ALL}")
            else:
                print(f"\n{WARNING}No items found to clean up in simulation.{Style.RESET_ALL}")
                
            check_disk_space()
            return
    
    if command == "help":
        show_help()
    elif command == "logs":
        days = None
        if len(args) >= 2:
            try:
                days = float(args[1])
            except ValueError:
                print(f"{ERROR}Invalid number of days: {args[1]}{Style.RESET_ALL}")
                return
        clean_logs(days, simulate)
    elif command == "temp":
        clean_temp_files(simulate)
    elif command == "cache":
        clean_package_cache(simulate)
    elif command == "space":
        check_disk_space()
    else:
        print(f"{ERROR}Unknown command: {command}{Style.RESET_ALL}")
        show_help()

if __name__ == "__main__":
    main() 