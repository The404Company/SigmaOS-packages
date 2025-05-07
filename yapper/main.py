import os
import sys
import platform
from colorama import Fore, Style, init

# Cross-platform keyboard input
if platform.system() == 'Windows':
    import msvcrt
    
    def get_key():
        """Get a single key press on Windows"""
        key = msvcrt.getch()
        if key == b'\x1b':  # Escape key
            return 'exit'
        elif key == b'\r':  # Enter key
            return 'enter'
        elif key == b'\x08':  # Backspace key
            return 'backspace'
        elif key == b'\xe0':  # Special keys (arrows, function keys)
            key = msvcrt.getch()
            if key == b'H':  # Up arrow
                return 'up'
            elif key == b'P':  # Down arrow
                return 'down'
            elif key == b'K':  # Left arrow
                return 'left'
            elif key == b'M':  # Right arrow
                return 'right'
        else:
            return key.decode('ascii', errors='ignore') if len(key) == 1 else None
else:
    # For Linux/Mac
    import termios
    import tty
    import select
    
    def get_key():
        """Get a single key press on Linux/Mac"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                ch = sys.stdin.read(1)
            else:
                ch = ''
                
            # Handle escape sequences for arrow keys
            if ch == '\x1b':  # Escape key or special key
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        if select.select([sys.stdin], [], [], 0.1)[0]:
                            ch3 = sys.stdin.read(1)
                            if ch3 == 'A':
                                return 'up'
                            elif ch3 == 'B':
                                return 'down'
                            elif ch3 == 'C':
                                return 'right'
                            elif ch3 == 'D':
                                return 'left'
                return 'exit'
            elif ch == '\n' or ch == '\r':  # Enter key
                return 'enter'
            elif ch == '\x7f' or ch == '\b':  # Backspace key
                return 'backspace'
            else:
                return ch if ch else None
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def show_banner():
    print(f"{Fore.CYAN}Welcome to Yapper!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}A simple text editor for SigmaOS.{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Press ESC to save and exit.{Style.RESET_ALL}\n")

def editor(filename=None):
    init(autoreset=True)
    show_banner()
    
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    docs_dir = os.path.join(root_dir, "documents")
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    if filename is None:
        filename = input(f"{Fore.GREEN}Enter filename: {Style.RESET_ALL}")
    filepath = os.path.join(docs_dir, filename)
    
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
            if not content:  
                content = [""]
        print(f"{Fore.GREEN}Loaded existing file: {filename}{Style.RESET_ALL}")
    else:
        content = [""]  
        if filename:  
            print(f"{Fore.YELLOW}New file: {filename}{Style.RESET_ALL}")
    
    cursor_y = 0
    cursor_x = 0
    
    # Improve scrolling behavior
    def refresh_screen():
        os.system('cls' if os.name == 'nt' else 'clear')  # More compatible screen clearing
        print(f"{Fore.CYAN}Editing: {filename} {Fore.WHITE}(ESC to save and exit){Style.RESET_ALL}\n")
        
        start_line = max(0, cursor_y - 10)
        end_line = min(len(content), start_line + 20)
        
        for i in range(start_line, end_line):
            line = content[i]
            if i == cursor_y:
                sys.stdout.write(line[:cursor_x] + "█" + line[cursor_x:] + "\n")
            else:
                sys.stdout.write(line + "\n")
        sys.stdout.flush()
    
    refresh_screen()
    
    while True:
        key = get_key()
        if key is None:
            continue
            
        if key == 'exit':
            break
        elif key == 'enter':
            current = content[cursor_y]
            content[cursor_y] = current[:cursor_x]
            content.insert(cursor_y + 1, current[cursor_x:])
            cursor_y += 1
            cursor_x = 0
        elif key == 'backspace':
            if cursor_x > 0:
                current = content[cursor_y]
                content[cursor_y] = current[:cursor_x-1] + current[cursor_x:]
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
                content[cursor_y] += content.pop(cursor_y + 1)
        elif key == 'left':
            if cursor_x > 0:
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_y -= 1
                cursor_x = len(content[cursor_y])
        elif key == 'right':
            if cursor_x < len(content[cursor_y]):
                cursor_x += 1
            elif cursor_y < len(content) - 1:
                cursor_y += 1
                cursor_x = 0
        elif key == 'up':
            if cursor_y > 0:
                cursor_y -= 1
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif key == 'down':
            if cursor_y < len(content) - 1:
                cursor_y += 1
                cursor_x = min(cursor_x, len(content[cursor_y]))
        elif isinstance(key, str) and key.isprintable():
            current = content[cursor_y]
            content[cursor_y] = current[:cursor_x] + key + current[cursor_x:]
            cursor_x += 1
        
        refresh_screen()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))
    
    print(f"\n{Fore.GREEN}File saved to: {filepath}{Style.RESET_ALL}")
    
    # Cross-platform way to restart SigmaOS
    python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
    os.system(f'{python_cmd} ' + os.path.join(root_dir, 'SigmaOS.py'))

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None 
    editor(filename)
