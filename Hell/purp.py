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

from kivy.properties import BooleanProperty, ObjectProperty
from kivy.clock import Clock

from functools import partial

if platform != "android":
    Window.size = (350, 650)

def rename_variable_in_dict(dictionary, old_variable_name, new_variable_name):
    if old_variable_name in dictionary:
        value = dictionary[old_variable_name]
        del dictionary[old_variable_name]
        dictionary[new_variable_name] = value
    return dictionary


class PurpApp(App):
    theme_cls = ThemeManager()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.title = "Velox"
        self.icon = "assets/images/logo.png"

        self.theme_cls.theme_style = config.get_theme_style()

        Window.keyboard_anim_args = {"d": 0.2, "t": "linear"}
        Window.softinput_mode = "below_target"

        self.long_press_duration = 0.3  # Adjust this value to change the long press duration
        self.is_touching = False
        self.long_press_trigger = None

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

        }
        self.root.get_screen("home").chats.append(user_data)
        self.root.set_current("home")

        self.root.get_screen("home").popup.dismiss(force=True)
        self.root.get_screen("home").ids.first.opacity = 0
        self.root.get_screen("home").ids.first.height = 0

    def nah(self, touch, name):
        a, touch = touch
        if a.collide_point(*touch.pos):
            if touch.is_mouse_scrolling:
                # Scrolling detected, ignore the touch event
                return
            self.is_touching = True
            self.long_press_trigger = Clock.schedule_once(partial(self.check_press_type, name), self.long_press_duration)

    def no(self, n, touch):
        if self.is_touching:
            if not n.collide_point(*touch.pos):
                self.cancel_press()

    def noo(self, n, touch, text):
        if self.is_touching:
            self.cancel_press()
            if n.collide_point(*touch.pos):
                print("Short press detected!")
                self.root.get_screen("home").goto_chat_screen(text)
                print(text)

    def check_press_type(self, name, *args):
        if self.is_touching:
            print("Long press detected!")
            self.root.get_screen("home").user_settings(name)
            self.cancel_press()

    def cancel_press(self):
        self.is_touching = False
        if self.long_press_trigger:
            self.long_press_trigger.cancel()
            self.long_press_trigger = None

    def delete_user(self, user):
        print("I have never called that functin")
        # Read the JSON file
        with open('assets/users.json', 'r') as file:
            data = json.load(file)
        # Delete the entry with key "asd"
        if user in data:
            del data[user]

        # Write the updated data back to the JSON file
        with open('assets/users.json', 'w') as file:
            json.dump(data, file, indent=4)

        self.root.get_screen("home").popup2.dismiss(force=True)

        with open('assets/users.json', 'r') as file:
            data = json.load(file)
        self.root.get_screen("home").chats = []
        if data != {}:
            for i in data:
                user_data = {
                    "text": i,
                    "secondary_text": data[i]["message"],
                    "time": data[i]["time"],
                    "image": data[i]["image"],
                    "name": i,
                    "unread_messages": data[i]["unread_messages"],
                }
                self.root.get_screen("home").chats.append(user_data)
        else:
            self.root.get_screen("home").ids.first.opacity = 1

        self.root.set_current("home")


if __name__ == "__main__":
    PurpApp().run()
