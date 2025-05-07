from scripts.settings import BACKGROUND_COLOR, TEXT_COLOR, CURSOR_COLOR, HINT_COLOR, AUTO_SYNC, OPTIONS_PATH
from scripts.settings import DESKTOP, WINDOW_WIDTH, WINDOW_HEIGHT

from scripts.connection import connect
from scripts.transfer import sync_playlists, print_folder_tree, transfer_playlist
from scripts.audio import get_music
from scripts.mods import find_playlist, clean_temp

from kivy.config import Config
Config.set("graphics", "width", WINDOW_WIDTH)
Config.set("graphics", "height", WINDOW_HEIGHT)
Config.set("graphics", "resizable", "0")

from kivy.app import App
from kivy.clock import Clock

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior

from kivy.core.window import Window
from kivy.core.text import LabelBase
LabelBase.register(name="orbitron_regular", fn_regular="fonts/orbitron_regular.ttf")

import sys
import threading
import json

class OptionsButton(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = "assets/cog.png"
        self.size_hint = (None, None)
        self.size = (32, 32)
        self.allow_stretch = True
        self.keep_ratio = True
        self.color = (1, 1, 1, 0.2)

    @staticmethod
    def load_options():
        with open(OPTIONS_PATH, "r") as file:
            return json.load(file)

    @staticmethod
    def save_options(data):
        with open(OPTIONS_PATH, "w") as file:
            json.dump(data, file, indent=4)

    def on_options(self, instance):
        current_options = self.load_options()
        content = BoxLayout(orientation="vertical", spacing=5, padding=10)
        inputs = {}

        for key, value in current_options.items():
            row = BoxLayout(orientation="horizontal", spacing=5, size_hint_y=None, height=30)
            row.add_widget(Label(
                text=key,color=TEXT_COLOR,
                font_name="orbitron_regular",
                size_hint_x=0.4)
            )

            if isinstance(value, bool):
                checkbox = CheckBox(
                    active=value
                )
                inputs[key] = checkbox
                row.add_widget(checkbox)
            else:
                input_field = TextInput(
                    text=str(value),
                    multiline=False,
                    size_hint_x=None,
                    width=300 if DESKTOP else 80,
                    foreground_color=TEXT_COLOR,
                    background_color=BACKGROUND_COLOR,
                    cursor_color=CURSOR_COLOR
                )
                inputs[key] = input_field
                row.add_widget(input_field)

            content.add_widget(row)

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)

        def update_options(_):
            updated_options = current_options.copy()
            for key, widget in inputs.items():
                if isinstance(widget, CheckBox):
                    updated_options[key] = widget.active
                else:
                    current_value = updated_options[key]
                    input_value = widget.text
                    try:
                        if isinstance(current_value, int):
                            updated_options[key] = int(input_value)
                        elif isinstance(current_value, float):
                            updated_options[key] = float(input_value)
                        else:
                            updated_options[key] = input_value
                    except Exception as e:
                        print(e)
                        updated_options[key] = input_value

            self.save_options(updated_options)
            print("\n[ Options Saved, Restart To Apply Changes. ]\n")
            popup.dismiss()

        save_button = Button(
            text="Save",
            background_normal="",
            background_color=BACKGROUND_COLOR,
            color=TEXT_COLOR,
            font_name="orbitron_regular"
        )
        save_button.bind(on_release=update_options)

        close_button = Button(
            text="Close",
            background_normal="",
            background_color=BACKGROUND_COLOR,
            color=TEXT_COLOR,
            font_name="orbitron_regular"
        )
        close_button.bind(on_release=lambda _: popup.dismiss())

        buttons.add_widget(save_button)
        buttons.add_widget(close_button)
        content.add_widget(buttons)

        popup = Popup(
            title="Options [Requires Restart]",
            title_font="orbitron_regular",
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False,
            background="",
            background_color=BACKGROUND_COLOR
        )
        popup.open()

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

        float_layout = FloatLayout()
        box_layout = BoxLayout(orientation="vertical")

        self.options = OptionsButton(pos_hint={"x": 0.88, "top": 0.95})
        self.options.bind(on_press=self.options.on_options)

        self.console = ConsoleOutput(readonly=True,
                                     size_hint=(1, 0.8),
                                     font_name="orbitron_regular",
                                     foreground_color=TEXT_COLOR,
                                     cursor_color=CURSOR_COLOR,
                                     background_color=BACKGROUND_COLOR)
        box_layout.add_widget(self.console)

        self.button = Button(text="Connect",
                             size_hint=(1, 0.1),
                             font_name="orbitron_regular",
                             color=TEXT_COLOR,
                             background_color=BACKGROUND_COLOR,
                             background_normal=""
                             )
        self.button.bind(on_press=self.on_connect)
        box_layout.add_widget(self.button)

        self.input_field = TextInput(hint_text="Input...",
                                     size_hint=(1, 0.1),
                                     font_name="orbitron_regular",
                                     foreground_color=TEXT_COLOR,
                                     cursor_color=CURSOR_COLOR,
                                     hint_text_color=HINT_COLOR,
                                     background_color=BACKGROUND_COLOR,
                                     multiline=False)
        self.input_field.bind(on_text_validate=self.on_enter)
        box_layout.add_widget(self.input_field)

        float_layout.add_widget(box_layout)
        float_layout.add_widget(self.options)

        self.add_widget(float_layout)

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
                if AUTO_SYNC:
                    sync_playlists(self.device)
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