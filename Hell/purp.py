import json
import os
import random
import sys

root_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
sys.path.insert(0, os.path.join(root_dir, "libs", "applibs"))
sys.path.insert(0, os.path.join(root_dir, "libs", "uix"))


from kivy.app import App
from kivy.core.window import Window
from kivy.utils import platform
from datetime import datetime

import components
from androspecific import statusbar
from core.theming import ThemeManager
from root import Root
from utils.configparser import config
from components.toast import toast

if platform != "android":
    Window.size = (350, 650)


class PurpApp(App):
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Velox"
        self.icon = "assets/images/logo.png"

        self.theme_cls.theme_style = config.get_theme_style()

        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.softinput_mode = "below_target"

    def build(self):
        self.root = Root()
        self.root.set_current("auth")

    def on_start(self):
        statusbar.set_color(self.theme_cls.primary_color)

    def is_name_taken(self, name):
        with open('assets/users.json', 'r') as file:
            data = json.load(file)
        return name in data

    def create_chat(self, rec):
        if rec == "":
            toast("Please enter a recipient")
            return
        if self.is_name_taken(rec):
            toast("Recipient already taken.")
            return

        with open('assets/users.json', 'r') as file:
            data = json.load(file)

        pb = f"assets/images/{random.randint(1, 8)}.jpg"
        t = str(f"{datetime.now().strftime('%H:%M')}")

        # Add a new entry to the dictionary
        data[rec] = {
            "image": pb,
            "message": "This is a new message.",
            "time": t,
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
            "time": t,
            "image": pb,
            "unread_messages": False,
            "on_release": lambda x={
                "name": rec,
                **data2[rec],
            }: self.root.get_screen("home").goto_chat_screen(x),

        }
        self.root.get_screen("home").chats.append(user_data)
        self.root.set_current("home")

        self.root.get_screen("home").popup.dismiss(force=True)
        self.root.get_screen("home").ids.first.opacity = 0

    def nah(self, touch, name):
        print(touch, name)


if __name__ == "__main__":
    PurpApp().run()
