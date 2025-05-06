import os
import sys
import time
import platform
import subprocess
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
WIFI_SSID = Fore.CYAN
WIFI_SIGNAL = Fore.GREEN
WIFI_SECURITY = Fore.YELLOW
WIFI_CONNECTED = Fore.MAGENTA

# Check if running on Windows
IS_WINDOWS = platform.system().lower() == "windows"

# List of dependencies
DEPENDENCIES = ["pywifi", "comtypes"]

# Check and install dependencies if needed
missing_deps = []
for dep in DEPENDENCIES:
    try:
        __import__(dep)
    except ImportError:
        missing_deps.append(dep)

# Install missing dependencies
if missing_deps:
    print(f"{INFO}Installing required dependencies: {', '.join(missing_deps)}{Style.RESET_ALL}")
    for dep in missing_deps:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL)
            print(f"{SUCCESS}Successfully installed {dep}!{Style.RESET_ALL}")
        except Exception as e:
            print(f"{ERROR}Failed to install {dep}: {e}{Style.RESET_ALL}")
            print(f"{INFO}You can manually install it with: pip install {dep}{Style.RESET_ALL}")

# Now try to import required modules
try:
    import pywifi
    from pywifi import const
    PYWIFI_AVAILABLE = True
except ImportError:
    PYWIFI_AVAILABLE = False
    print(f"{ERROR}Failed to import pywifi even after installation attempt.{Style.RESET_ALL}")
    print(f"{INFO}Please manually install the dependencies with: pip install pywifi comtypes{Style.RESET_ALL}")

def check_wifi_support():
    """Check if WiFi management is supported on this system"""
    if not IS_WINDOWS:
        print(f"{ERROR}This module currently only supports Windows.{Style.RESET_ALL}")
        return False
    
    if not PYWIFI_AVAILABLE:
        print(f"{ERROR}The required dependencies couldn't be imported.{Style.RESET_ALL}")
        print(f"{INFO}Please manually install them with: pip install pywifi comtypes{Style.RESET_ALL}")
        return False
    
    # Check if the WiFi interface can be initialized
    try:
        iface = get_wifi_interface(skip_check=True)
        if not iface:
            return False
        # Try to check the interface status to make sure it's working
        iface.status()
        return True
    except Exception as e:
        print(f"{ERROR}Error initializing WiFi interface: {e}{Style.RESET_ALL}")
        print(f"{INFO}Make sure your WiFi adapter is enabled and working properly.{Style.RESET_ALL}")
        return False

def get_wifi_interface(skip_check=False):
    """Get the first available WiFi interface"""
    if not skip_check and not check_wifi_support():
        return None
    
    wifi = pywifi.PyWiFi()
    if len(wifi.interfaces()) == 0:
        print(f"{ERROR}No WiFi interfaces found.{Style.RESET_ALL}")
        return None
    
    iface = wifi.interfaces()[0]
    return iface

def format_signal_strength(signal):
    """Format signal strength as bars"""
    # Convert dBm to percentage
    # -30 dBm is excellent (100%), -90 dBm is poor (0%)
    if signal >= -50:
        bars = "▂▄▆█"  # Excellent
        color = SUCCESS
    elif signal >= -60:
        bars = "▂▄▆_"  # Good
        color = SUCCESS
    elif signal >= -70:
        bars = "▂▄__"  # Fair
        color = WARNING
    elif signal >= -80:
        bars = "▂___"  # Poor
        color = WARNING
    else:
        bars = "____"  # Very poor
        color = ERROR
    
    percentage = max(0, min(100, int((signal + 90) * (100 / 60))))
    return f"{color}{bars} {percentage}%{Style.RESET_ALL}"

def format_security(akm_type):
    """Format security type"""
    if akm_type == const.AKM_TYPE_NONE:
        return f"{ERROR}OPEN{Style.RESET_ALL}"
    elif akm_type == const.AKM_TYPE_WPA:
        return f"{WIFI_SECURITY}WPA{Style.RESET_ALL}"
    elif akm_type == const.AKM_TYPE_WPAPSK:
        return f"{WIFI_SECURITY}WPA-PSK{Style.RESET_ALL}"
    elif akm_type == const.AKM_TYPE_WPA2:
        return f"{WIFI_SECURITY}WPA2{Style.RESET_ALL}"
    elif akm_type == const.AKM_TYPE_WPA2PSK:
        return f"{WIFI_SECURITY}WPA2-PSK{Style.RESET_ALL}"
    else:
        return f"{WIFI_SECURITY}UNKNOWN{Style.RESET_ALL}"

def scan_networks():
    """Scan for available WiFi networks and return results"""
    iface = get_wifi_interface()
    if not iface:
        return []
    
    print(f"{INFO}Scanning for WiFi networks...{Style.RESET_ALL}")
    
    try:
        iface.scan()
        time.sleep(5)  # Give some time for the scan to complete
        
        scan_results = iface.scan_results()
        
        # Sort by signal strength
        scan_results.sort(key=lambda x: x.signal, reverse=True)
        
        return scan_results
    except Exception as e:
        print(f"{ERROR}Error scanning WiFi networks: {e}{Style.RESET_ALL}")
        return []

