import os
import requests
import shutil
import time
import psutil
import signal
import subprocess
import sys
import platform
from datetime import datetime
from colorama import Fore, Style

def loading_animation(message, duration=2):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        print(f"\r{Fore.CYAN}{frames[i]} {message}", end="")
        time.sleep(0.1)
        i = (i + 1) % len(frames)
    print(f"\r{Fore.GREEN}✓ {message}{Style.RESET_ALL}")

def get_current_pid():
    """Get the current process ID"""
    return os.getpid()

def force_terminate_sigmaos():
    """Terminates SigmaOS processes except for the current one"""
    current_pid = get_current_pid()
    parent_pid = os.getppid()
    
    # Log info about the current process
    print(f"{Fore.CYAN}Current process: PID={current_pid}, Parent PID={parent_pid}{Style.RESET_ALL}")
    
    terminated = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            pid = proc.info['pid']
            cmdline = proc.info['cmdline']
            # Skip the current process and its parent
            if pid == current_pid or pid == parent_pid:
                continue
                
            if cmdline and 'python' in cmdline[0].lower() and 'sigmaos.py' in cmdline[-1].lower():
                print(f"{Fore.YELLOW}Terminating SigmaOS process: PID={pid}{Style.RESET_ALL}")
                # Force kill the process
                if platform.system() == 'Windows':  # Windows
                    os.kill(pid, signal.SIGTERM)
                else:  # Linux/Mac
                    os.kill(pid, signal.SIGKILL)
                terminated = True
        except Exception as e:
            print(f"{Fore.RED}Error terminating process: {str(e)}{Style.RESET_ALL}")
            continue
    return terminated

def update_sigma():
    # Get absolute paths - make sure we're in root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))  # SigmaUpdate directory
    root_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to root
    target_file = os.path.join(root_dir, "SigmaOS.py")
    temp_file = os.path.join(root_dir, "SigmaOS.py.temp")
    
    print(f"{Fore.CYAN}Update paths:{Style.RESET_ALL}")
    print(f"Root directory: {root_dir}")
    print(f"Target file: {target_file}")
    
    # Force terminate existing SigmaOS process
    print(f"{Fore.YELLOW}Looking for SigmaOS processes to terminate...{Style.RESET_ALL}")
    if force_terminate_sigmaos():
        loading_animation("SigmaOS process terminated")
        time.sleep(1)
    else:
        print(f"{Fore.YELLOW}No other SigmaOS processes found to terminate.{Style.RESET_ALL}")
    
    try:
        # Download new version
        url = "https://raw.githubusercontent.com/The404Company/SigmaOS/main/SigmaOS.py"
        loading_animation("Downloading latest version")
        response = requests.get(url)
        response.raise_for_status()
        
        # Make sure we write to root directory
        os.chdir(root_dir)  # Change working directory to root
        
        # First save to temp file in root directory
        with open(temp_file, 'wb') as f:
            f.write(response.content)
        
        # Create backup if original exists
        if os.path.exists(target_file):
            backup_path = os.path.join(root_dir, f"SigmaOS.py.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            shutil.copy2(target_file, backup_path)
            print(f"{Fore.CYAN}Backup created at: {backup_path}{Style.RESET_ALL}")
            os.remove(target_file)
        
        # Move new file into place in root directory
        shutil.move(temp_file, target_file)
        loading_animation("Installing update")
        
        if not os.path.exists(target_file):
            raise Exception("Failed to replace SigmaOS.py in root directory")
        
        print(f"{Fore.GREEN}File replacement successful!{Style.RESET_ALL}")
        time.sleep(1)
        
        # Start new instance using a separate script that won't be killed
        print(f"{Fore.CYAN}Preparing to start new SigmaOS instance...{Style.RESET_ALL}")
        
        # Create a small launcher script
        launcher_script = os.path.join(root_dir, "launch_sigmaos.py")
        with open(launcher_script, 'w') as f:
            f.write(f"""
import os
import subprocess
import time
import platform

# Wait for the parent process to exit
time.sleep(1)

# Start SigmaOS
python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
os.chdir({repr(root_dir)})  # Change to root directory
cmd = [python_cmd, {repr(target_file)}]

if platform.system() == 'Windows':
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
else:
    subprocess.Popen(cmd, start_new_session=True)
""")
        
        # Run the launcher script
        python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
        subprocess.Popen([python_cmd, launcher_script], 
                         start_new_session=True if platform.system() != 'Windows' else False,
                         creationflags=subprocess.CREATE_NEW_CONSOLE if platform.system() == 'Windows' else 0)
        
        print(f"{Fore.GREEN}Update complete! New instance will start automatically.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Exiting updater...{Style.RESET_ALL}")
        time.sleep(2)
        sys.exit(0)
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if 'backup_path' in locals() and os.path.exists(backup_path):
            shutil.copy2(backup_path, target_file)
            print(f"{Fore.GREEN}Restored from backup{Style.RESET_ALL}")

if __name__ == "__main__":
    update_sigma()
