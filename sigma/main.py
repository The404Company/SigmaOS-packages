import os
import sys
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

def get_package_root():
    """Returns the path to the sigma package directory"""
    return os.path.dirname(os.path.abspath(__file__))

def get_sigmaos_root():
    """Returns the path to the SigmaOS root directory"""
    # Navigate up from package dir to find SigmaOS root
    package_dir = get_package_root()
    return os.path.dirname(os.path.dirname(package_dir))

def show_help():
    """Display help information for the sigma package"""
    print(f"\n{HEADER}╔══ Sigma Utilities ══════════════════════════╗{Style.RESET_ALL}")
    
    # Core Utilities
    print(f"\n{INFO}Core Utilities:{Style.RESET_ALL}")
    utilities = [
        ("sigma", "Display this help menu"),
        ("sigma.env", "Manage environment variables"),
        ("sigma.viewlogs", "View and manage log files"),
        ("sigma.ping", "Check connectivity to a host"),
        ("sigma.sysinfo", "Detailed system information"),
        ("sigma.clean", "Clean temporary files"),
        ("sigma.benchmark", "Simple system benchmark"),
        ("sigma.netstat", "Network statistics"),
        ("sigma.proclist", "List running processes"),
        ("sigma.wifi", "Wi-Fi network management"),
    ]
    for cmd, desc in utilities:
        print(f"{COMMAND}  {cmd:<25}{DESCRIPTION} - {desc}")
    
    print(f"\n{HEADER}╚{'═' * 45}╝{Style.RESET_ALL}")

def main():
    """Main entry point for the sigma package"""
    show_help()

if __name__ == "__main__":
    main() 