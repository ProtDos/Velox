import json

from kivy.metrics import sp
from kivy.properties import ListProperty, NumericProperty, StringProperty, Clock
from kivy.uix.button import Button
from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen
from components.label import PLabel


class HomeScreen(PScreen):

    chats = ListProperty()
    popup = None
    popup2 = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with open("assets/users.json") as f:
            self.data = json.load(f)

        print(len(self.data))

        if self.data != {}:
            for i in self.data:
                user_data = {
                    "text": i,
                    "secondary_text": self.data[i]["message"],
                    "time": self.data[i]["time"],
                    "image": self.data[i]["image"],
                    "name": i,
                    "unread_messages": self.data[i]["unread_messages"],
                }
                self.chats.append(user_data)
                print(self.chats)
        else:
            self.ids.first.opacity = 1

    def goto_chat_screen(self, user3):
        print(user3)
        with open("assets/users.json") as f:
            self.data = json.load(f)
        user = {
             "name": user3,
             **self.data[user3],
        }
        self.manager.set_current("chat")
        chat_screen = self.manager.get_screen("chat")
        chat_screen.user = user
        chat_screen.chat_logs = []
        chat_screen.title = user["name"]
        chat_screen.receive(user["message"])

    def show_menu(self, *args):
        PDialog(content=MenuDialogContent()).open()

    def create(self):
        self.popup = PDialog(content=CreatePopup())
        self.popup.open()

    def user_settings(self, name):
        with open("assets/users.json") as f:
            data = json.load(f)
        for item in data:
            if item == name:
                print(item)
                print(data[item])
                self.popup2 = PDialog(
                    content=UserInfoDialogContent(
                        title=item,
                        image=data[item]["image"],
                        about=data[item]["about"],
                    )
                )
                self.popup2.open()
                return


class MenuDialogContent(PBoxLayout):
    pass


class CreatePopup(PBoxLayout):
    pass


class UserInfoDialogContent(PBoxLayout):
    title = StringProperty()
    image = StringProperty()
    about = StringProperty()


