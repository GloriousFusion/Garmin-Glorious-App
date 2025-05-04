from kivy.utils import get_color_from_hex
from pathlib import Path

#   Requirements (Directories)
REQUIRED_DIRECTORIES = ["temp", "cache"]

for directory in REQUIRED_DIRECTORIES:
    print("directories......")
    Path(directory).mkdir(parents=True, exist_ok=True)

#   Connection (Environment + Retry Time)
ENV_KDE = True
RETRY_TIME = 3

#   Transfer (Directories + Buffer Time)
MUSIC_DEFAULT = "Music"
GENRE_DEFAULT = "Mix"
PLAYLIST_DEFAULT = GENRE_DEFAULT + str(1)
BUFFER_TIME = 1

#   Audio (Directories)
SOURCE_DEFAULT = "url"
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
