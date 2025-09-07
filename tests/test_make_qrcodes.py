import os
import sys
import glob

import pytest
from PIL import Image, ImageFont, ImageDraw

# Ensure project root is on sys.path so 'make_qrcodes.py' can be imported
CURRENT_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import functions under test
from make_qrcodes import (
    add_caption,
    clear_folder,
    create_folder_if_not_exists,
    create_qrcodes,
    get_qrcode_amount,
    main,
)


@pytest.fixture(autouse=True)
def patch_truetype(monkeypatch):
    """Patch PIL's truetype loader to avoid dependency on system font files.

    This ensures tests don't require a real .ttf/.ttc file and remain portable,
    and avoids recursion by preloading a default font before patching.
    Also patch ImageDraw.text to default to black fill when none is provided.
    """
    # 1) Preload a default font and patch truetype to return it
    default_font = ImageFont.load_default()
    monkeypatch.setattr(
        "PIL.ImageFont.truetype", lambda *args, **kwargs: default_font, raising=True
    )

    # 2) Patch ImageDraw.ImageDraw.text to ensure a visible default fill
    original_text = ImageDraw.ImageDraw.text

    def text_with_default_fill(self, xy, text, fill=None, *args, **kwargs):
        if fill is None:
            mode = getattr(self, "mode", None)
            if mode == "RGBA":
                fill = (0, 0, 0, 255)
            elif mode == "RGB":
                fill = (0, 0, 0)
            elif mode in ("L", "P", "1"):
                fill = 0
            elif mode == "LA":
                fill = (0, 255)
            else:
                # Fallback to black as an int; PIL will try to map appropriately
                fill = 0
        return original_text(self, xy, text, fill=fill, *args, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", text_with_default_fill, raising=True)


@pytest.fixture
def temp_cwd(tmp_path, monkeypatch):
    """Run each test in a temporary working directory to isolate file I/O."""
    monkeypatch.chdir(tmp_path)
    return tmp_path


def test_create_and_clear_folder(temp_cwd):
    # Ensure folder doesn't exist
    assert not os.path.exists("qrcodes")

    # Create it
    create_folder_if_not_exists()
    assert os.path.isdir("qrcodes")

    # Drop a dummy PNG and clear
    img = Image.new("RGB", (10, 10), color=(255, 255, 255))
    sample_path = os.path.join("qrcodes", "sample.png")
    img.save(sample_path)

    assert glob.glob("qrcodes/*.png")

    clear_folder()
    assert not glob.glob("qrcodes/*.png")


def test_add_caption_draws_text(temp_cwd):
    # Create a white image
    img = Image.new("RGB", (200, 100), color=(255, 255, 255))
    path = "base.png"
    img.save(path)

    # Draw caption near the bottom
    add_caption(
        caption_to=path,
        caption_what="HELLO",
        font_file_name="dummy.ttf",  # patched to load default
        font_size=12,
        text_position=12,
    )

    # Verify image has non-white pixels now
    img2 = Image.open(path).convert("RGB")
    pixels = list(img2.getdata())
    assert any(px != (255, 255, 255) for px in pixels)


def test_get_qrcode_amount_prints_count(tmp_path, capsys):
    # Create a file with 3 lines
    fpath = tmp_path / "input.txt"
    fpath.write_text("one,a\nTwo,b\nthree,c\n", encoding="utf-8")

    get_qrcode_amount(str(fpath))
    out = capsys.readouterr().out
    assert "Generating 3 qr-codes" in out


def test_create_qrcodes_creates_images(temp_cwd):
    # Input with and without explicit scale
    input_path = "qr_input.txt"
    contents = """
One, https://example.com, 4
Two, data-two
""".strip()
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(contents)

    # Execute
    create_qrcodes(input_path, font_file_name="dummy.ttf")  # font loader is patched

    # Verify outputs exist and are valid images
    out1 = os.path.join("qrcodes", "One.png")
    out2 = os.path.join("qrcodes", "Two.png")
    for p in (out1, out2):
        assert os.path.exists(p), f"Expected output image missing: {p}"
        # Can be opened by PIL
        Image.open(p).verify()  # verify doesn't load full image, just checks integrity


def test_main_without_args_shows_usage_and_exits(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["make_qrcodes.py"])  # no args
    with pytest.raises(SystemExit) as ex:
        main()
    assert ex.value.code == 1
    out = capsys.readouterr().out
    assert "Usage:" in out