def list_networks():
    """Scan and display available WiFi networks"""
    if not check_wifi_support():
        return
    
    networks = scan_networks()
    
    if not networks:
        print(f"{WARNING}No WiFi networks found.{Style.RESET_ALL}")
        return
    
    print(f"\n{HEADER}Available WiFi Networks:{Style.RESET_ALL}")
    print(f"{COMMAND}{'SSID':<25} {'Signal':<15} {'Security':<12} {'Status'}{Style.RESET_ALL}")
    print("-" * 65)
    
    # Get currently connected network
    current_network = get_connected_network()
    
    for network in networks:
        ssid = network.ssid
        signal = network.signal
        akm = const.AKM_TYPE_NONE
        if len(network.akm) > 0:
            akm = network.akm[0]
        
        # Check if this is the connected network
        status = ""
        if current_network and ssid == current_network:
            status = f"{WIFI_CONNECTED}CONNECTED{Style.RESET_ALL}"
            
        print(f"{WIFI_SSID}{ssid:<25}{Style.RESET_ALL} "
              f"{format_signal_strength(signal):<15} "
              f"{format_security(akm):<12} "
              f"{status}")

def get_connected_network():
    """Get the currently connected WiFi network SSID"""
    iface = get_wifi_interface()
    if not iface:
        return None
    
    try:
        if iface.status() == const.IFACE_CONNECTED:
            # Get the profile of the connected network
            profiles = iface.network_profiles()
            for profile in profiles:
                if iface.status() == const.IFACE_CONNECTED:
                    return profile.ssid
    except Exception as e:
        print(f"{ERROR}Error getting connected network: {e}{Style.RESET_ALL}")
    
    return None

def show_connection_status():
    """Show current WiFi connection status"""
    if not check_wifi_support():
        return
    
    iface = get_wifi_interface()
    if not iface:
        return
    
    print(f"\n{HEADER}WiFi Connection Status:{Style.RESET_ALL}")
    
    try:
        status_code = iface.status()
        status_text = "UNKNOWN"
        
        if status_code == const.IFACE_DISCONNECTED:
            status_text = f"{WARNING}DISCONNECTED{Style.RESET_ALL}"
        elif status_code == const.IFACE_SCANNING:
            status_text = f"{INFO}SCANNING{Style.RESET_ALL}"
        elif status_code == const.IFACE_CONNECTING:
            status_text = f"{INFO}CONNECTING{Style.RESET_ALL}"
        elif status_code == const.IFACE_CONNECTED:
            status_text = f"{SUCCESS}CONNECTED{Style.RESET_ALL}"
        elif status_code == const.IFACE_INACTIVE:
            status_text = f"{ERROR}INACTIVE{Style.RESET_ALL}"
        
        print(f"{INFO}Interface Status:{Style.RESET_ALL} {status_text}")
        
        connected_ssid = get_connected_network()
        if connected_ssid:
            print(f"{INFO}Connected to:{Style.RESET_ALL} {WIFI_SSID}{connected_ssid}{Style.RESET_ALL}")
            
            # Try to get signal strength of connected network
            networks = scan_networks()
            for network in networks:
                if network.ssid == connected_ssid:
                    print(f"{INFO}Signal Strength:{Style.RESET_ALL} {format_signal_strength(network.signal)}")
                    break
    except Exception as e:
        print(f"{ERROR}Error getting connection status: {e}{Style.RESET_ALL}")

