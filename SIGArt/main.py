import os
from PIL import Image
import json
import argparse

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_banner():
    clear_screen()
    print("""
    ╔════════════════════════════════╗
    ║      ASCII Art Generator       ║
    ╚════════════════════════════════╝
    """)

def image_to_ascii(image_path, width=100):
    chars = "@%#*+=-:. "
    try:
        img = Image.open(image_path)
        aspect_ratio = img.height / img.width
        new_height = int(aspect_ratio * width * 0.55)
        img = img.resize((width, new_height))
        img = img.convert('L')

        ascii_art = ""
        for pixel_value in img.getdata():
            # Ensure pixel_value is within the range of chars
            ascii_art += chars[min(pixel_value // 25, len(chars) - 1)]
        ascii_art = '\n'.join([ascii_art[i:i+width] for i in range(0, len(ascii_art), width)])
        return ascii_art
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_ascii_art(ascii_art, original_image_name):
    filename = input("Enter filename for the ASCII art (without extension): ")
    filename = f"{filename}.siga"
    save_path = os.path.join(os.path.dirname(__file__), "..", "..", "documents", filename)

    data = {
        "original_image": original_image_name,
        "ascii_art": ascii_art
    }

    with open(save_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"ASCII art saved to documents/{filename}")

def view_siga_file(file_path):
    try:
        full_path = os.path.join(os.path.dirname(__file__), "..", "..", "documents", file_path)
        with open(full_path, 'r') as file:
            data = json.load(file)
            print(f"Original Image: {data['original_image']}")
            print("\nASCII Art:\n")
            print(data['ascii_art'])
    except Exception as e:
        print(f"Error reading .siga file: {e}")

def setup_parser():
    parser = argparse.ArgumentParser(
        description="SIGArt - Convert PNG to ASCII art and manage .siga files.", 
        prefix_chars='?', 
        add_help=False,
        usage=argparse.SUPPRESS  # Suppress the default usage message
    )
    parser.add_argument("?h", "?help", action="help", help="show this help message and exit")
    parser.add_argument("?image", help="Path to the .png image to convert.")
    parser.add_argument("?view", help="Path to the .siga file to view.")
    parser.add_argument("?width", type=int, default=100, help="Width of the ASCII art (default: 100).")
    return parser

def main():
    parser = setup_parser()
    args = parser.parse_args()

    if args.view:
        view_siga_file(args.view)
        return

    if args.image:
        image_path = os.path.join(os.path.dirname(__file__), "..", "..", "documents", args.image)
        if not os.path.exists(image_path):
            print("Image file not found!")
            return

        ascii_art = image_to_ascii(image_path, args.width)
        if ascii_art:
            print("\nGenerated ASCII Art:\n")
            print(ascii_art)

            save_option = input("\nDo you want to save the ASCII art? [y/N]: ").lower()
            if save_option == 'y':
                save_ascii_art(ascii_art, args.image)
        return

    print("No valid arguments provided. Use ?help for usage information.")

if __name__ == "__main__":
    main()