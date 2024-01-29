import segno
import sys
from PIL import Image, ImageDraw, ImageFont

"""
Create QR codes from a file with the specified filename and an optional font file name.
"""
def create_qrcodes(filename, fontFileName='AmericanTypewriter.ttc'):
    get_qrcode_amount(filename)

    with open(filename) as artist_file:
        n = 1
        for line in artist_file:
            first_part_of_line = line.split(",")[0]
            name_of_file = first_part_of_line + '.png'
            link_to_launch = line.split(",")[1]
            print(">> Generating: " +name_of_file + " that goes to: " +link_to_launch)
            qrcode = segno.make_qr(link_to_launch)
            qrcode.save(
                name_of_file,
                scale=4,
                border=5,
                light=None,
            )
            add_caption(name_of_file, first_part_of_line, fontFileName)
            n += 1

"""
Calculate the number of qr-codes in the specified file.

Args:
    file_name (str): The name of the file containing the qr-codes.

Returns:
    None
""" 
def get_qrcode_amount(file_name):
    with open(file_name, 'r') as fp:
        x = len(fp.readlines())
        print('####################################################')
        print('# Generating ' + str(x) + ' qr-codes                            #')   
        print('####################################################')

"""
Adds a caption to the specified image using the provided caption and font. 

Args:
    caption_to (str): The path to the image to which the caption should be added.
    caption_what (str): The text of the caption.
    fontFileName (str): The path to the font file to be used for the caption.

Returns:
    None
"""
def add_caption(caption_to, caption_what, fontFileName):
    image = Image.open(caption_to)
    width, height = image.size
    draw = ImageDraw.Draw(image)
    text_seat = caption_what
    font = ImageFont.truetype(fontFileName, 12)
    draw.text((20,height - 20), text_seat, font=font)
    image.save(caption_to)   

"""
This function is the main entry point of the program. It checks the command line arguments
and calls the create_qrcodes function with the appropriate parameters.
"""
def main():
    if(len(sys.argv) < 2):
        print("Usage: python3 make_qrcodes.py <artists-text-file> <optional-font-file-name>")
        sys.exit(1)
    if(len(sys.argv) == 2):
        create_qrcodes(sys.argv[1])
    if(len(sys.argv) == 3):
        create_qrcodes(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
