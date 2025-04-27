import os
import msvcrt
import sys
from colorama import Fore, Style, init

def get_key():
    # there's a lot of stuff here thats not needed but i dont care
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
        return key.decode('ascii') if len(key) == 1 else None

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
        sys.stdout.write("\033[H")  
        sys.stdout.write("\033[J")  
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
    os.system('python ' + os.path.join(root_dir, 'SigmaOS.py'))

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None # its broken af
    editor(filename)
