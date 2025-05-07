import os
import requests
import sys
from colorama import init, Fore, Style
from SigmaOS_core import loading_animation, press_enter_to_continue, clear_screen

# ensure Colorama works on all terminals
init(autoreset=True)

def download_task(url: str, dest_path: str):
    resp = requests.get(url, stream=True)
    resp.raise_for_status()
    total = int(resp.headers.get('content-length', 0))
    chunk_size = 8192
    downloaded = 0

    with open(dest_path, 'wb') as f:
        for chunk in resp.iter_content(chunk_size):
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)

    return f"{Fore.GREEN}Saved to{Style.RESET_ALL} documents"

def main():
    clear_screen()
    # 1) prompt for URL
    print(f"{Fore.CYAN}=== Sucker Downloader ==={Style.RESET_ALL}")
    url = input("Enter URL to download: ").strip()
    if not url:
        print(f"{Fore.RED}No URL entered, exiting.{Style.RESET_ALL}")
        press_enter_to_continue()
        return

    # 2) compute destination
    filename = url.rstrip("/").split("/")[-1] or "downloaded.file"
    base = os.path.dirname(__file__)
    docs = os.path.abspath(os.path.join(base, "..", "..", "documents"))
    os.makedirs(docs, exist_ok=True)
    dest = os.path.join(docs, filename)

    # 3) run download under SigmaOS loading_animation
    print()  # space before animation
    try:
        result = loading_animation(f"Downloading {filename}", task=lambda: download_task(url, dest))
        # loading_animation prints its own spinner; result is what download_task returned
        print(result)
    except Exception as e:
        print(f"{Fore.RED}Error during download:{Style.RESET_ALL} {e}")

    if not os.path.exists(os.path.join(base, "..", "doccx")):
        print(f"To view the file, install 'DoccX' with: {Fore.CYAN}ligma install DoccX{Style.RESET_ALL}")

    # 4) wait before SigmaOS clears screen
    press_enter_to_continue()

if __name__ == "__main__":
    main()
