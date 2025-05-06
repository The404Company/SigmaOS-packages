import os
import sys
import subprocess
import platform
import socket
import time
import re
import psutil
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
NET_LOCAL = Fore.CYAN
NET_REMOTE = Fore.YELLOW
NET_STATE = Fore.GREEN
NET_PID = Fore.WHITE
NET_PROGRAM = Fore.LIGHTBLUE_EX

def format_bytes(size, per_second=False):
    """Format bytes to human-readable form"""
    power = 2**10
    n = 0
    power_labels = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /= power
        n += 1
    suffix = "/s" if per_second else ""
    return f"{size:.2f} {power_labels[n]}{suffix}"

def get_process_name(pid):
    """Get process name for a PID"""
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown"

def get_connections():
    """Get active network connections"""
    connections = []
    
    try:
        # Use psutil for cross-platform compatibility
        net_connections = psutil.net_connections(kind='inet')
        
        for conn in net_connections:
            status = conn.status
            
            # Skip connections in CLOSE_WAIT state
            if status == "CLOSE_WAIT":
                continue
                
            local_address = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "Unknown"
            remote_address = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "-"
            
            pid = conn.pid or ""
            program = get_process_name(pid) if pid else ""
            
            # Add color based on state
            if status == "ESTABLISHED":
                status_color = SUCCESS
            elif status == "LISTEN":
                status_color = INFO
            elif status in ["FIN_WAIT1", "FIN_WAIT2", "TIME_WAIT"]:
                status_color = WARNING
            else:
                status_color = DESCRIPTION
            
            connections.append({
                "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                "local": local_address,
                "remote": remote_address,
                "state": status,
                "state_color": status_color,
                "pid": pid,
                "program": program
            })
        
    except Exception as e:
        print(f"{ERROR}Error getting connections: {e}{Style.RESET_ALL}")
    
    return connections

def get_network_stats():
    """Get network interface statistics"""
    stats = []
    
    try:
        # Get network counters
        counters = psutil.net_io_counters(pernic=True)
        
        # First pass to get initial values
        initial = {}
        for interface, data in counters.items():
            initial[interface] = {
                "bytes_sent": data.bytes_sent,
                "bytes_recv": data.bytes_recv,
                "packets_sent": data.packets_sent,
                "packets_recv": data.packets_recv,
                "errin": data.errin,
                "errout": data.errout,
                "dropin": data.dropin,
                "dropout": data.dropout
            }
        
        # Wait a bit to calculate rates
        time.sleep(1)
        
        # Second pass to calculate rates
        counters = psutil.net_io_counters(pernic=True)
        
        for interface, data in counters.items():
            if interface in initial:
                # Calculate rates
                bytes_sent_rate = data.bytes_sent - initial[interface]["bytes_sent"]
                bytes_recv_rate = data.bytes_recv - initial[interface]["bytes_recv"]
                packets_sent_rate = data.packets_sent - initial[interface]["packets_sent"]
                packets_recv_rate = data.packets_recv - initial[interface]["packets_recv"]
                
                # Only show active interfaces or if explicitly asked
                if bytes_sent_rate > 0 or bytes_recv_rate > 0:
                    stats.append({
                        "interface": interface,
                        "bytes_sent": data.bytes_sent,
                        "bytes_recv": data.bytes_recv,
                        "bytes_sent_rate": bytes_sent_rate,
                        "bytes_recv_rate": bytes_recv_rate,
                        "packets_sent": data.packets_sent,
                        "packets_recv": data.packets_recv,
                        "packets_sent_rate": packets_sent_rate,
                        "packets_recv_rate": packets_recv_rate,
                        "errin": data.errin,
                        "errout": data.errout,
                        "dropin": data.dropin,
                        "dropout": data.dropout
                    })
    
    except Exception as e:
        print(f"{ERROR}Error getting network stats: {e}{Style.RESET_ALL}")
    
    return stats

def show_connections():
    """Display active network connections"""
    connections = get_connections()
    
    if not connections:
        print(f"{WARNING}No active connections found.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Active Network Connections:{Style.RESET_ALL}")
    print(f"{COMMAND}{'Proto':<6} {'Local Address':<25} {'Remote Address':<25} {'State':<15} {'PID':<7} Program{Style.RESET_ALL}")
    print("-" * 90)
    
    for conn in connections:
        state = conn["state"]
        pid = conn["pid"] if conn["pid"] else "-"
        program = conn["program"] if conn["program"] else "-"
        
        print(f"{INFO}{conn['protocol']:<6}{Style.RESET_ALL} "
              f"{NET_LOCAL}{conn['local']:<25}{Style.RESET_ALL} "
              f"{NET_REMOTE}{conn['remote']:<25}{Style.RESET_ALL} "
              f"{conn['state_color']}{state:<15}{Style.RESET_ALL} "
              f"{NET_PID}{pid:<7}{Style.RESET_ALL} "
              f"{NET_PROGRAM}{program}{Style.RESET_ALL}")

