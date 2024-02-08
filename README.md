# pyqrcodegenerator
This is my simple Python QR-code generator that adds text given from text file to QR-code. Done with Python3

## Libs used
This Python program uses following libs:
* segno for QR-code generation
* sys to get commandline parameters
* Image, ImageDrwa and ImageFont from PIL lib to draw text to QR-code
* Glob and os for folder manipulation

## How to
First install needed libs and then create a text file with file names and text to add to QR-code. Running is as simple as: python3 make_qr.py sometextfile.txt optional_font_file<.ttf/ttc>

## File structure
Text file that include what this app generates must have line structure as follows:
name-to-be-included-under-qr-code, link-or-what-ever-this-qr-code-has-as-data, scale-as-integer

### About sizes
Size is not basically in inches or what ever it is the scale of qr-code. I usually use 4 to 12. But one can try different thing. Plus app calculates the place for text based on the scale.





