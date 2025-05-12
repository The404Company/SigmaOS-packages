import os
import sys
import platform
import time
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

def get_terminal_size():
    """Get terminal size cross-platform"""
    if platform.system() == 'Windows':
        from ctypes import windll, create_string_buffer
        h = windll.kernel32.GetStdHandle(-11)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            import struct
            (_, _, _, _, _, left, top, right, bottom, _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            columns = right - left + 1
            rows = bottom - top + 1
            return rows, columns
    else:
        import fcntl, termios, struct
        try:
            hw = struct.unpack('hh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, '1234'))
            return hw[0], hw[1]
        except:
            pass
    return 25, 80  # Default fallback

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
    
    # Track file modification
    original_content = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read().splitlines()
            original_content = content.copy()
            if not content:
                content = [""]
        print(f"{Fore.GREEN}Loaded existing file: {filename}{Style.RESET_ALL}")
    else:
        content = [""]
        original_content = [""]
        if filename:
            print(f"{Fore.YELLOW}New file: {filename}{Style.RESET_ALL}")
    
    cursor_y = 0
    cursor_x = 0
    last_screen = []
    last_time = time.time()
    
    def is_modified():
        return content != original_content
    
    def get_line_number_width():
        return len(str(len(content)))
    
    def render_line(i, line, is_current):
        num_width = get_line_number_width()
        line_num = f"{Fore.BLUE}{str(i+1).rjust(num_width)} {Style.RESET_ALL}"
        if is_current:
            # Cursor always shown as a block (█) at the cursor position
            before = line[:cursor_x]
            after = line[cursor_x:]
            return f"{line_num}{before}{Fore.WHITE}█{Style.RESET_ALL}{after}"
        return f"{line_num}{line}"

    def refresh_screen(force=False):
        nonlocal last_screen, last_time
        current_time = time.time()
        
        if not force and current_time - last_time < 0.016:
            return
        last_time = current_time
        
        # Fixed viewport of 12 lines
        VIEWPORT_HEIGHT = 12
        
        # Calculate viewport window
        if cursor_y < VIEWPORT_HEIGHT // 2:
            start_line = 0
        elif cursor_y >= len(content) - (VIEWPORT_HEIGHT // 2):
            start_line = max(0, len(content) - VIEWPORT_HEIGHT)
        else:
            start_line = cursor_y - (VIEWPORT_HEIGHT // 2)
            
        end_line = min(start_line + VIEWPORT_HEIGHT, len(content))
        
        # Prepare new screen content
        new_screen = []
        num_width = get_line_number_width()
        
        # Header with file info and viewport position
        status = f"{Fore.GREEN}*{Style.RESET_ALL} " if is_modified() else ""
        scroll_info = f"[{start_line + 1}-{end_line}/{len(content)}]"
        header = f"{Fore.CYAN}Editing: {status}{filename} {scroll_info} {Fore.WHITE}(ESC to save and exit){Style.RESET_ALL}"
        new_screen.append(header)
        new_screen.append("")
        
        # Content with line numbers
        for i in range(start_line, end_line):
            new_screen.append(render_line(i, content[i], i == cursor_y))
        
        # Fill remaining viewport space with empty lines
        while len(new_screen) < VIEWPORT_HEIGHT + 3:  # +3 for header, blank line, and status
            new_screen.append("~")
        
        # Status line
        pos_info = f"Line {cursor_y + 1}/{len(content)}, Col {cursor_x + 1}"
        status_line = f"{Fore.YELLOW}{pos_info}{Style.RESET_ALL}"
        new_screen.append("")
        new_screen.append(status_line)
        
        # Update screen
        if not force:
            for i, (old, new) in enumerate(zip(last_screen + [""] * len(new_screen), new_screen)):
                if old != new:
                    sys.stdout.write(f"\033[{i+1};0H")  # Move cursor to line
                    sys.stdout.write("\033[K")  # Clear line
                    sys.stdout.write(new + "\n")
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            sys.stdout.write("\n".join(new_screen) + "\n")
        
        last_screen = new_screen
        sys.stdout.flush()

    # Initial screen draw
    refresh_screen(force=True)
    
    # Main editor loop
    while True:
        key = get_key()
        if key is None:
            continue
            
        if key == 'exit':
            break
        elif key == 'enter':
            current = content[cursor_y]
            indent = len(current) - len(current.lstrip())
            content[cursor_y] = current[:cursor_x]
            content.insert(cursor_y + 1, " " * indent + current[cursor_x:])
            cursor_y += 1
            cursor_x = indent
        elif key == 'backspace':
            if cursor_x > 0:
                current = content[cursor_y]
                content[cursor_y] = current[:cursor_x-1] + current[cursor_x:]
                cursor_x -= 1
            elif cursor_y > 0:
                cursor_x = len(content[cursor_y - 1])
                content[cursor_y - 1] += content.pop(cursor_y)
                cursor_y -= 1
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
    
    print(f"\n{Fore.GREEN}File saved to: documents/{filename}{Style.RESET_ALL}")
    
    # Cross-platform way to restart SigmaOS
    python_cmd = 'python3' if platform.system() != 'Windows' else 'python'
    os.system(f'{python_cmd} ' + os.path.join(root_dir, 'SigmaOS.py'))

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else None 
    editor(filename)
