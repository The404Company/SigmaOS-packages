import os
import sys
import psutil
import datetime
import platform
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
PROC_NAME = Fore.CYAN
PROC_PID = Fore.YELLOW
PROC_CPU = Fore.GREEN
PROC_MEM = Fore.MAGENTA
PROC_TIME = Fore.BLUE
PROC_STATUS = Fore.WHITE
PROC_USER = Fore.LIGHTBLUE_EX

def format_bytes(size):
    """Format bytes to human-readable form"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def get_processes(sort_by="cpu", top=None, filter_text=None):
    """Get list of running processes with details"""
    processes = []
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                # Only include processes that match filter text if provided
                if filter_text and filter_text.lower() not in proc.info['name'].lower():
                    continue
                    
                # Get process info
                pid = proc.info['pid']
                name = proc.info['name']
                username = proc.info['username'] or "Unknown"
                status = proc.info['status']
                cpu_percent = proc.info['cpu_percent']
                memory_bytes = proc.info['memory_info'].rss if proc.info['memory_info'] else 0
                memory = format_bytes(memory_bytes)
                create_time = datetime.datetime.fromtimestamp(proc.info['create_time']).strftime("%H:%M:%S")
                
                # Try to get command line
                try:
                    cmdline = " ".join(proc.cmdline())
                    if len(cmdline) > 100:
                        cmdline = cmdline[:97] + "..."
                except:
                    cmdline = name
                
                # Add to list
                processes.append({
                    "pid": pid,
                    "name": name,
                    "username": username,
                    "status": status,
                    "cpu_percent": cpu_percent,
                    "memory_bytes": memory_bytes,
                    "memory": memory,
                    "create_time": create_time,
                    "cmdline": cmdline
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    
    except Exception as e:
        print(f"{ERROR}Error getting process list: {e}{Style.RESET_ALL}")
    
    # Sort processes
    if sort_by == "cpu":
        processes.sort(key=lambda p: p["cpu_percent"], reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda p: p["memory_bytes"], reverse=True)
    elif sort_by == "pid":
        processes.sort(key=lambda p: p["pid"])
    elif sort_by == "name":
        processes.sort(key=lambda p: p["name"].lower())
    elif sort_by == "time":
        processes.sort(key=lambda p: p["create_time"], reverse=True)
    
    # Limit to top N if specified
    if top:
        processes = processes[:top]
    
    return processes

def show_processes(sort_by="cpu", top=None, filter_text=None, detailed=False):
    """Display list of running processes"""
    processes = get_processes(sort_by, top, filter_text)
    
    if not processes:
        print(f"{WARNING}No processes found.{Style.RESET_ALL}")
        if filter_text:
            print(f"{INFO}Try a different filter.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Process List ({len(processes)} processes):{Style.RESET_ALL}")
    
    if detailed:
        print(f"{COMMAND}{'PID':<7} {'CPU%':<7} {'Memory':<10} {'Status':<10} {'Start':<10} {'User':<15} {'Name':<20} Command{Style.RESET_ALL}")
        print("-" * 100)
        
        for proc in processes:
            status_color = SUCCESS if proc["status"] == "running" else (
                WARNING if proc["status"] == "sleeping" else ERROR)
            
            print(f"{PROC_PID}{proc['pid']:<7}{Style.RESET_ALL} "
                  f"{PROC_CPU}{proc['cpu_percent']:<7.1f}{Style.RESET_ALL} "
                  f"{PROC_MEM}{proc['memory']:<10}{Style.RESET_ALL} "
                  f"{status_color}{proc['status']:<10}{Style.RESET_ALL} "
                  f"{PROC_TIME}{proc['create_time']:<10}{Style.RESET_ALL} "
                  f"{PROC_USER}{proc['username'][:15]:<15}{Style.RESET_ALL} "
                  f"{PROC_NAME}{proc['name'][:20]:<20}{Style.RESET_ALL} "
                  f"{DESCRIPTION}{proc['cmdline']}{Style.RESET_ALL}")
    else:
        print(f"{COMMAND}{'PID':<7} {'CPU%':<7} {'Memory':<10} {'Status':<10} {'Name'}{Style.RESET_ALL}")
        print("-" * 70)
        
        for proc in processes:
            status_color = SUCCESS if proc["status"] == "running" else (
                WARNING if proc["status"] == "sleeping" else ERROR)
            
            print(f"{PROC_PID}{proc['pid']:<7}{Style.RESET_ALL} "
                  f"{PROC_CPU}{proc['cpu_percent']:<7.1f}{Style.RESET_ALL} "
                  f"{PROC_MEM}{proc['memory']:<10}{Style.RESET_ALL} "
                  f"{status_color}{proc['status']:<10}{Style.RESET_ALL} "
                  f"{PROC_NAME}{proc['name']}{Style.RESET_ALL}")

def get_process_tree():
    """Build a process tree"""
    # Get all processes
    processes = {}
    tree = {}
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'ppid']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                ppid = proc.ppid()
                
                processes[pid] = {
                    "pid": pid,
                    "name": name,
                    "ppid": ppid,
                    "children": []
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Build the tree by connecting parents and children
        for pid, proc in processes.items():
            ppid = proc["ppid"]
            if ppid in processes:
                processes[ppid]["children"].append(proc)
            else:
                # Top-level process (no parent or parent not visible)
                tree[pid] = proc
    
    except Exception as e:
        print(f"{ERROR}Error building process tree: {e}{Style.RESET_ALL}")
    
    return tree

def show_process_tree():
    """Display process tree"""
    tree = get_process_tree()
    
    if not tree:
        print(f"{WARNING}Could not build process tree.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Process Tree:{Style.RESET_ALL}")
    
    def print_tree(processes, indent=0):
        for pid, proc in sorted(processes.items(), key=lambda x: x[1]["name"].lower()):
            prefix = "  " * indent
            print(f"{prefix}{PROC_PID}{proc['pid']} {PROC_NAME}{proc['name']}{Style.RESET_ALL}")
            
            if proc["children"]:
                children_dict = {p["pid"]: p for p in proc["children"]}
                print_tree(children_dict, indent + 1)
    
    print_tree(tree)

def find_process(pid):
    """Find and display detailed information about a specific process"""
    try:
        proc = psutil.Process(pid)
        
        print(f"\n{HEADER}Process Details for PID {pid}:{Style.RESET_ALL}")
        
        # Basic info
        print(f"{INFO}Name:{Style.RESET_ALL} {proc.name()}")
        print(f"{INFO}Status:{Style.RESET_ALL} {proc.status()}")
        print(f"{INFO}Created:{Style.RESET_ALL} {datetime.datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # User info
        try:
            username = proc.username()
            print(f"{INFO}User:{Style.RESET_ALL} {username}")
        except:
            pass
        
        # Parent process
        try:
            parent = proc.parent()
            if parent:
                print(f"{INFO}Parent:{Style.RESET_ALL} {parent.pid} ({parent.name()})")
        except:
            pass
        
        # Command line
        try:
            cmdline = " ".join(proc.cmdline())
            print(f"{INFO}Command:{Style.RESET_ALL} {cmdline}")
        except:
            pass
        
        # CPU and memory
        print(f"{INFO}CPU Usage:{Style.RESET_ALL} {proc.cpu_percent(interval=0.1):.1f}%")
        print(f"{INFO}Memory Usage:{Style.RESET_ALL} {format_bytes(proc.memory_info().rss)}")
        
        # File handles
        try:
            num_files = len(proc.open_files())
            print(f"{INFO}Open Files:{Style.RESET_ALL} {num_files}")
        except:
            pass
        
        # Network connections
        try:
            connections = proc.connections()
            if connections:
                print(f"{INFO}Network Connections:{Style.RESET_ALL} {len(connections)}")
        except:
            pass
        
        # Child processes
        try:
            children = proc.children()
            if children:
                print(f"{INFO}Child Processes:{Style.RESET_ALL} {len(children)}")
                for child in children:
                    print(f"  {PROC_PID}{child.pid} {PROC_NAME}{child.name()}{Style.RESET_ALL}")
        except:
            pass
        
    except psutil.NoSuchProcess:
        print(f"{ERROR}Process with PID {pid} not found.{Style.RESET_ALL}")
    except psutil.AccessDenied:
        print(f"{ERROR}Access denied to process with PID {pid}.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{ERROR}Error getting process details: {e}{Style.RESET_ALL}")

def show_help():
    """Show help for proclist commands"""
    print(f"\n{HEADER}Process Management Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.proclist{DESCRIPTION} - Show process list (sorted by CPU usage)")
    print(f"{COMMAND}  sigma.proclist top <n>{DESCRIPTION} - Show top N processes by CPU")
    print(f"{COMMAND}  sigma.proclist sort <type>{DESCRIPTION} - Sort by: cpu, memory, pid, name, time")
    print(f"{COMMAND}  sigma.proclist detail{DESCRIPTION} - Show detailed process list")
    print(f"{COMMAND}  sigma.proclist find <text>{DESCRIPTION} - Find processes by name")
    print(f"{COMMAND}  sigma.proclist pid <pid>{DESCRIPTION} - Show details for specific PID")
    print(f"{COMMAND}  sigma.proclist tree{DESCRIPTION} - Show process tree")
    print()

def main():
    """Main entry point for proclist module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Default behavior: show process list sorted by CPU
        show_processes()
        return
    
    command = args[0].lower()
    
    if command == "help":
        show_help()
    elif command == "top" and len(args) >= 2:
        try:
            top = int(args[1])
            show_processes(top=top)
        except ValueError:
            print(f"{ERROR}Invalid number: {args[1]}{Style.RESET_ALL}")
            show_help()
    elif command == "sort" and len(args) >= 2:
        sort_by = args[1].lower()
        if sort_by in ["cpu", "memory", "pid", "name", "time"]:
            show_processes(sort_by=sort_by)
        else:
            print(f"{ERROR}Invalid sort type: {sort_by}{Style.RESET_ALL}")
            print(f"{INFO}Valid types: cpu, memory, pid, name, time{Style.RESET_ALL}")
    elif command == "detail":
        show_processes(detailed=True)
    elif command == "find" and len(args) >= 2:
        filter_text = args[1]
        show_processes(filter_text=filter_text)
    elif command == "tree":
        show_process_tree()
    elif command == "pid" and len(args) >= 2:
        try:
            pid = int(args[1])
            find_process(pid)
        except ValueError:
            print(f"{ERROR}Invalid PID: {args[1]}{Style.RESET_ALL}")
    else:
        print(f"{ERROR}Unknown command: {command}{Style.RESET_ALL}")
        show_help()

if __name__ == "__main__":
    # Initialize psutil's CPU monitoring
    psutil.cpu_percent(interval=0.1, percpu=True)
    main() 