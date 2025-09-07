# pyqrcodegenerator
This is my simple Python QR-code generator that adds text given from text file to QR-code. Done with Python3

## Libs used
This Python program uses following libs:
* segno for QR-code generation
* sys to get commandline parameters
* Image, ImageDrwa and ImageFont from PIL lib to draw text to QR-code
* Glob and os for folder manipulation

## How to use
First thing is to have a venv and install reqs:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Running is as simple as: python3 make_qrcodes.py sometextfile.txt optional_font_file<.ttf/ttc>

## File structure for qr-code processing
Text file that include what this app generates must have line structure as follows:
name-to-be-included-under-qr-code, link-or-what-ever-this-qr-code-has-as-data, scale-as-integer

See example.of.qr-codes for little more.

## Linting
To run local pylint, just type:
```bash
./lint.sh
```

### About sizes
Scale is not the size it is the scale of qr-code. I usually use 4 to 12. But one can try different thing. Notice that the app calculates the place for text based on the scale.
