import os
import sys
import platform
import psutil
import datetime
import socket
import subprocess
import re
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
SYSINFO_CATEGORY = Fore.YELLOW
SYSINFO_ITEM = Fore.CYAN
SYSINFO_VALUE = Fore.WHITE
SYSINFO_GOOD = Fore.GREEN
SYSINFO_BAD = Fore.RED
SYSINFO_WARNING = Fore.YELLOW

def get_gpu_info():
    """Get GPU information"""
    gpu_info = "Unknown"
    
    try:
        if platform.system() == "Windows":
            # Try using wmic first
            try:
                gpu_output = subprocess.check_output("wmic path win32_VideoController get Name", shell=True).decode("utf-8")
                gpu_output = gpu_output.strip().split("\n")[1:]
                if gpu_output:
                    gpu_info = ", ".join([line.strip() for line in gpu_output if line.strip()])
            except:
                # Fall back to dxdiag
                try:
                    dxdiag = subprocess.check_output("dxdiag /t dxdiag_output.txt", shell=True)
                    # Wait for dxdiag to finish
                    import time
                    time.sleep(2)
                    with open("dxdiag_output.txt", "r") as f:
                        dxdiag_content = f.read()
                    os.remove("dxdiag_output.txt")
                    
                    display_devices = re.findall(r"Card name: (.*)", dxdiag_content)
                    if display_devices:
                        gpu_info = ", ".join(display_devices)
                except:
                    pass
        elif platform.system() == "Linux":
            # Try lspci
            try:
                lspci_output = subprocess.check_output("lspci | grep -i 'vga\\|3d\\|2d'", shell=True).decode("utf-8")
                if lspci_output:
                    # Extract GPU names
                    gpus = []
                    for line in lspci_output.strip().split("\n"):
                        if ":" in line:
                            gpu_name = line.split(":", 2)[-1].strip()
                            gpus.append(gpu_name)
                    if gpus:
                        gpu_info = ", ".join(gpus)
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                # Use system_profiler to get GPU info
                sp_output = subprocess.check_output("system_profiler SPDisplaysDataType | grep 'Chipset Model:'", shell=True).decode("utf-8")
                if sp_output:
                    gpus = []
                    for line in sp_output.strip().split("\n"):
                        if ":" in line:
                            gpu_name = line.split(":", 1)[1].strip()
                            gpus.append(gpu_name)
                    if gpus:
                        gpu_info = ", ".join(gpus)
            except:
                pass
                
    except Exception as e:
        gpu_info = f"Error detecting GPU: {e}"
    
    # Try to use GPUtil as a fallback for NVIDIA GPUs
    if gpu_info == "Unknown":
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_info = ", ".join([gpu.name for gpu in gpus])
        except:
            pass
            
    return gpu_info

def format_bytes(size):
    """Format bytes to human-readable form"""
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    return f"{size:.2f} {power_labels[n]}"

def get_network_info():
    """Get network information"""
    network_info = []
    
    try:
        hostname = socket.gethostname()
        network_info.append(("Hostname", hostname))
        
        # Get IP addresses
        ip_addresses = []
        try:
            interfaces = psutil.net_if_addrs()
            for interface_name, interface_addresses in interfaces.items():
                for address in interface_addresses:
                    if address.family == socket.AF_INET:  # IPv4
                        ip_addresses.append(f"{interface_name}: {address.address}")
        except:
            pass
        
        if ip_addresses:
            network_info.append(("IP Addresses", "\n                  ".join(ip_addresses)))
        
        try:
            # Get default gateway
            if platform.system() == "Windows":
                gateway_output = subprocess.check_output("ipconfig | findstr Gateway", shell=True).decode("utf-8")
                gateways = re.findall(r"Gateway.*: (.*)", gateway_output)
                if gateways:
                    network_info.append(("Default Gateway", gateways[0].strip()))
            else:
                # For Linux/macOS
                gateway_output = subprocess.check_output("ip route | grep default", shell=True).decode("utf-8")
                gateways = re.findall(r"default via (.*) dev", gateway_output)
                if gateways:
                    network_info.append(("Default Gateway", gateways[0].strip()))
        except:
            pass
            
        # Add public IP if we can get it
        try:
            import requests
            public_ip = requests.get("https://api.ipify.org").text
            network_info.append(("Public IP", public_ip))
        except:
            pass
    
    except Exception as e:
        network_info.append(("Error", f"Error getting network info: {e}"))
    
    return network_info

