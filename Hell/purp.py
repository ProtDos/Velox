
import json
import os
import random

import sys
import time
import uuid

import socket
import rsa

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

from security import *



#if __name__ == "__main__":
#    N = 167
#    p = 3
#    q = 128
#    filename = "myKey"
#
#    generate(N, p, q, filename + ".priv", filename + ".pub")
#
#    inp = b"test"
#
#    input_arsa = np.unpackbits(np.frombuffer(inp, dtype=np.uint8))
#    input_arsa = np.trim_zeros(input_arsa, 'b')
#
#    out = encrypt(filename + ".pub.npz", input_arsa=input_arsa)
#
#    print(out)
#
#    dec = decrypt(filename + ".priv.npz", out)
#
#    a = np.packbits(np.arsaay(dec).astype(np.int)).tobytes().decode()
#    print(a)
#    print(type(a))


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

    def change_avatar(self):
        print("Not available")

    def signup(self, username, password):
        # First with RSA, then with NTRU

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 5000))
        sock.send(f"USER_EXISTS:{username}".encode())
        if sock.recv(1024) == b"exists":
            toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return

        if len(username) > 12:
            toast("Username too long.")
            return
        if " " in username:
            toast("No space allowed.")
            return
        if hashCrackWordlist(password) is not None or strength_test(password)[0] is False:
            toast("Password isn't strong enough.")
            return

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 5000))
        
        idd = uuid.uuid4()
        public, private = rsa.newkeys(512)

        sock.send(f"SIGNUP:::{username}:::{hash_pwd(password)}:::{idd}".encode())
        print("nah bruh")
        time.sleep(.5)
        sock.send(public.save_pkcs1())
        r = sock.recv(1024).decode()
        if r == "error":
            toast("Username taken. Try again.")
            self.root.get_screen("auth").uname.shake()
            return
        elif r == "errorv2":
            toast("ID already used - internal error. Try again later.")
            return
        elif r == "errorv4":
            toast("Invalid username.")
            self.root.get_screen("auth").uname.shake()
            return



        """
        with open("private_key.txt", "w") as file:
            file.write(self.private_key.save_pkcs1().decode())
        """
        with open(f"private_key_{username}.txt", "w") as file:
            file.write(
                Encrypt(message_=private.save_pkcs1().decode(), key=password).encrypt().decode())
        with open(f"public_key_{username}.txt", "w") as file:
            file.write(public.save_pkcs1().decode())

        toast("Account created successfully!")
        self.login(username, password, show=False)

    def login(self, username, password, show=True):
        if username == "" or password == "":
            return
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("localhost", 5000))
        
        sock.send(f"LOGIN:::{username}:::{hash_pwd(password)}".encode())
        r = sock.recv(1024).decode()
        print(r)
        if r == "error":
            toast("Invalid username")
            self.root.get_screen("auth").uname.shake()
            # self.root.get_screen("auth").password.shake()
            return
        elif r == "errorv2":
            toast("Invalid password")
            self.root.get_screen("auth").password.shake()
            return
        else:
            # with open("private_key.txt", "rb") as file:
            #     self.private_key = rsa.PrivateKey.load_pkcs1(file.read())
            if username != "Google":
                with open(f"private_key_{username}.txt", "r") as file:
                    a = file.read()
                    dec_priv = Decrypt(message_=a, key=password).decrypt().encode()
                    # print(dec_priv)
                    if dec_priv is None:
                        toast("Private key couldn't be decrypted.")
                        return
                    self.private_key = rsa.PrivateKey.load_pkcs1(dec_priv)
            else:
                self.public = rsa.PublicKey.load_pkcs1(
                    b'-----BEGIN RSA PUBLIC KEY-----\nMIIBCgKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDzSvum\nujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR3WDH\nxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/QQIC\nnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEiTLXh\nNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC8yjz\nV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQAB\n-----END RSA PUBLIC KEY-----\n')
                self.private_key = rsa.PrivateKey.load_pkcs1(
                    b'-----BEGIN RSA PRIVATE KEY-----\nMIIEqQIBAAKCAQEAlinP8nQRq3UWBtimgucKjX8bO9xG9dBXPsTJy8VLek9e1GDz\nSvumujfD1EXEvtAJHOQWzkAfCI8X/NfwjHnZ6PVAeka8cZooR05q/nyeeJcqJNTR\n3WDHxNVe7FL1IsML//BtYibumbogDNVrzsN1YAcxtK4M60GgHUPBgZMoJCXuLiP/\nQQICnOCKKdresNS7UYqrltr68xcBQLkBfbeJtlICOdLfYX31Krsaoi6PiRF3hVvEi\nTLXhNgVukTrkf7Afp+/C10mE5NClLfjrGFPZmbaAwrLCV6t5bWGWifG7NVUQtAZC\n8yjzV9jJljVLaXp4sQmGgE4ATvHqgvuAJQRyhQIDAQABAoIBACKRh5SKEdNFxgdX\ncqWp6G0AeNWD9TX7e0ow5T+qsKB8ixkbJIb7fbtawRMp6IwAukhTXcinTD2dK2mC\nkJbWKksNwoUjqZgBZApeTBU/vP+H1STbdWCgOfzfHdYLlvEks6t8vsGcssri5SPv\nMb1Mk8XCgjfU5ZZ26ekuVV0VJLoMAeTQT9GSQBPeLLI38YQsLvWWLBiGP+zbAC9E\nH7JhnLf6yZzcWUrt8F8uFclydM1Zl/Jzvtf2v7DXZBapr7goykgJt+dfOqG6L3mN\n7K7HIKPMdWT/j2TiS9bjEik7NQV/CkqltNE+SiXJqddDqHJZklHSSKERUgNoc+s1\nvKPS1XUCgYkAutyUZcFY/VROPZQHGGJ7DF13j1y3GajcfdM/W9dWNaTKD+JSu0NJ\n29txB/7zPT+JNtBZ/Jb2WzFtY8hmeZKSYZJAJPpOHBweBZLVnZdocg+WVbAOBjXu\nPpJm0G9lQY0NPgetJm7gxRAx7HtohGBAXkp/Q5sskzLeEOXhaRwg3hIcMPi9LaMY\nywJ5AM25MOwluNdqzVE2H7kyODIb3guXHT73qQ9bMM91CWVo3NCP4+eR9yYVtRgv\nQ8Nbu5K1pFYQEifk6O8Xl/O+h5x4lBUbOwN5yezQxYBs+mXhbrZR6HN+IuSLidzj\nCViQ+BmJwE9uXfl4h5fI8EU/yo99WoSJjaBH7wKBiGW/F9q0ReVi01t6T8a6UO/x\nsNlSDa0eIjktHpG+lgWNniy5+nxW7k+VlF1bOE0AXJGJL4Z3GNuc9Uhg5VOLOMOC\nJAU+eeuab8pvInu15rw8uoob2/cLxJczlmImVcc0q6I8Ac8sjp0e7WAr7kQuOL5e\n6B8Czmm0R/CBi5R1KXxh9hHATxobdbMCeQC9abZupyiyRqa2EGRTCrcNA/WErGUE\nFdk1x1uAl5zIHy24ZdOL4iwxh6kOlG4K0Eo7AT1G9FMTIkOJ6CpDBPktiyOk70Z9\no8PUZECER1KhPVfHTFD/DXMpBIUxuGRhhFC6isdjGxYxXNVTXnJDAEILrXoLL+8T\nVUcCgYgil44+MdrsaYh63SEppvtkbGMJD93YDjp3ugoRi6u+GfXv/8RBb1QjI1zfO\n1bKVhcxu9PlFmcfSmzN+H48hQu+eLpJH930iqumVqPGw9UHR0JwZQhU9j/k665IS\nlIg1rSRgaX1KdpVsfx5Fv8qzCrL+aIjWV4u9RQPFBw1HEARCbS8EPCHVi3DL\n-----END RSA PRIVATE KEY-----\n')
            self.username = username
            self.password = password
            self.super_dubba_key = password
            _, idd = r.split(":")
            self.id = idd
            toast("Logged in!")

        self.root.set_current("home")
        if show:
            toast("Signed In successfully!")


if __name__ == "__main__":
    PurpApp().run()
