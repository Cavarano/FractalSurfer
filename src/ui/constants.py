"""Constant values used throughout the UI."""

from pathlib import Path

MIN_WIDTH = 1200
MIN_HEIGHT = 800
SIDE_PANEL_WIDTH = 400
TAB_BAR_TAG = "tab_bar"

SCREENSHOT_FOLDER = Path("./screenshots/")
ANIMATIONS_FOLDER = Path("./animations/")
GIF_FOLDER = ANIMATIONS_FOLDER / "gif"
MP4_FOLDER = ANIMATIONS_FOLDER / "mp4"
WEBM_FOLDER = ANIMATIONS_FOLDER / "webm"

SCREENSHOT_FOLDER.mkdir(exist_ok=True)
ANIMATIONS_FOLDER.mkdir(exist_ok=True)
GIF_FOLDER.mkdir(exist_ok=True)
MP4_FOLDER.mkdir(exist_ok=True)
WEBM_FOLDER.mkdir(exist_ok=True)