def get_disk_info():
    """Get disk information"""
    disk_info = []
    
    try:
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if platform.system() == "Windows" and "cdrom" in partition.opts:
                # Skip CD-ROM drives on Windows
                continue
                
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                size = format_bytes(usage.total)
                used = format_bytes(usage.used)
                free = format_bytes(usage.free)
                percent = usage.percent
                
                # Determine color based on usage percentage
                if percent >= 90:
                    percent_color = SYSINFO_BAD
                elif percent >= 70:
                    percent_color = SYSINFO_WARNING
                else:
                    percent_color = SYSINFO_GOOD
                    
                disk_info.append((
                    f"Disk {partition.device}",
                    f"{size} total, {used} used, {free} free ({percent_color}{percent}%{SYSINFO_VALUE})"
                ))
            except:
                # Some partitions may not be accessible
                disk_info.append((f"Disk {partition.device}", "Not accessible"))
    except Exception as e:
        disk_info.append(("Error", f"Error getting disk info: {e}"))
    
    return disk_info

def get_cpu_info():
    """Get CPU information"""
    cpu_info = []
    
    try:
        cpu_info.append(("CPU", platform.processor()))
        cpu_info.append(("Architecture", platform.machine()))
        cpu_info.append(("Cores", f"Physical: {psutil.cpu_count(logical=False)}, Logical: {psutil.cpu_count(logical=True)}"))
        
        # Get CPU frequency
        try:
            freq = psutil.cpu_freq()
            if freq:
                cpu_info.append(("Frequency", f"Current: {freq.current:.2f} MHz, Max: {freq.max:.2f} MHz"))
        except:
            pass
        
        # Get CPU usage
        try:
            usage_percent = psutil.cpu_percent(interval=1)
            
            # Determine color based on usage percentage
            if usage_percent >= 90:
                percent_color = SYSINFO_BAD
            elif usage_percent >= 70:
                percent_color = SYSINFO_WARNING
            else:
                percent_color = SYSINFO_GOOD
                
            cpu_info.append(("Usage", f"{percent_color}{usage_percent}%{SYSINFO_VALUE}"))
        except:
            pass
            
        # Try to get more detailed CPU info from OS-specific commands
        if platform.system() == "Windows":
            try:
                model_name = subprocess.check_output("wmic cpu get name", shell=True).decode("utf-8")
                model_name = model_name.strip().split("\n")[1].strip()
                cpu_info.insert(0, ("CPU Model", model_name))
            except:
                pass
                
        elif platform.system() == "Linux":
            try:
                # Try to get CPU info from /proc/cpuinfo
                with open("/proc/cpuinfo", "r") as f:
                    cpuinfo = f.read()
                    
                model_name = re.search(r"model name\s+:\s+(.*)", cpuinfo)
                if model_name:
                    cpu_info.insert(0, ("CPU Model", model_name.group(1)))
            except:
                pass
                
        elif platform.system() == "Darwin":  # macOS
            try:
                model_name = subprocess.check_output("sysctl -n machdep.cpu.brand_string", shell=True).decode("utf-8").strip()
                cpu_info.insert(0, ("CPU Model", model_name))
            except:
                pass
                
    except Exception as e:
        cpu_info.append(("Error", f"Error getting CPU info: {e}"))
    
    return cpu_info

def get_memory_info():
    """Get memory information"""
    memory_info = []
    
    try:
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        total = format_bytes(mem.total)
        used = format_bytes(mem.used)
        available = format_bytes(mem.available)
        percent = mem.percent
        
        # Determine color based on usage percentage
        if percent >= 90:
            percent_color = SYSINFO_BAD
        elif percent >= 70:
            percent_color = SYSINFO_WARNING
        else:
            percent_color = SYSINFO_GOOD
            
        memory_info.append(("RAM", f"{total} total, {used} used, {available} available ({percent_color}{percent}%{SYSINFO_VALUE})"))
        
        swap_total = format_bytes(swap.total)
        swap_used = format_bytes(swap.used)
        swap_free = format_bytes(swap.free)
        swap_percent = swap.percent
        
        # Determine color based on swap usage percentage
        if swap_percent >= 50:  # Swap usage is generally worse at lower percentages
            swap_color = SYSINFO_BAD
        elif swap_percent >= 25:
            swap_color = SYSINFO_WARNING
        else:
            swap_color = SYSINFO_GOOD
            
        memory_info.append(("Swap", f"{swap_total} total, {swap_used} used, {swap_free} free ({swap_color}{swap_percent}%{SYSINFO_VALUE})"))
        
    except Exception as e:
        memory_info.append(("Error", f"Error getting memory info: {e}"))
    
    return memory_info

