"""FastAPI app exposing endpoints to generate and serve QR codes.

This wraps the functions in make_qrcodes.py and provides a simple web API:
- POST /qrcodes/generate: generate QR codes from uploaded text or file
- GET  /qrcodes/list: list generated QR code image URLs
- Static /qrcodes: serve generated PNG images
"""

from __future__ import annotations

import contextlib
import glob
import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile  # pylint: disable=import-error
from fastapi.responses import JSONResponse  # pylint: disable=import-error
from fastapi.staticfiles import StaticFiles  # pylint: disable=import-error

# Ensure project root (where make_qrcodes.py lives) is importable
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Local import after path adjustment
from make_qrcodes import create_qrcodes  # pylint: disable=wrong-import-position

QRCODES_DIR = BASE_DIR / "qrcodes"

app = FastAPI(title="pyqrcodegenerator API", version="1.0.0")

# Serve generated images directly under /qrcodes
app.mount("/qrcodes", StaticFiles(directory=str(QRCODES_DIR), html=False), name="qrcodes")


@contextlib.contextmanager
def _chdir(path: Path):
    """Temporarily change the current working directory.

    make_qrcodes.py uses relative paths (./qrcodes), so we ensure cwd is project root
    when invoking it from the web layer.
    """
    original = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(original)


def _write_text_to_tempfile(text: str, dir_path: Path) -> Path:
    """Persist provided text to a temporary file and return its path."""
    dir_path.mkdir(parents=True, exist_ok=True)
    # Use a predictable but unique filename

    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, dir=dir_path) as tmp:
        tmp.write(text)
        return Path(tmp.name)


def _write_upload_to_tempfile(upload: UploadFile, dir_path: Path, suffix: str = "") -> Path:
    """Persist an uploaded file to a temporary path and return it."""
    dir_path.mkdir(parents=True, exist_ok=True)

    with tempfile.NamedTemporaryFile("wb", suffix=suffix, delete=False, dir=dir_path) as tmp:
        # Avoid reading the entire file into memory if large
        upload.file.seek(0)
        shutil.copyfileobj(upload.file, tmp)
        return Path(tmp.name)


@app.get("/health")
async def health() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root() -> dict:
    """API entry point with brief help."""
    return {
        "name": "pyqrcodegenerator API",
        "docs": "/docs",
        "endpoints": {
            "generate": {"method": "POST", "path": "/qrcodes/generate"},
            "list": {"method": "GET", "path": "/qrcodes/list"},
            "static": {"method": "GET", "path": "/qrcodes/{image}.png"},
        },
    }


@app.get("/qrcodes/list")
async def list_qrcodes() -> JSONResponse:
    """List available PNG images in the qrcodes directory."""
    files = [f"/qrcodes/{Path(p).name}" for p in sorted(glob.glob(str(QRCODES_DIR / "*.png")))]
    return JSONResponse({"count": len(files), "files": files})


@app.post("/qrcodes/generate")
async def generate_qrcodes(
    # Provide either 'text' or 'input_file'
    input_file: Optional[UploadFile] = File(
        None,
        description="Text file with lines: name, data, [scale]",
    ),
    text: Optional[str] = Form(None, description="Raw text containing lines: name, data, [scale]"),
    # Optional font: upload a .ttf/.ttc or pass a filesystem path available on server
    font_file: Optional[UploadFile] = File(
        None,
        description="Font file (.ttf/.ttc) to render captions",
    ),
    font_file_name: Optional[str] = Form(None, description="Server-side font file path"),
) -> JSONResponse:
    """Generate QR codes using the same logic as the CLI.

    One of 'text' or 'input_file' must be provided. Optionally, a font can be supplied
    either via upload or by providing a path known to the server.
    """
    if not text and not input_file:
        raise HTTPException(status_code=400, detail="Provide either 'text' or 'input_file'.")

    # Persist inputs to temporary files under project root to keep relative paths simple
    tmp_dir = BASE_DIR / ".tmp"
    input_path: Optional[Path] = None
    font_path: Optional[Path] = None
    try:
        if text:
            input_path = _write_text_to_tempfile(text, tmp_dir)
        else:
            assert input_file is not None  # for type checker
            # Use text/plain by default; still write as binary
            input_path = _write_upload_to_tempfile(input_file, tmp_dir, suffix=".txt")

        if font_file is not None:
            # Preserve original extension if present
            suffix = Path(font_file.filename or "").suffix or ".ttf"
            font_path = _write_upload_to_tempfile(font_file, tmp_dir, suffix=suffix)

        with _chdir(BASE_DIR):
            if font_path is not None:
                create_qrcodes(str(input_path), font_file_name=str(font_path))
            elif font_file_name:
                create_qrcodes(str(input_path), font_file_name=font_file_name)
            else:
                # Rely on default in make_qrcodes.py (may require that font to be present)
                create_qrcodes(str(input_path))

        # Return list of generated images as URLs
        files = [f"/qrcodes/{Path(p).name}" for p in sorted(glob.glob(str(QRCODES_DIR / "*.png")))]
        return JSONResponse({"count": len(files), "files": files})
    finally:
        # Best-effort cleanup of temporary files
        for p in (input_path, font_path):
            try:
                if p and p.exists():
                    p.unlink(missing_ok=True)
            except OSError:
                # Non-fatal cleanup failure
                pass