def show_network_stats():
    """Display network interface statistics"""
    stats = get_network_stats()
    
    if not stats:
        print(f"{WARNING}No active network interfaces found.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Network Interface Statistics:{Style.RESET_ALL}")
    print(f"{COMMAND}{'Interface':<15} {'Rx Rate':<12} {'Tx Rate':<12} {'Rx Total':<12} {'Tx Total':<12} {'Rx Packets':<12} {'Tx Packets':<12}{Style.RESET_ALL}")
    print("-" * 90)
    
    for stat in stats:
        interface = stat["interface"]
        bytes_recv_rate = format_bytes(stat["bytes_recv_rate"], True)
        bytes_sent_rate = format_bytes(stat["bytes_sent_rate"], True)
        bytes_recv = format_bytes(stat["bytes_recv"])
        bytes_sent = format_bytes(stat["bytes_sent"])
        
        # Use colors based on activity
        if stat["bytes_recv_rate"] > 1024*1024:  # More than 1 MB/s
            recv_color = SUCCESS
        elif stat["bytes_recv_rate"] > 1024:  # More than 1 KB/s
            recv_color = INFO
        else:
            recv_color = DESCRIPTION
            
        if stat["bytes_sent_rate"] > 1024*1024:  # More than 1 MB/s
            sent_color = SUCCESS
        elif stat["bytes_sent_rate"] > 1024:  # More than 1 KB/s
            sent_color = INFO
        else:
            sent_color = DESCRIPTION
            
        print(f"{INFO}{interface:<15}{Style.RESET_ALL} "
              f"{recv_color}{bytes_recv_rate:<12}{Style.RESET_ALL} "
              f"{sent_color}{bytes_sent_rate:<12}{Style.RESET_ALL} "
              f"{DESCRIPTION}{bytes_recv:<12} {bytes_sent:<12} {stat['packets_recv']:<12} {stat['packets_sent']:<12}{Style.RESET_ALL}")
    
    # Display errors and drops if any
    has_errors = False
    for stat in stats:
        if stat["errin"] > 0 or stat["errout"] > 0 or stat["dropin"] > 0 or stat["dropout"] > 0:
            if not has_errors:
                print(f"\n{HEADER}Interface Errors and Drops:{Style.RESET_ALL}")
                print(f"{COMMAND}{'Interface':<15} {'Rx Errors':<10} {'Tx Errors':<10} {'Rx Drops':<10} {'Tx Drops':<10}{Style.RESET_ALL}")
                print("-" * 60)
                has_errors = True
                
            print(f"{INFO}{stat['interface']:<15}{Style.RESET_ALL} "
                  f"{ERROR}{stat['errin']:<10}{Style.RESET_ALL} "
                  f"{ERROR}{stat['errout']:<10}{Style.RESET_ALL} "
                  f"{WARNING}{stat['dropin']:<10}{Style.RESET_ALL} "
                  f"{WARNING}{stat['dropout']:<10}{Style.RESET_ALL}")

def get_listening_ports():
    """Get all listening ports sorted by port number"""
    listening = []
    
    try:
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN':
                pid = conn.pid or 0
                program = get_process_name(pid) if pid else "Unknown"
                
                listening.append({
                    "protocol": "TCP" if conn.type == socket.SOCK_STREAM else "UDP",
                    "port": conn.laddr.port,
                    "address": conn.laddr.ip,
                    "pid": pid,
                    "program": program
                })
    
    except Exception as e:
        print(f"{ERROR}Error getting listening ports: {e}{Style.RESET_ALL}")
    
    # Sort by port number
    return sorted(listening, key=lambda x: x["port"])

def show_listening_ports():
    """Display all listening ports"""
    listening = get_listening_ports()
    
    if not listening:
        print(f"{WARNING}No listening ports found.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Listening Ports:{Style.RESET_ALL}")
    print(f"{COMMAND}{'Proto':<6} {'Address':<25} {'Port':<8} {'PID':<7} Program{Style.RESET_ALL}")
    print("-" * 80)
    
    for l in listening:
        port = l["port"]
        address = l["address"]
        
        # Highlight well-known ports differently
        if port < 1024:
            port_color = WARNING
        else:
            port_color = SUCCESS
            
        print(f"{INFO}{l['protocol']:<6}{Style.RESET_ALL} "
              f"{NET_LOCAL}{address:<25}{Style.RESET_ALL} "
              f"{port_color}{port:<8}{Style.RESET_ALL} "
              f"{NET_PID}{l['pid']:<7}{Style.RESET_ALL} "
              f"{NET_PROGRAM}{l['program']}{Style.RESET_ALL}")

def show_help():
    """Show help for netstat commands"""
    print(f"\n{HEADER}Network Statistics Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.netstat{DESCRIPTION} - Show all network information")
    print(f"{COMMAND}  sigma.netstat conn{DESCRIPTION} - Show active connections")
    print(f"{COMMAND}  sigma.netstat listen{DESCRIPTION} - Show listening ports")
    print(f"{COMMAND}  sigma.netstat stats{DESCRIPTION} - Show interface statistics")
    print()

def main():
    """Main entry point for netstat module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Show all information by default
        show_connections()
        print()
        show_listening_ports()
        print()
        show_network_stats()
        return
    
    command = args[0].lower()
    
    if command == "help":
        show_help()
    elif command in ["conn", "connections"]:
        show_connections()
    elif command in ["listen", "listening", "ports"]:
        show_listening_ports()
    elif command in ["stats", "interfaces"]:
        show_network_stats()
    else:
        print(f"{ERROR}Unknown command: {command}{Style.RESET_ALL}")
        show_help()

if __name__ == "__main__":
    main() 