def get_os_info():
    """Get OS information"""
    os_info = []
    
    try:
        os_info.append(("OS", platform.system()))
        os_info.append(("Version", platform.version()))
        os_info.append(("Platform", platform.platform()))
        
        # Get more detailed OS info
        if platform.system() == "Windows":
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
                product_name = winreg.QueryValueEx(key, "ProductName")[0]
                os_info.append(("Product", product_name))
                
                build = winreg.QueryValueEx(key, "CurrentBuildNumber")[0]
                os_info.append(("Build", build))
                
                try:
                    edition = winreg.QueryValueEx(key, "EditionID")[0]
                    os_info.append(("Edition", edition))
                except:
                    pass
            except:
                pass
        elif platform.system() == "Linux":
            try:
                # Try to get Linux distribution info
                try:
                    import distro
                    dist_name = distro.name()
                    dist_version = distro.version()
                    os_info.append(("Distribution", f"{dist_name} {dist_version}"))
                except ImportError:
                    # Fall back to reading /etc/os-release
                    try:
                        with open("/etc/os-release", "r") as f:
                            os_release = f.read()
                            name_match = re.search(r'PRETTY_NAME="([^"]+)"', os_release)
                            if name_match:
                                os_info.append(("Distribution", name_match.group(1)))
                    except:
                        pass
            except:
                pass
        elif platform.system() == "Darwin":  # macOS
            try:
                # Get macOS name and version
                mac_ver = platform.mac_ver()
                os_info.append(("macOS Version", mac_ver[0]))
                
                # Map version to name
                mac_names = {
                    "10.15": "Catalina",
                    "11": "Big Sur",
                    "12": "Monterey",
                    "13": "Ventura",
                    "14": "Sonoma"
                }
                
                # Check for major version first, then major.minor
                major_ver = mac_ver[0].split(".")[0]
                major_minor_ver = ".".join(mac_ver[0].split(".")[:2])
                
                name = mac_names.get(major_ver, mac_names.get(major_minor_ver, "Unknown"))
                os_info.append(("macOS Name", name))
            except:
                pass
                
        # Get boot time
        try:
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            # Format uptime
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = ""
            if days > 0:
                uptime_str += f"{days} days, "
            uptime_str += f"{hours:02}:{minutes:02}:{seconds:02}"
            
            os_info.append(("Boot Time", boot_time.strftime("%Y-%m-%d %H:%M:%S")))
            os_info.append(("Uptime", uptime_str))
        except:
            pass
            
    except Exception as e:
        os_info.append(("Error", f"Error getting OS info: {e}"))
    
    return os_info

def show_sysinfo():
    """Display detailed system information"""
    print(f"\n{HEADER}╔══ System Information ══════════════════════════╗{Style.RESET_ALL}")
    
    # OS Information
    print(f"\n{SYSINFO_CATEGORY}Operating System:{Style.RESET_ALL}")
    for item, value in get_os_info():
        print(f"{SYSINFO_ITEM}  {item:<15}: {SYSINFO_VALUE}{value}")
    
    # CPU Information
    print(f"\n{SYSINFO_CATEGORY}CPU:{Style.RESET_ALL}")
    for item, value in get_cpu_info():
        print(f"{SYSINFO_ITEM}  {item:<15}: {SYSINFO_VALUE}{value}")
    
    # Memory Information
    print(f"\n{SYSINFO_CATEGORY}Memory:{Style.RESET_ALL}")
    for item, value in get_memory_info():
        print(f"{SYSINFO_ITEM}  {item:<15}: {SYSINFO_VALUE}{value}")
    
    # GPU Information
    gpu_info = get_gpu_info()
    print(f"\n{SYSINFO_CATEGORY}Graphics:{Style.RESET_ALL}")
    print(f"{SYSINFO_ITEM}  {'GPU':<15}: {SYSINFO_VALUE}{gpu_info}")
    
    # Disk Information
    print(f"\n{SYSINFO_CATEGORY}Storage:{Style.RESET_ALL}")
    for item, value in get_disk_info():
        print(f"{SYSINFO_ITEM}  {item:<15}: {SYSINFO_VALUE}{value}")
    
    # Network Information
    print(f"\n{SYSINFO_CATEGORY}Network:{Style.RESET_ALL}")
    for item, value in get_network_info():
        print(f"{SYSINFO_ITEM}  {item:<15}: {SYSINFO_VALUE}{value}")
    
    # Python Information
    print(f"\n{SYSINFO_CATEGORY}Python:{Style.RESET_ALL}")
    print(f"{SYSINFO_ITEM}  {'Version':<15}: {SYSINFO_VALUE}{platform.python_version()}")
    print(f"{SYSINFO_ITEM}  {'Implementation':<15}: {SYSINFO_VALUE}{platform.python_implementation()}")
    print(f"{SYSINFO_ITEM}  {'Path':<15}: {SYSINFO_VALUE}{sys.executable}")
    
    print(f"\n{HEADER}╚{'═' * 45}╝{Style.RESET_ALL}")

def main():
    """Main entry point for the sysinfo module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # For now, just show all system info regardless of arguments
    show_sysinfo()

if __name__ == "__main__":
    main() 