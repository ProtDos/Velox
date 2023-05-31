import json
import os
import sys

root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(root_dir, "libs", "applibs"))
sys.path.insert(0, os.path.join(root_dir, "libs", "uix"))


from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform

import components
from androspecific import statusbar
from core.theming import ThemeManager
from root import Root
from utils.configparser import config

if platform != "android":
    Window.size = (350, 650)


class PurpApp(App):
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Purp"
        self.icon = "assets/images/logo_w.png"

        self.theme_cls.theme_style = config.get_theme_style()

        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.softinput_mode = "below_target"

    def build(self):
        self.root = Root()
        self.root.set_current("auth")

    def on_start(self):
        statusbar.set_color(self.theme_cls.primary_color)

    def create_chat(self, rec):
        with open('assets/users.json', 'r') as file:
            data = json.load(file)

        # Add a new entry to the dictionary
        data[rec] = {
            "image": "assets/images/5.jpg",
            "message": "This is a new message.",
            "time": "10:00",
            "about": "Just added!",
            "unread_messages": False
        }

        # Write the updated dictionary back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)

        with open('assets/users.json', 'r') as file:
            data2 = json.load(file)

        user_data = {
            "text": rec,
            "secondary_text": "This is a new person.",
            "time": "10:00",
            "image": "assets/images/5.jpg",
            "unread_messages": False,
            "on_release": lambda x={
                "name": rec,
                **data2[rec],
            }: self.root.get_screen("home").goto_chat_screen(x)
        }
        self.root.get_screen("home").chats.append(user_data)
        self.root.set_current("home")

        self.root.get_screen("home").popup.dismiss(force=True)
        self.root.get_screen("home").ids.first.opacity = 0


if __name__ == "__main__":
    PurpApp().run()
