"""2.B 1.5.0 and 3.A 1.4.0: an image's type is read from its first bytes
before its size matters, and a redirect inside the recording is followed.
Pure tests on bytes and a hand-made recording; no browser."""

from __future__ import annotations

import io
import json
import zipfile

from PIL import Image

from tobi508.capture import media_body
from tobi508.motion import _can_animate


def _png(frames: int) -> bytes:
    out = io.BytesIO()
    imgs = [Image.new("RGB", (4, 4), (40 * i, 0, 0)) for i in range(frames)]
    if frames > 1:
        imgs[0].save(out, "PNG", save_all=True, append_images=imgs[1:], duration=100)
    else:
        imgs[0].save(out, "PNG")
    return out.getvalue()


def _webp(frames: int) -> bytes:
    out = io.BytesIO()
    imgs = [Image.new("RGB", (4, 4), (40 * i, 0, 0)) for i in range(frames)]
    if frames > 1:
        imgs[0].save(out, "WEBP", save_all=True, append_images=imgs[1:], duration=100)
    else:
        imgs[0].save(out, "WEBP")
    return out.getvalue()


def _jpeg() -> bytes:
    out = io.BytesIO()
    Image.new("RGB", (4, 4)).save(out, "JPEG")
    return out.getvalue()


def test_a_still_png_webp_or_jpeg_is_done_from_its_first_bytes():
    assert _can_animate(_png(1)) is None
    assert _can_animate(_webp(1)) is None
    assert _can_animate(_jpeg()) is None
    assert _can_animate(b"<svg xmlns='http://www.w3.org/2000/svg'/>") is None


def test_an_animated_png_webp_or_any_gif_is_decoded():
    assert _can_animate(_png(3)) == "image/png"
    assert _can_animate(_webp(3)) == "image/webp"
    gif = io.BytesIO()
    Image.new("RGB", (4, 4)).save(gif, "GIF")
    assert _can_animate(gif.getvalue()) == "image/gif"


def test_a_png_that_cannot_be_walked_is_decoded():
    assert _can_animate(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x05junk") == "image/png"


def _har(tmp_path, entries: list[dict], files: dict[str, bytes]):
    path = tmp_path / "page.har.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("har.har", json.dumps({"log": {"entries": entries}}))
        for name, body in files.items():
            z.writestr(name, body)
    return path


def _entry(url: str, status: int, file: str = "", location: str = "") -> dict:
    headers = [{"name": "Location", "value": location}] if location else []
    content = {"_file": file} if file else {}
    return {
        "request": {"url": url},
        "response": {"status": status, "headers": headers, "content": content},
    }


def test_a_redirect_inside_the_recording_is_followed(tmp_path):
    har = _har(
        tmp_path,
        [
            _entry("https://a.example/avatar", 302, location="/img/1.png"),
            _entry("https://a.example/img/1.png", 200, file="b1.png"),
        ],
        {"b1.png": b"PNGBYTES"},
    )
    assert media_body(har, "https://a.example/avatar") == b"PNGBYTES"


def test_a_redirect_loop_or_a_missing_target_reads_nothing(tmp_path):
    har = _har(
        tmp_path,
        [
            _entry("https://a.example/x", 302, location="https://a.example/y"),
            _entry("https://a.example/y", 302, location="https://a.example/x"),
            _entry("https://a.example/z", 302, location="https://a.example/gone"),
        ],
        {},
    )
    assert media_body(har, "https://a.example/x") is None
    assert media_body(har, "https://a.example/z") is None
