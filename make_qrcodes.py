"""Generate QR codes from a text file (name,data,optional scale) and overlay caption text."""

import sys
import os
import glob

import segno
from PIL import Image, ImageDraw, ImageFont

def create_qrcodes(filename: str, font_file_name: str = "AmericanTypewriter.ttc") -> None:
    """Create QR codes from lines in ``filename`` and optionally use a custom font.

    The input file should contain CSV-like rows:
        name, data, [scale]

    - name: label to render below the QR code (also used as filename)
    - data: string encoded into the QR code
    - scale: optional integer scale for the QR image (default 4)
    """
    get_qrcode_amount(filename)
    create_folder_if_not_exists()
    clear_folder()

    with open(filename, encoding="utf-8") as artist_file:
        for line in artist_file:
            data_from_line = line.split(",")
            first_part_of_line = data_from_line[0]
            name_of_file = "./qrcodes/" + first_part_of_line + ".png"
            link_to_launch = data_from_line[1]
            font_size: int = 12
            text_position: int = 20
            qr_image_scale: int = 4
            try:
                qr_image_scale = int(data_from_line[2])
                font_size = qr_image_scale * 3
                text_position = int(font_size * 1.67)
                print(
                    f">> Generating with image size: scale {qr_image_scale}, "
                    f"font size {font_size}, text position {text_position}"
                )
            except IndexError:
                print(">> Using defaults: scale 4, font 12, text_pos 20")
            print(f">>> Generating: {name_of_file} -> {link_to_launch}")
            qrcode = segno.make_qr(link_to_launch)
            qrcode.save(
                name_of_file,
                scale=qr_image_scale,
                border=5,
                light=None,
            )
            add_caption(
                name_of_file,
                first_part_of_line,
                font_file_name,
                font_size,
                text_position,
            )

def get_qrcode_amount(file_name: str) -> None:
    """Print how many QR codes will be generated based on the input file lines."""
    with open(file_name, "r", encoding="utf-8") as fp:
        x = len(fp.readlines())
    print("####################################################")
    print(f"# Generating {x} qr-codes                            #")
    print("####################################################")

def clear_folder() -> None:
    """Delete all QR code images in the 'qrcodes' folder."""
    for path in glob.glob("./qrcodes/*.png"):
        os.remove(path)

def create_folder_if_not_exists() -> None:
    """Create the 'qrcodes' folder if it does not already exist."""
    os.makedirs("qrcodes", exist_ok=True)

def add_caption(
    caption_to: str,
    caption_what: str,
    font_file_name: str,
    font_size: int,
    text_position: int,
) -> None:
    """Add a caption to the image using the provided font."""
    image = Image.open(caption_to)
    _, height = image.size
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_file_name, font_size)
    draw.text((text_position, height - text_position), caption_what, font=font)
    image.save(caption_to)

def main() -> None:
    """Parse CLI args and generate QR codes."""
    if len(sys.argv) < 2:
        print("Usage: python3 make_qrcodes.py <artists-text-file> <optional-font-file-name>")
        sys.exit(1)
    elif len(sys.argv) == 2:
        create_qrcodes(sys.argv[1])
    else:
        create_qrcodes(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
