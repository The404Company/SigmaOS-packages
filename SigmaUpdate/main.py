import os
import requests
import time
import sys
import platform
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

def update_sigma():
    # Get absolute paths - make sure we're in root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))  # SigmaUpdate directory
    root_dir = os.path.dirname(os.path.dirname(current_dir))  # Go up two levels to root
    target_file = os.path.join(root_dir, "SigmaOS.py")
    
    print(f"{Fore.CYAN}Update paths:{Style.RESET_ALL}")
    print(f"Root directory: {root_dir}")
    print(f"Target file: {target_file}")
    
    try:
        # Check current version
        if not os.path.exists(target_file):
            print(f"{Fore.RED}Error: SigmaOS.py not found in root directory{Style.RESET_ALL}")
            return
        
        with open(target_file, 'r', encoding='utf-8') as f:
            current_content = f.read()
        
        # Download GitHub version to compare
        url = "https://raw.githubusercontent.com/The404Company/SigmaOS/main/SigmaOS.py"
        loading_animation("Checking for updates")
        response = requests.get(url)
        response.raise_for_status()
        github_content = response.content.decode('utf-8')
        
        # Compare versions
        if current_content == github_content:
            print(f"{Fore.GREEN}SigmaOS is already up to date!{Style.RESET_ALL}")
            return
        
        # Ask for confirmation
        print(f"{Fore.YELLOW}A new version of SigmaOS is available.{Style.RESET_ALL}")
        confirm = input(f"{Fore.CYAN}Do you want to update? [Y/n]: {Style.RESET_ALL}")
        
        if confirm.lower() == 'n':
            print(f"{Fore.YELLOW}Update cancelled.{Style.RESET_ALL}")
            return
        
        # Update the file
        print(f"{Fore.CYAN}Updating SigmaOS...{Style.RESET_ALL}")
        with open(target_file, 'w', encoding='utf-8') as f:
            # Truncate and rewrite the file instead of replacing it
            f.write(github_content)
        
        loading_animation("Installing update")
        print(f"{Fore.GREEN}Update complete!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please restart SigmaOS to apply the changes.{Style.RESET_ALL}")
        
    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    update_sigma()
