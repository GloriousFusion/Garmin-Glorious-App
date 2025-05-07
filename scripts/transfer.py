from scripts.settings import MUSIC_DEFAULT, TEMP_DIRECTORY, BUFFER_TIME, CACHE_DIRECTORY

from pymtp.models import LIBMTP_Track
from pymtp.errors import CommandFailed

from pathlib import Path

import os
import time

def create_folder_tree(root_folder):
    folder_metadata = {}
    folder_tree = {}

    def walk(folder):
        folder_metadata[folder.folder_id] = folder
        folder_tree[folder.folder_id] = []

        child_pointer = folder.child
        while bool(child_pointer):
            child = child_pointer.contents
            folder_tree[folder.folder_id].append(child.folder_id)
            walk(child)
            child_pointer = child.sibling

    walk(root_folder)
    return folder_tree, folder_metadata

def print_folder_tree(device, default=MUSIC_DEFAULT):
    folders = device.get_parent_folders()
    print("\n[ Directories ]")
    for root in folders:
        if root.name.decode() == default:
            folder_tree, folder_metadata = create_folder_tree(root)
            def print_tree(folder_id, indent=""):
                folder = folder_metadata[folder_id]
                print(f"{indent}- {folder.name.decode()}")
                for child_id in folder_tree.get(folder_id, []):
                    print_tree(child_id, indent + "     ")
            print_tree(root.folder_id)
            return
    print(f"Folder '{default}' not found (change in settings).")

def get_folder_id(device, path):
    folders = device.get_parent_folders()

    for root in folders:
        if root.name.decode() == path[0]:
            folder_tree, folder_metadata = create_folder_tree(root)
            current_id = root.folder_id
            break
    else:
        return None

    for part in path[1:]:
        found = False
        for child_id in folder_tree.get(current_id, []):
            child = folder_metadata[child_id]
            if child.name.decode() == part:
                current_id = child.folder_id
                found = True
                break
        if not found:
            return None

    return current_id

def get_file_from_folder(device, folder_id):
    files = device.get_filelisting()
    folder_files = [f for f in files if f.parent_id == folder_id]
    return folder_files

def create_folder_new(device, parent, folder):
    folder_id = device.create_folder(folder.encode(), parent, 0)
    return folder_id

def sync_playlists(device):
    print("\n [ Syncing Playlists ] \n")
    music_folder_id = get_folder_id(device, [MUSIC_DEFAULT])
    if music_folder_id is None:
        music_folder_id = create_folder_new(device, 0, MUSIC_DEFAULT)
    music_files = get_file_from_folder(device, music_folder_id)
    for file in music_files:
        if file.filename.decode().endswith(".m3u8"):
            target_path = str(Path(CACHE_DIRECTORY) / file.filename.decode())
            print(f" [ Synced Playlist: {file.filename.decode()} ]")
            device.get_file_to_file(file.item_id, target_path.encode("utf-8"))
        else:
            print("No Playlists Found.")

def transfer_playlist(device, genre_name, playlist_name, playlist_file, ui, restart_callback, disconnect_callback):
    music_folder_id = get_folder_id(device, [MUSIC_DEFAULT])
    if music_folder_id is None:
        music_folder_id = create_folder_new(device, 0, MUSIC_DEFAULT)

    genre_folder_id = get_folder_id(device, [MUSIC_DEFAULT, genre_name])
    if genre_folder_id is None:
        genre_folder_id = create_folder_new(device, music_folder_id, genre_name)
        print(genre_folder_id)

    playlist_folder_id = get_folder_id(device, [MUSIC_DEFAULT, genre_name, playlist_name])
    if playlist_folder_id is None:
        playlist_folder_id = create_folder_new(device, genre_folder_id, playlist_name)
        print(playlist_folder_id)

    for i, music_file in enumerate(sorted(os.listdir(TEMP_DIRECTORY))):
        music_file_path = os.path.join(TEMP_DIRECTORY, music_file)

        metadata = LIBMTP_Track()
        metadata.filename = music_file.encode()
        metadata.title = os.path.splitext(music_file)[0].encode()
        metadata.album = playlist_name.encode()
        metadata.genre_name = genre_name.encode()
        metadata.parent_id = playlist_folder_id

        try:
            print(f"[ Transferred Track: {music_file} ]")
            device.send_track_from_file(source=music_file_path, target=music_file.encode(), metadata=metadata)
            time.sleep(BUFFER_TIME)
        except CommandFailed:
            print(f"[ Failed To Transfer {music_file} ]")

    playlist_filename = os.path.basename(playlist_file)
    print(f"[ Transferred Playlist: {playlist_filename} ]")
    time.sleep(BUFFER_TIME)
    device.send_file_from_file(source=playlist_file, target=playlist_filename, parent_id=music_folder_id)

    print("[ Transfer Completed. ]")

    def on_repeat_input(response):
        if response.strip().lower() == "y":
            restart_callback()
        else:
            disconnect_callback()

    ui.get_input("- Transfer Another Playlist? (y/N)", on_repeat_input)