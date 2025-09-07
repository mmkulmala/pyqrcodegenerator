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

### About sizes of qr-codes
Scale is not the size it is the scale of qr-code. I usually use 4 to 12. But one can try different thing. Notice that the app calculates the place for text based on the scale.

## Linting and testing
To run local pylint, just type:
```bash
./lint.sh
```

To run tests:
```bash
python3 -m pip install -r requirements.txt pytest
pytest -q --disable-warnings --maxfail=1
```

## Using FastAPI and web
Demo for using FastAPI is included. See below.

### How to run:
*  Create/activate venv and install deps:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
*  Start the server:
```bash
uvicorn app:app --reload
```
*  Open docs: http://127.0.0.1:8000/docs

### Example usage:
*  Generate from text (via curl):
```bash
curl -X POST http://127.0.0.1:8000/qrcodes/generate -F 'text=One, https://example.com, 4\nTwo, data-two'
```
*  Generate from a file:
```bash
curl -X POST http://127.0.0.1:8000/qrcodes/generate -F input_file=@example.of.qr-codes
```
*  With a custom font upload:
```bash
curl -X POST http://127.0.0.1:8000/qrcodes/generate -F input_file=@example.of.qr-codes -F font_file=@YourFont.ttf
```
*  List results:
```bash
curl http://127.0.0.1:8000/qrcodes/list
```
*  Fetch an image:
```bash
curl http://127.0.0.1:8000/qrcodes/One.png
```

### FastAPI Notes:
*  If you don’t provide a font, make_qrcodes.py defaults to AmericanTypewriter.ttc. If that font isn’t available on the host, uploads via font_file are recommended.
*  Each generation run clears the qrcodes directory (per current make_qrcodes behavior). If you need to keep previous images or support concurrent generations without clearing, we can adjust behavior in a follow-up.
