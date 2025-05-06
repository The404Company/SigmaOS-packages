import os
import sys
import platform
import subprocess
import time
import re
import socket
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
PING_SUCCESS = Fore.GREEN
PING_FAILURE = Fore.RED
PING_INFO = Fore.CYAN
PING_STATS = Fore.YELLOW

def ping_host(host, count=4, timeout=2, interval=1.0):
    """Ping a host and return results"""
    results = []
    total_time = 0
    successful = 0
    times = []
    
    print(f"{HEADER}Pinging {host}...{Style.RESET_ALL}")
    
    try:
        # First resolve hostname to IP if possible
        try:
            ip = socket.gethostbyname(host)
            if ip != host:
                print(f"{INFO}Resolved {host} to {ip}{Style.RESET_ALL}")
        except:
            ip = host
        
        # Different ping command parameters based on OS
        param = "-n" if platform.system().lower() == "windows" else "-c"
        timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
        
        for i in range(count):
            start_time = time.time()
            
            # Construct ping command
            command = ["ping", param, "1", timeout_param, str(timeout * 1000 if platform.system().lower() == "windows" else timeout), ip]
            
            try:
                # Use errors='replace' to handle encoding issues
                output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True, encoding='utf-8', errors='replace')
                status = "Success"
                
                # Extract time from ping output
                time_match = re.search(r"time[=<]([0-9.]+)", output)
                if time_match:
                    ping_time = float(time_match.group(1))
                    times.append(ping_time)
                    total_time += ping_time
                    successful += 1
                    print(f"{PING_SUCCESS}Reply from {ip}: time={ping_time}ms{Style.RESET_ALL}")
                else:
                    print(f"{PING_SUCCESS}Reply from {ip}: time=Unknown{Style.RESET_ALL}")
                    
            except subprocess.CalledProcessError:
                status = "Timeout"
                print(f"{PING_FAILURE}Request timed out for {ip}{Style.RESET_ALL}")
                
            results.append({
                "seq": i + 1,
                "status": status,
                "time": time.time() - start_time
            })
            
            # Sleep between pings (except for the last one)
            if i < count - 1:
                time.sleep(interval)
    
    except Exception as e:
        print(f"{ERROR}Error pinging {host}: {e}{Style.RESET_ALL}")
        return False
    
    # Print summary
    print(f"\n{PING_STATS}Ping statistics for {ip}:{Style.RESET_ALL}")
    
    # Calculate packet loss
    packet_loss = 100 - (successful / count * 100)
    
    print(f"{PING_INFO}    Packets: Sent = {count}, Received = {successful}, Lost = {count - successful} ({packet_loss:.0f}% loss){Style.RESET_ALL}")
    
    # Calculate time statistics if we have successful pings
    if successful > 0:
        min_time = min(times) if times else 0
        max_time = max(times) if times else 0
        avg_time = total_time / successful if successful else 0
        
        print(f"{PING_INFO}    Approximate round trip times in milliseconds:{Style.RESET_ALL}")
        print(f"{PING_INFO}    Minimum = {min_time:.2f}ms, Maximum = {max_time:.2f}ms, Average = {avg_time:.2f}ms{Style.RESET_ALL}")
    
    # Return overall success or failure
    return successful > 0

def traceroute(host):
    """Perform a traceroute to a host"""
    print(f"{HEADER}Traceroute to {host}...{Style.RESET_ALL}")
    
    try:
        # Resolve hostname to IP if possible
        try:
            ip = socket.gethostbyname(host)
            if ip != host:
                print(f"{INFO}Resolved {host} to {ip}{Style.RESET_ALL}")
        except:
            ip = host
        
        # Different traceroute command based on OS
        command = ["tracert" if platform.system().lower() == "windows" else "traceroute", ip]
        
        # Use encoding='utf-8' and errors='replace' to handle encoding issues
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                universal_newlines=True, encoding='utf-8', errors='replace')
        
        # Print results in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                
                # Color the line based on content
                if "Request timed out" in line or "* * *" in line:
                    print(f"{PING_FAILURE}{line}{Style.RESET_ALL}")
                elif "ms" in line and (line.startswith("  ") or line[0].isdigit()):
                    # Try to highlight just the IP or hostname in the line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if re.match(r"\d+\.\d+\.\d+\.\d+", part) or "." in part and not part.endswith("ms") and not part.endswith("ms]"):
                            parts[i] = f"{INFO}{part}{Style.RESET_ALL}"
                    
                    # Color the response times
                    colored_line = " ".join(parts)
                    colored_line = re.sub(r"(\d+)ms", f"{PING_SUCCESS}\\1ms{Style.RESET_ALL}", colored_line)
                    print(colored_line)
                else:
                    print(line)
        
        stderr = process.stderr.read()
        if stderr:
            print(f"{ERROR}{stderr}{Style.RESET_ALL}")
            
    except Exception as e:
        print(f"{ERROR}Error performing traceroute to {host}: {e}{Style.RESET_ALL}")
        return False
    
    return True

def show_help():
    """Show help information for ping commands"""
    print(f"\n{HEADER}Network Connectivity Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.ping <host>{DESCRIPTION} - Ping a host (default 4 times)")
    print(f"{COMMAND}  sigma.ping <host> <count>{DESCRIPTION} - Ping a host N times")
    print(f"{COMMAND}  sigma.ping <host> <count> <timeout>{DESCRIPTION} - Ping with custom timeout (seconds)")
    print(f"{COMMAND}  sigma.ping <host> trace{DESCRIPTION} - Perform a traceroute to host")
    print()

def main():
    """Main entry point for the ping module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        show_help()
        return
    
    host = args[0]
    
    # Handle traceroute
    if len(args) >= 2 and args[1].lower() in ["trace", "traceroute", "tracert"]:
        traceroute(host)
        return
    
    # Handle regular ping
    count = 4  # Default
    timeout = 2  # Default
    
    if len(args) >= 2:
        try:
            count = int(args[1])
        except ValueError:
            print(f"{ERROR}Invalid ping count. Using default (4).{Style.RESET_ALL}")
    
    if len(args) >= 3:
        try:
            timeout = float(args[2])
        except ValueError:
            print(f"{ERROR}Invalid timeout. Using default (2 seconds).{Style.RESET_ALL}")
    
    ping_host(host, count=count, timeout=timeout)

if __name__ == "__main__":
    main() 