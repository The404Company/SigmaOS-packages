import os
import sys
import requests
import json
from colorama import Fore, Style, init

init(autoreset=True)

# OpenRouter API settings
API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api.key")
MODEL = "mistralai/mistral-7b-instruct:free" 
SYSTEM_PROMPT_FILE = "XiAI.txt"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def show_banner():
    clear_screen()
    print(f"{Fore.CYAN}XiAI Online{Style.RESET_ALL}")

def load_api_key():
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, 'r') as f:
                return f.read().strip()
        else:
            print(f"{Fore.YELLOW}OpenRouter API key not found.{Style.RESET_ALL}")
            print(f"{Fore.CYAN}This API key will only be stored locally in '{API_KEY_FILE}' and costs nothing to use.{Style.RESET_ALL}")
            api_key = input(f"{Fore.WHITE}Please enter your OpenRouter API key: {Style.RESET_ALL}")
            
            try:
                with open(API_KEY_FILE, 'w') as f:
                    f.write(api_key)
                print(f"{Fore.GREEN}API key saved successfully!{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.YELLOW}Could not save API key to file: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Will use provided key for this session only.{Style.RESET_ALL}")
            
            return api_key
    except Exception as e:
        print(f"{Fore.YELLOW}Error accessing API key file: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Please enter your OpenRouter API key for this session:{Style.RESET_ALL}")
        return input(f"{Fore.WHITE}API key: {Style.RESET_ALL}")

def load_system_prompt():
    if not os.path.exists(SYSTEM_PROMPT_FILE):
        print(f"{Fore.RED}Missing system prompt file: {SYSTEM_PROMPT_FILE}{Style.RESET_ALL}")
        sys.exit(1)
    with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def chat():
    try:
        api_key = load_api_key()
        system_prompt = load_system_prompt()
        messages = [{"role": "system", "content": system_prompt}]  # Initialize messages
        
        print(f"\n{Fore.YELLOW}XiAI is ready! Ask a question or type 'exit'.{Style.RESET_ALL}")
        
        while True:
            try:
                user_input = input(f"{Fore.WHITE}\nYou: {Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}XiAI: Session ended by user.{Style.RESET_ALL}")
                break

            if user_input.lower() in ['exit', 'quit']:
                print(f"{Fore.CYAN}XiAI: See you next time!{Style.RESET_ALL}")
                break

            messages.append({"role": "user", "content": user_input})
            
            # Trim messages to keep context reasonable
            if len(messages) > 10:
                messages = [messages[0]] + messages[-9:]
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
                "X-Title": "SigmaOS", # Optional. Site title for rankings on openrouter.ai.
                "HTTP-Referer": "https://the404company.github.io/SigmaOS.html", # Optional. Site URL for rankings on openrouter.ai.
            }
            data = {
                "model": MODEL,
                "messages": messages,
                "stream": True
            }
            
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", 
                                    headers=headers, json=data, stream=True)
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}XiAI:{Style.RESET_ALL} ", end="", flush=True)
                response_text = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8').replace("data: ", ""))
                            content = chunk['choices'][0]['delta'].get('content', '')
                            print(content, end='', flush=True)
                            response_text += content
                        except json.JSONDecodeError:
                            continue
                print()  # Newline after response
                messages.append({"role": "assistant", "content": response_text})
            else:
                print(f"{Fore.RED}\nError: {response.status_code}{Style.RESET_ALL}")
                print(response.text)

    except Exception as e:
        print(f"{Fore.RED}Error during chat: {e}{Style.RESET_ALL}")

def main():
    show_banner()
    chat()

if __name__ == "__main__":
    main()