from scripts.settings import TEMP_DIRECTORY, CACHE_DIRECTORY

import os.path
import re
from shutil import rmtree

def remove_special(file):
    name, ext = os.path.splitext(file)
    output = re.sub(r'[^A-Za-z0-9 -]', '', name)
    return output.strip() + ext

def rename_temp():
    for file in os.listdir(TEMP_DIRECTORY):
        original_path = os.path.join(TEMP_DIRECTORY, file)
        if not os.path.isfile(original_path):
            continue

        modified_name = remove_special(file)
        modified_path = os.path.join(TEMP_DIRECTORY, modified_name)

        if file != modified_name:
            os.rename(original_path, modified_path)

def clean_temp():
    for file in os.listdir(TEMP_DIRECTORY):
        path = os.path.join(TEMP_DIRECTORY, file)
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                rmtree(path)
        except Exception as e:
            print(f"Failed to delete {path}: {e}")

def create_playlist(name):
    playlist_data = ["#EXTM3U"]

    for track in os.listdir(TEMP_DIRECTORY):
        playlist_data.append(f"#EXTINF:0,{track}")
        playlist_data.append(f"..\\{name}\\{track}")

    playlist_file = os.path.join(CACHE_DIRECTORY, f"{name}.m3u8".lower())
    with open (playlist_file, "w", encoding="utf-8") as file:
        file.write("\n".join(playlist_data))
        print("Playlist Completed!")

    return playlist_file

def edit_playlist(name, path):
    with open(path, "r", encoding="utf-8") as file:
        playlist_data = file.read().splitlines()

    tracks = set()
    for line in playlist_data:
        if line.startswith("..\\"):
            track = line.split("\\")[-1].strip().lower()
            tracks.add(track)

    new_data = []
    for track in os.listdir(TEMP_DIRECTORY):
        if not os.path.isfile(os.path.join(TEMP_DIRECTORY, track)):
            continue

        track_name = track.strip().lower()
        if track_name not in tracks:
            new_data.append(f"#EXTINF:0,{track}")
            new_data.append(f"..\\{name}\\{track}")

    if new_data:
        with open(path, "a", encoding="utf-8") as file:
            file.write("\n" + "\n".join(new_data))
        print(f"Added {len(new_data)//2} track(s) to {name}")
    else:
        print("Tracks Are Up To Date.")

def find_playlist(name):
    rename_temp()

    playlist_name = f"{name}.m3u8".lower()
    playlist_path = os.path.join(CACHE_DIRECTORY, playlist_name)

    if os.path.isfile(playlist_path):
        print(f"Playlist Found: {playlist_name}")
        edit_playlist(name, playlist_path)
        return playlist_path

    print(f"Playlist Not Found, Creating A New One")
    return create_playlist(name)