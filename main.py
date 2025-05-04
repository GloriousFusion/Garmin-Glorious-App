from scripts.settings import BACKGROUND_COLOR, TEXT_COLOR, CURSOR_COLOR, HINT_COLOR
from scripts.settings import WINDOW_WIDTH, WINDOW_HEIGHT

from scripts.connection import connect
from scripts.transfer import print_folder_tree, transfer_playlist
from scripts.audio import get_music
from scripts.mods import find_playlist, clean_temp

from kivy.config import Config
Config.set("graphics", "width", WINDOW_WIDTH)
Config.set("graphics", "height", WINDOW_HEIGHT)
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

from kivy.core.window import Window
from kivy.core.text import LabelBase
LabelBase.register(name="orbitron_regular", fn_regular="fonts/orbitron_regular.ttf")

import sys
import threading

class ConsoleOutput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.readonly = True
        self.font_size = 12

    def write(self, message):
        Clock.schedule_once(lambda dt: self._append_text(message))

    def _append_text(self, message):
        self.text += message
        self.cursor = (0, len(self.text.splitlines()))

    def flush(self):
        pass

class AppUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        Window.clearcolor = BACKGROUND_COLOR

        self.console = ConsoleOutput(readonly=True,
                                     size_hint=(1, 0.8),
                                     font_name="orbitron_regular",
                                     foreground_color=TEXT_COLOR,
                                     cursor_color=CURSOR_COLOR,
                                     background_color=BACKGROUND_COLOR)
        self.add_widget(self.console)

        self.button = Button(text="Connect",
                             size_hint=(1, 0.1),
                             font_name="orbitron_regular",
                             color=TEXT_COLOR,
                             background_color=BACKGROUND_COLOR,
                             background_normal=""
                             )
        self.button.bind(on_press=self.on_connect)
        self.add_widget(self.button)

        self.input_field = TextInput(hint_text="Input...",
                                     size_hint=(1, 0.1),
                                     font_name="orbitron_regular",
                                     foreground_color=TEXT_COLOR,
                                     cursor_color=CURSOR_COLOR,
                                     hint_text_color=HINT_COLOR,
                                     background_color=BACKGROUND_COLOR,
                                     multiline=False)
        self.input_field.bind(on_text_validate=self.on_enter)
        self.add_widget(self.input_field)

        sys.stdout = self.console
        sys.stderr = self.console

        self.input_callback = None
        self.device = None

    def on_connect(self, *args):
        clean_temp()
        if self.button.text == "Connected (Press To Disconnect)" and self.device:
            self.on_disconnect()
            return
        self.button.disabled = True
        threading.Thread(target=self.music_thread).start()

    def on_disconnect(self):
        self.device.disconnect()
        self.device = None
        self.console.text = ""
        print("Disconnected.")
        self.button.text = "Connect"

    def get_input(self, prompt, callback):
        print(prompt)
        self.input_field.text = ""
        self.input_callback = callback
        self.input_field.focus = True

    def on_enter(self, instance):
        if self.input_callback:
            self.input_callback(self.input_field.text)
            self.input_field.text = ""
        Clock.schedule_once(lambda dt: setattr(self.input_field, "focus", True), 0)

    def update_status(self, text):
        Clock.schedule_once(lambda dt: setattr(self.button, "text", text))
        if text == "Connected (Press To Disconnect)":
            Clock.schedule_once(lambda dt: setattr(self.button, 'disabled', False))

    def music_thread(self):
        self.device = connect(status_callback=self.update_status)

        def on_ready(genre_name, playlist_name):
            playlist = find_playlist(playlist_name)
            transfer_playlist(self.device, genre_name, playlist_name, playlist, self, restart_callback, disconnect_callback)
            clean_temp()

        def restart_callback():
            if self.device:
                print_folder_tree(self.device)
            else:
                Clock.schedule_once(lambda dt: setattr(self.button, 'disabled', False))
                return

            print("\n{     Add Music     }\n")
            get_music(self, on_ready)

        def disconnect_callback():
            self.on_disconnect()
            return

        restart_callback()

class AppBuild(App):
    def build(self):
        self.title = "Garmin Glorious App (Music)"
        self.ui = AppUI()
        return self.ui

    def on_close(self, *args):
        if hasattr(self.ui, "device") and self.ui.device:
            self.ui.device.disconnect()
        return False

if __name__ == "__main__":
    AppBuild().run()