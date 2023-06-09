from kivy.animation import Animation
from kivy.properties import ColorProperty

from components.screen import PScreen
from components.toast import toast

from utils.configparser import config

from components.boxlayout import PBoxLayout
from components.dialog import PDialog


class AuthScreen(PScreen):
    bg_color = ColorProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.primary_color

    def show_form(self):

        self.ids.intro.remove_widget(self.ids.intro_btn)
        Animation(bg_color=self.theme_cls.bg_normal, d=0.4).start(self)
        Animation(
            d=0.7, scale=0.75, text_color=self.theme_cls.primary_color
        ).start(self.ids.title)
        Animation(d=0.7, pos_hint={"center_y": 0.75}).start(self.ids.intro)
        self.ids.form.disabled = False

        a = config.is_startup()
        print(a)

        if a == "True" or a is True:
            print("a")
            PDialog(content=AboutDialogContent2()).open()

    def sign_in(self):
        self.manager.set_current("home")
        toast("Signed In successfully!")

    def sign_up(self):
        self.ids.uname.shake()
        toast("Account created successfully! Please Sign In to jump in!")


class AboutDialogContent2(PBoxLayout):
    pass
