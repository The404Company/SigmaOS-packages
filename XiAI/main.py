import os
import sys
import subprocess
from colorama import Fore, Style, init

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}╔═══ Ξ XiAI Assistant ═════════╗")
    print(f"║ 1. Run Locally               ║")
    print(f"║ 2. Run Online (recommended)  ║")
    print(f"║ 0. Exit                      ║")
    print(f"╚══════════════════════════════╝{Style.RESET_ALL}")

def main():
    init(autoreset=True)
    while True:
        show_banner()
        try:
            choice = input(f"\n{Fore.WHITE}Choose an option (0-2): {Style.RESET_ALL}")
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}Goodbye!{Style.RESET_ALL}")
            break

        if choice == "1":
            try:
                subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'local.py')], 
                               stdout=sys.stdout, stderr=sys.stderr)
            except Exception as e:
                print(f"{Fore.RED}Error running XiAI locally: {e}{Style.RESET_ALL}")
        elif choice == "2":
            try:
                subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'online.py')], 
                               stdout=sys.stdout, stderr=sys.stderr)
            except Exception as e:
                print(f"{Fore.RED}Error running XiAI online: {e}{Style.RESET_ALL}")
        elif choice == "0":
            clear_screen()
            sys.exit(0)
        else:
            print(f"{Fore.RED}Invalid choice!{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Press Enter to continue...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()