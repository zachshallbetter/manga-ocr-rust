from importlib import reload

from PIL import Image

from manga_ocr import MangaOcr  # noqa: F401
from manga_ocr.ocr import post_process
from manga_ocr.run import are_images_identical
from manga_ocr_dev import env


def test_post_process_whitespace():
    assert post_process("  素直 に  あやまる しか ") == "素直にあやまるしか"


def test_post_process_ellipsis():
    # post_process replaces '…' with '...' and then jaconv.h2z converts '.' to full-width '．'
    assert post_process("…") == "．．．"
    assert post_process("・・") == "．．"
    assert post_process("...") == "．．．"


def test_post_process_fullwidth_conversion():
    # half-width ASCII letters and numbers converted to full-width
    assert post_process("abc 123") == "ａｂｃ１２３"
    assert post_process("LINK") == "ＬＩＮＫ"


def test_are_images_identical():
    img1 = Image.new("RGB", (10, 10), color="red")
    img2 = Image.new("RGB", (10, 10), color="red")
    img3 = Image.new("RGB", (10, 10), color="blue")
    img4 = Image.new("RGB", (12, 12), color="red")

    assert are_images_identical(img1, img2) is True
    assert are_images_identical(img1, img3) is False
    assert are_images_identical(img1, img4) is False
    assert are_images_identical(None, None) is True
    assert are_images_identical(img1, None) is False


def test_env_overrides(monkeypatch, tmp_path):
    custom_fonts = tmp_path / "custom_fonts"
    monkeypatch.setenv("FONTS_ROOT", str(custom_fonts))

    reload(env)
    assert env.FONTS_ROOT == custom_fonts
