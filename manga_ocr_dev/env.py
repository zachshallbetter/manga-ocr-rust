import os
from pathlib import Path

ASSETS_PATH = Path(__file__).parent.parent / "assets"

FONTS_ROOT = Path(os.getenv("FONTS_ROOT", "~/data/jp_fonts")).expanduser()
DATA_SYNTHETIC_ROOT = Path(os.getenv("DATA_SYNTHETIC_ROOT", "~/data/manga/synthetic")).expanduser()
BACKGROUND_DIR = Path(os.getenv("BACKGROUND_DIR", "~/data/manga/Manga109s/background")).expanduser()
MANGA109_ROOT = Path(os.getenv("MANGA109_ROOT", "~/data/manga/Manga109s")).expanduser()
TRAIN_ROOT = Path(os.getenv("TRAIN_ROOT", "~/data/manga/out")).expanduser()

