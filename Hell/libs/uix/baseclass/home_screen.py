import json

from kivy.properties import ListProperty, NumericProperty

from components.boxlayout import PBoxLayout
from components.dialog import PDialog
from components.screen import PScreen


class HomeScreen(PScreen):

    chats = ListProperty()
    popup = None

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
                    "unread_messages": self.data[i]["unread_messages"],
                    "on_release": lambda x={
                        "name": i,
                        **self.data[i],
                    }: self.goto_chat_screen(x),
                }
                self.chats.append(user_data)
        else:
            self.ids.first.opacity = 1

    def goto_chat_screen(self, user):
        self.manager.set_current("chat")
        chat_screen = self.manager.get_screen("chat")
        chat_screen.user = user
        chat_screen.chat_logs = []
        chat_screen.title = user["name"]
        chat_screen.receive(user["message"])

    def show_menu(self):
        PDialog(content=MenuDialogContent()).open()

    def create(self):
        self.popup = PDialog(content=CreatePopup())
        self.popup.open()


class MenuDialogContent(PBoxLayout):
    pass


class CreatePopup(PBoxLayout):
    pass