def connect_to_network(ssid, password=None):
    """Connect to a specific WiFi network"""
    if not check_wifi_support():
        return False
    
    iface = get_wifi_interface()
    if not iface:
        return False
    
    print(f"{INFO}Connecting to {WIFI_SSID}{ssid}{Style.RESET_ALL}...")
    
    try:
        # Find the network in scan results to determine security type
        networks = scan_networks()
        target_network = None
        
        for network in networks:
            if network.ssid == ssid:
                target_network = network
                break
        
        if not target_network:
            print(f"{ERROR}Network '{ssid}' not found.{Style.RESET_ALL}")
            print(f"{INFO}Make sure the network is in range and broadcasting its SSID.{Style.RESET_ALL}")
            return False
        
        # Disconnect from current network if connected
        iface.disconnect()
        time.sleep(1)
        
        # Create a new profile
        profile = pywifi.Profile()
        profile.ssid = ssid
        
        # Set security parameters based on the network's security type
        if len(target_network.akm) == 0 or target_network.akm[0] == const.AKM_TYPE_NONE:
            # Open network
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(const.AKM_TYPE_NONE)
            profile.cipher = const.CIPHER_TYPE_NONE
        else:
            # Secured network
            profile.auth = const.AUTH_ALG_OPEN
            profile.akm.append(target_network.akm[0])
            
            if target_network.cipher == const.CIPHER_TYPE_CCMP:
                profile.cipher = const.CIPHER_TYPE_CCMP
            elif target_network.cipher == const.CIPHER_TYPE_TKIP:
                profile.cipher = const.CIPHER_TYPE_TKIP
            else:
                profile.cipher = const.CIPHER_TYPE_CCMP  # Default to CCMP
            
            if not password:
                print(f"{ERROR}Password required for this network.{Style.RESET_ALL}")
                return False
            
            profile.key = password
        
        # Remove existing profile with the same SSID
        iface.remove_all_network_profiles()
        
        # Add the new profile
        tmp_profile = iface.add_network_profile(profile)
        
        # Connect
        iface.connect(tmp_profile)
        
        # Wait for connection
        print(f"{INFO}Waiting for connection...{Style.RESET_ALL}")
        max_wait = 10  # seconds
        for i in range(max_wait):
            time.sleep(1)
            if iface.status() == const.IFACE_CONNECTED:
                print(f"{SUCCESS}Successfully connected to {WIFI_SSID}{ssid}{Style.RESET_ALL}!")
                return True
        
        print(f"{ERROR}Failed to connect to {ssid}.{Style.RESET_ALL}")
        print(f"{INFO}Please check the password and try again.{Style.RESET_ALL}")
        return False
    
    except Exception as e:
        print(f"{ERROR}Error connecting to network: {e}{Style.RESET_ALL}")
        return False

def disconnect_network():
    """Disconnect from the current WiFi network"""
    if not check_wifi_support():
        return False
    
    iface = get_wifi_interface()
    if not iface:
        return False
    
    try:
        if iface.status() == const.IFACE_CONNECTED:
            connected_ssid = get_connected_network()
            print(f"{INFO}Disconnecting from {WIFI_SSID}{connected_ssid or 'network'}{Style.RESET_ALL}...")
            
            iface.disconnect()
            time.sleep(1)
            
            if iface.status() in [const.IFACE_DISCONNECTED, const.IFACE_INACTIVE]:
                print(f"{SUCCESS}Successfully disconnected.{Style.RESET_ALL}")
                return True
            else:
                print(f"{ERROR}Failed to disconnect.{Style.RESET_ALL}")
                return False
        else:
            print(f"{WARNING}Not currently connected to any network.{Style.RESET_ALL}")
            return True
    except Exception as e:
        print(f"{ERROR}Error disconnecting from network: {e}{Style.RESET_ALL}")
        return False

def show_help():
    """Show help information for the WiFi module"""
    print(f"\n{HEADER}WiFi Management Commands:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.wifi{DESCRIPTION} - Show WiFi connection status")
    print(f"{COMMAND}  sigma.wifi scan{DESCRIPTION} - Scan and list available WiFi networks")
    print(f"{COMMAND}  sigma.wifi connect <ssid> [password]{DESCRIPTION} - Connect to a specific network")
    print(f"{INFO}      For SSIDs with spaces, use quotes: {COMMAND}sigma.wifi connect \"My Network\" password{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.wifi disconnect{DESCRIPTION} - Disconnect from current network")
    print(f"{COMMAND}  sigma.wifi status{DESCRIPTION} - Show current WiFi connection status")
    print()

def main():
    """Main entry point for the WiFi module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Default behavior: show connection status
        show_connection_status()
        show_help()
        return
    
    command = args[0].lower()
    
    if command == "help":
        show_help()
    elif command == "scan":
        list_networks()
    elif command == "status":
        show_connection_status()
    elif command == "connect" and len(args) >= 2:
        # Check if the SSID is quoted
        if len(args) >= 3 and args[1].startswith('"') and not args[1].endswith('"'):
            # Find the end of the quoted SSID
            quoted_ssid_parts = []
            end_quote_found = False
            
            for i in range(1, len(args)):
                part = args[i]
                quoted_ssid_parts.append(part)
                
                if part.endswith('"'):
                    end_quote_found = True
                    break
            
            if end_quote_found:
                # Join the parts and remove quotes
                ssid = ' '.join(quoted_ssid_parts).strip('"')
                # Password is the next argument after the quoted SSID
                password = args[len(quoted_ssid_parts) + 1] if len(args) > len(quoted_ssid_parts) + 1 else None
            else:
                # If no end quote is found, treat the first argument as the SSID
                ssid = args[1].strip('"')
                password = args[2] if len(args) >= 3 else None
        else:
            # Handle SSID with quotes in a single argument (e.g., "My Network")
            ssid = args[1].strip('"')
            password = args[2] if len(args) >= 3 else None
            
        connect_to_network(ssid, password)
    elif command == "disconnect":
        disconnect_network()
    else:
        print(f"{ERROR}Unknown command: {command}{Style.RESET_ALL}")
        show_help()

if __name__ == "__main__":
    main() 