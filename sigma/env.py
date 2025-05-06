import os
import sys
import json
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

def get_sigmaos_root():
    """Returns the path to the SigmaOS root directory"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(package_dir))

def get_env_file_path():
    """Returns the path to the user.env file"""
    return os.path.join(get_sigmaos_root(), "user.env")

def load_env_variables():
    """Load environment variables from user.env file"""
    env_file = get_env_file_path()
    if not os.path.exists(env_file):
        return {}
    
    try:
        with open(env_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"{ERROR}Error: user.env file is corrupted.{Style.RESET_ALL}")
        return {}
    except Exception as e:
        print(f"{ERROR}Error loading environment variables: {e}{Style.RESET_ALL}")
        return {}

def save_env_variables(variables):
    """Save environment variables to user.env file"""
    env_file = get_env_file_path()
    try:
        with open(env_file, 'w') as f:
            json.dump(variables, f, indent=4)
        return True
    except Exception as e:
        print(f"{ERROR}Error saving environment variables: {e}{Style.RESET_ALL}")
        return False

def set_variable(name, value):
    """Set an environment variable"""
    variables = load_env_variables()
    variables[name] = value
    if save_env_variables(variables):
        print(f"{SUCCESS}Variable '{name}' set to '{value}'.{Style.RESET_ALL}")
    else:
        print(f"{ERROR}Failed to set variable '{name}'.{Style.RESET_ALL}")

def get_variable(name):
    """Get the value of an environment variable"""
    variables = load_env_variables()
    if name in variables:
        print(f"{INFO}{name}{Style.RESET_ALL}={DESCRIPTION}{variables[name]}")
        return variables[name]
    else:
        print(f"{ERROR}Variable '{name}' not found.{Style.RESET_ALL}")
        return None

def delete_variable(name):
    """Delete an environment variable"""
    variables = load_env_variables()
    if name in variables:
        del variables[name]
        if save_env_variables(variables):
            print(f"{SUCCESS}Variable '{name}' deleted.{Style.RESET_ALL}")
        else:
            print(f"{ERROR}Failed to delete variable '{name}'.{Style.RESET_ALL}")
    else:
        print(f"{ERROR}Variable '{name}' not found.{Style.RESET_ALL}")

def list_variables():
    """List all environment variables"""
    variables = load_env_variables()
    if variables:
        print(f"\n{HEADER}Environment Variables:{Style.RESET_ALL}")
        for name, value in variables.items():
            print(f"{INFO}{name}{Style.RESET_ALL}={DESCRIPTION}{value}")
    else:
        print(f"{WARNING}No environment variables found.{Style.RESET_ALL}")

def show_help():
    """Show help information for env commands"""
    print(f"\n{HEADER}Environment Variable Management:{Style.RESET_ALL}")
    print(f"{COMMAND}  sigma.env list{DESCRIPTION} - List all variables")
    print(f"{COMMAND}  sigma.env get <name>{DESCRIPTION} - Get variable value")
    print(f"{COMMAND}  sigma.env set <name> <value>{DESCRIPTION} - Set variable value")
    print(f"{COMMAND}  sigma.env delete <name>{DESCRIPTION} - Delete variable")
    print()

def main():
    """Main entry point for the env module"""
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        show_help()
        list_variables()
        return
    
    command = args[0].lower()
    
    if command == "list":
        list_variables()
    elif command == "get" and len(args) == 2:
        get_variable(args[1])
    elif command == "set" and len(args) >= 3:
        set_variable(args[1], " ".join(args[2:]))
    elif command == "delete" and len(args) == 2:
        delete_variable(args[1])
    else:
        show_help()

if __name__ == "__main__":
    main() 