import json
import timeit

from kivy.animation import Animation
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ColorProperty, StringProperty, Clock
from kivy.uix.behaviors import ButtonBehavior

from components.boxlayout import PBoxLayout
from core.theming import ThemableBehavior

from baseclass.home_screen import HomeScreen

Builder.load_string(
    """
<ListItem>
    spacing: dp(15)
    padding: dp(10)
    adaptive_height: True

    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    PBoxLayout:
        adaptive_size: True
        pos_hint: {"center_y": .5}

        PIcon:
            icon: root.icon
            adaptive_size: True
            font_size: sp(30)

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None


<-ChatListItem>
    padding: [dp(10), dp(15)]
    spacing: dp(10)
    adaptive_height: True
    
    on_touch_down:
        app.nah(args, self.text)
    
    on_touch_move:
        app.no(*args)
    
    on_touch_up:
        app.noo(*args, self.text)
    
    #on_long_press:
    #    app.nah("asd", "asd")
    
    canvas.before:
        Color:
            rgba: root.bg_color
        RoundedRectangle:
            radius: [dp(18),]
            size: self.size
            pos: self.pos

    PBoxLayout:
       
        adaptive_size: True
        pos_hint: {"center_y": .5}

        FitImage:
            source: root.image
            size_hint: None, None
            size: dp(50), dp(50)
            radius: [dp(18),]

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_height: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.text
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

        PLabel:
            text: root.secondary_text
            font_name: 'LexendLight'
            text_color: 0.5, 0.5, 0.5, 0.5
            adaptive_height: True
            shorten: True
            shorten_from: 'right'
            text_size: self.width, None

    PBoxLayout:
        orientation: 'vertical'
        spacing: dp(7)
        adaptive_size: True
        pos_hint: {"center_y": .5}

        PLabel:
            text: root.time
            font_name: 'LexendThin'
            adaptive_size: True

        Widget:
            size_hint: None, None
            size: dp(10), dp(10)

            canvas.before:
                Color:
                    rgba:
                        root.theme_cls.primary_color if root.unread_messages \
                        else (0, 0, 0, 0)
                Ellipse:
                    size: self.size
                    pos: self.pos

    """
)


class ListItem(ButtonBehavior, ThemableBehavior, PBoxLayout):

    bg_color = ColorProperty([0, 0, 0, 0])

    text = StringProperty()

    secondary_text = StringProperty()

    icon = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_color = self.theme_cls.bg_normal
        self.theme_cls.bind(theme_style=self._update_bg_color)

        self.long_press_time = 1  # Time threshold for long press in seconds
        self.long_press_event = None

    def _update_bg_color(self, *args):
        self.bg_color = self.theme_cls.bg_normal

    def on_state(self, instance, value):
        Animation(
            bg_color=self.theme_cls.bg_dark
            if value == "down"
            else self.theme_cls.bg_normal,
            d=0.1,
            t="in_out_cubic",
        ).start(self)


class ChatListItem(ListItem):
    image = StringProperty()

    name = StringProperty()

    time = StringProperty()

    unread_messages = BooleanProperty()

    #def __init__(self, **kwargs):
    #    super(ChatListItem, self).__init__(**kwargs)
    #    self.long_press_duration = 0.5  # Adjust this value to change the long press duration
    #    self.is_touching = False
    #    self.long_press_trigger = None
#
    #def on_touch_down(self, touch):
    #    if self.collide_point(*touch.pos):
    #        if touch.is_mouse_scrolling:
    #            # Scrolling detected, ignore the touch event
    #            return
    #        self.is_touching = True
    #        self.long_press_trigger = Clock.schedule_once(self.check_press_type, self.long_press_duration)
#
    #def on_touch_move(self, touch):
    #    if self.is_touching:
    #        if not self.collide_point(*touch.pos):
    #            self.cancel_press()
#
    #def on_touch_up(self, touch):
    #    if self.is_touching:
    #        self.cancel_press()
#
    #        if self.collide_point(*touch.pos):
    #            print("Short press detected!")
    #            print(self.text)
#
    #            with open("assets/users.json") as f:
    #                self.data = json.load(f)
#
    #            x = {
    #                 "name": self.text,
    #                 **self.data[self.text],
    #            }
#
    #            HomeScreen().goto_chat_screen(x)
#
    #            # do this here
#
    #def check_press_type(self, dt):
    #    if self.is_touching:
    #        print("Long press detected!")
    #        print(self.text)
    #        self.cancel_press()
#
    #def cancel_press(self):
    #    self.is_touching = False
    #    if self.long_press_trigger:
    #        self.long_press_trigger.cancel()
    #        self.long_press_trigger = None


