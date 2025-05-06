import os
import sys
import glob
from datetime import datetime
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
LOG_INFO = Fore.BLUE
LOG_ERROR = Fore.RED
LOG_WARNING = Fore.YELLOW
LOG_SUCCESS = Fore.GREEN
LOG_TIMESTAMP = Fore.CYAN
LOG_NORMAL = Fore.WHITE

def get_sigmaos_root():
    """Returns the path to the SigmaOS root directory"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(package_dir))

def get_logs_dir():
    """Returns the path to the logs directory"""
    return os.path.join(get_sigmaos_root(), "logs")

def ensure_logs_dir():
    """Ensure logs directory exists"""
    logs_dir = get_logs_dir()
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    return logs_dir

def list_logs():
    """List all log files in the logs directory"""
    logs_dir = ensure_logs_dir()
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    
    if not log_files:
        print(f"{WARNING}No log files found.{Style.RESET_ALL}")
        return []
    
    print(f"\n{HEADER}Available Log Files:{Style.RESET_ALL}")
    for i, log_file in enumerate(sorted(log_files, reverse=True)):
        file_name = os.path.basename(log_file)
        file_size = os.path.getsize(log_file)
        file_time = datetime.fromtimestamp(os.path.getmtime(log_file)).strftime("%Y-%m-%d %H:%M:%S")
        
        # Format file size
        if file_size < 1024:
            size_str = f"{file_size} B"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size/1024:.1f} KB"
        else:
            size_str = f"{file_size/(1024*1024):.1f} MB"
            
        print(f"{INFO}{i+1}.{Style.RESET_ALL} {file_name} - {DESCRIPTION}{size_str} - {file_time}")
    
    return log_files

def view_log(log_file, lines=None, filter_text=None, show_errors_only=False):
    """View the contents of a log file"""
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        # Apply filters
        if filter_text:
            content = [line for line in content if filter_text.lower() in line.lower()]
        
        if show_errors_only:
            content = [line for line in content if "error" in line.lower() or "exception" in line.lower()]
            
        # Limit lines if specified
        if lines:
            content = content[-lines:]
            
        if not content:
            print(f"{WARNING}No log entries match the criteria.{Style.RESET_ALL}")
            return
            
        print(f"\n{HEADER}Log File: {os.path.basename(log_file)}{Style.RESET_ALL}")
        
        for line in content:
            # Color formatting based on log content
            line = line.strip()
            if not line:
                continue
                
            if "[ERROR]" in line or "Error:" in line or "Exception" in line:
                color = LOG_ERROR
            elif "[WARNING]" in line or "Warning:" in line:
                color = LOG_WARNING
            elif "[SUCCESS]" in line or "Success:" in line:
                color = LOG_SUCCESS
            elif "[INFO]" in line or "Info:" in line:
                color = LOG_INFO
            else:
                color = LOG_NORMAL
                
            # Highlight timestamp if present
            if "]" in line and "[" in line:
                timestamp_end = line.find("]") + 1
                timestamp = line[:timestamp_end]
                message = line[timestamp_end:]
                print(f"{LOG_TIMESTAMP}{timestamp}{color}{message}{Style.RESET_ALL}")
            else:
                print(f"{color}{line}{Style.RESET_ALL}")
                
    except Exception as e:
        print(f"{ERROR}Error reading log file: {e}{Style.RESET_ALL}")

def delete_log(log_file):
    """Delete a log file"""
    try:
        os.remove(log_file)
        print(f"{SUCCESS}Log file deleted: {os.path.basename(log_file)}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{ERROR}Error deleting log file: {e}{Style.RESET_ALL}")
        return False

def clear_all_logs():
    """Delete all log files"""
    logs_dir = ensure_logs_dir()
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    
    if not log_files:
        print(f"{WARNING}No log files to clear.{Style.RESET_ALL}")
        return
        
    print(f"{WARNING}About to delete {len(log_files)} log files.{Style.RESET_ALL}")
    confirm = input(f"{WARNING}Are you sure? (y/N): {Style.RESET_ALL}")
    
    if confirm.lower() != 'y':
        print(f"{INFO}Operation cancelled.{Style.RESET_ALL}")
        return
        
    deleted = 0
    for log_file in log_files:
        if delete_log(log_file):
            deleted += 1
            
    print(f"{SUCCESS}Deleted {deleted} of {len(log_files)} log files.{Style.RESET_ALL}")

def show_help():
    """Show help information for log commands"""
    print(f"\n{HEADER}Log Viewing Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.viewlogs{DESCRIPTION} - List all log files")
    print(f"{COMMAND}  sigma.viewlogs <n>{DESCRIPTION} - View log file by number")
    print(f"{COMMAND}  sigma.viewlogs <filename>{DESCRIPTION} - View specific log file")
    print(f"{COMMAND}  sigma.viewlogs <n> <lines>{DESCRIPTION} - View last N lines of log file")
    print(f"{COMMAND}  sigma.viewlogs <n> filter <text>{DESCRIPTION} - Filter log by text")
    print(f"{COMMAND}  sigma.viewlogs <n> errors{DESCRIPTION} - Show only errors in log")
    print(f"{COMMAND}  sigma.viewlogs delete <n>{DESCRIPTION} - Delete log file by number")
    print(f"{COMMAND}  sigma.viewlogs clear{DESCRIPTION} - Delete all log files")
    print()

def main():
    """Main entry point for the viewlogs module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        log_files = list_logs()
        if log_files:
            print(f"\n{INFO}Use 'sigma.viewlogs <number>' to view a log file.{Style.RESET_ALL}")
        return
    
    command = args[0].lower()
    
    if command == "help":
        show_help()
        return
        
    if command == "clear":
        clear_all_logs()
        return
        
    if command == "delete" and len(args) == 2:
        try:
            index = int(args[1]) - 1
            log_files = sorted(glob.glob(os.path.join(get_logs_dir(), "*.log")), reverse=True)
            if 0 <= index < len(log_files):
                delete_log(log_files[index])
            else:
                print(f"{ERROR}Invalid log file number.{Style.RESET_ALL}")
        except ValueError:
            print(f"{ERROR}Invalid log file number.{Style.RESET_ALL}")
        return
    
    # Handle viewing logs
    try:
        # Try to parse first argument as a number
        index = int(command) - 1
        log_files = sorted(glob.glob(os.path.join(get_logs_dir(), "*.log")), reverse=True)
        
        if 0 <= index < len(log_files):
            log_file = log_files[index]
            
            # Check for additional arguments
            if len(args) >= 2:
                if args[1] == "filter" and len(args) >= 3:
                    # Filter by text
                    filter_text = args[2]
                    view_log(log_file, filter_text=filter_text)
                elif args[1] == "errors":
                    # Show only errors
                    view_log(log_file, show_errors_only=True)
                else:
                    try:
                        # Try to parse as number of lines
                        lines = int(args[1])
                        view_log(log_file, lines=lines)
                    except ValueError:
                        view_log(log_file)
            else:
                view_log(log_file)
        else:
            print(f"{ERROR}Invalid log file number.{Style.RESET_ALL}")
    except ValueError:
        # First argument is not a number, try as filename
        logs_dir = get_logs_dir()
        log_file = os.path.join(logs_dir, command if command.endswith(".log") else command + ".log")
        
        if os.path.exists(log_file):
            view_log(log_file)
        else:
            print(f"{ERROR}Log file not found: {command}{Style.RESET_ALL}")
            list_logs()

if __name__ == "__main__":
    main() 