from scripts.settings import TEMP_DIRECTORY, SOURCE_DEFAULT, GENRE_DEFAULT, PLAYLIST_DEFAULT

import yt_dlp

from pathlib import Path
from shutil import copy2

from plyer import filechooser
from kivy.clock import Clock

### https://yt-dlp.memoryview.in/docs/embedding-yt-dlp/using-yt-dlp-in-python-scripts#customizing-options ###
def install_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': f'{TEMP_DIRECTORY}/%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def get_audio(ui, input_callback, source_type):
    def on_repeat_input(response):
        if response.strip().lower() == "y":
            get_audio(ui, input_callback, source_type)
        else:
            input_callback()

    if source_type == "url":
        def on_url_input(url):
            if url:
                print("\nInstalling...")
                def do_install(dt):
                    try:
                        install_audio(url)
                    except Exception as e:
                        print(f"\n[ URL is not supported ]\n[ Due to: {e} ]\n")
                    ui.get_input("- Get More Audio? (y/N)", on_repeat_input)
                Clock.schedule_once(do_install, 0.1)
            else:
                print("[ No URL Entered. ]")
                ui.get_input("- Get More Audio? (y/N)", on_repeat_input)
        ui.get_input("- Enter Audio URL (Youtube, Soundcloud etc.)", on_url_input)

    elif source_type == "dir":
        def on_dir_selection(selection):
            if not selection:
                print("[ No Directory Selected. ]")
                input_callback()
                return

            dir_path = Path(selection[0])
            audio_files = list(dir_path.glob("*.mp3"))

            if not audio_files:
                print(f"[ No Audio Found In {dir_path} (Only .mp3 Supported) ]")
            else:
                for audio_file in audio_files:
                    dest_path = Path(TEMP_DIRECTORY) / audio_file.name
                    copy2(audio_file, dest_path)
                print(f"[ Copied {len(audio_files)} track(s) from {dir_path} ]")

            ui.get_input("- Get More Audio? (y/N)", on_repeat_input)
        filechooser.choose_dir(on_selection=on_dir_selection, title="Select Audio Directory")
    else:
        print("[ Invalid source type (change in settings). ]")

def get_music(ui, input_callback):
    def on_genre_input(genre_input):
        genre = genre_input.strip().capitalize() or GENRE_DEFAULT

        def on_playlist_input(playlist_input):
            playlist = playlist_input.strip().capitalize() or PLAYLIST_DEFAULT

            def on_source_input(source_input):
                source = source_input.strip().lower() or SOURCE_DEFAULT
                get_audio(ui, lambda: input_callback(genre, playlist), source)

            ui.get_input(f"- Enter Source Type (url or dir) [Default = {SOURCE_DEFAULT}]", on_source_input)
        ui.get_input(f"- Enter Playlist Name (Dnb1, Classic3 etc.) [Default = {PLAYLIST_DEFAULT}]", on_playlist_input)
    ui.get_input(f"- Enter Genre Name (Edm, Funk, Chill etc.) [Default = {GENRE_DEFAULT}]", on_genre_input)