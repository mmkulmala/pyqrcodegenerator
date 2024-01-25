import segno
import sys
from PIL import Image, ImageDraw, ImageFont

def create_qrcodes(filename):
    get_qrcode_amount(filename)

    with open(filename) as artist_file:
        n = 1
        for line in artist_file:
            first_part_of_line = line.split(",")[0]
            name_of_file = first_part_of_line + '.png'
            link_to_launch = line.split(",")[1]
            print(">> Generating: " +name_of_file + " that has data: " +link_to_launch)
            qrcode = segno.make_qr(link_to_launch)
            qrcode.save(
                name_of_file,
                scale=8,
                border=5,
                light=None,
            )
            add_caption(name_of_file, first_part_of_line)
            n += 1
 
def get_qrcode_amount(file_name):
    with open(file_name, 'r') as fp:
        x = len(fp.readlines())
        print('####################################################')
        print('# Generating ' + str(x) + ' qr-codes                            #')   
        print('####################################################')

def add_caption(caption_to, caption_what):
    image = Image.open(caption_to)
    width, height = image.size
    draw = ImageDraw.Draw(image)
    text_seat = caption_what
    font = ImageFont.truetype('Chalkduster.ttf', 24)
    draw.text((40,height - 40), text_seat, font=font)
    image.save(caption_to)   

def main():
    if(len(sys.argv) != 2):
        print("Usage: python3 make_qrcodes.py <info-text-file>")
        sys.exit(1)
    create_qrcodes(sys.argv[1])

if __name__ == "__main__":
    main()
