from kivy.utils import get_color_from_hex
from pathlib import Path

import json

#   Requirements (Directories)
REQUIRED_DIRECTORIES = ["temp", "cache"]

for directory in REQUIRED_DIRECTORIES:
    Path(directory).mkdir(parents=True, exist_ok=True)

#   App (Options)
OPTIONS_PATH = "./data/options.json"

with open(OPTIONS_PATH, "r") as file:
    OPTIONS = json.load(file)

ENV_KDE = OPTIONS.get("ENV_KDE")
AUTO_SYNC = OPTIONS.get("AUTO_SYNC")
GENRE_DEFAULT = OPTIONS.get("GENRE_DEFAULT")
SOURCE_DEFAULT = OPTIONS.get("SOURCE_DEFAULT")

#   Connection (Retry Time)
RETRY_TIME = 3

#   Transfer (Directories + Buffer Time)
MUSIC_DEFAULT = "Music"
PLAYLIST_DEFAULT = GENRE_DEFAULT + str(1)
BUFFER_TIME = 1

#   Audio (Directories)
TEMP_DIRECTORY = "temp"
CACHE_DIRECTORY = "cache"

#   Customization (Dimensions + Color)
DESKTOP = True
WINDOW_HEIGHT = "360" if DESKTOP else "640"
WINDOW_WIDTH = "640" if DESKTOP else "360"
BACKGROUND_COLOR = 	get_color_from_hex("#333333")
TEXT_COLOR = get_color_from_hex("#00aaff")
CURSOR_COLOR = get_color_from_hex("#00aaff")
HINT_COLOR = get_color_from_hex("#f8f8ff")