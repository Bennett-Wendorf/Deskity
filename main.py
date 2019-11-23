from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.core.window import Window

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

class ToDoWidget(Widget):
    def on_touch_down(self, touch):
        print(touch)

class Main(BoxLayout):
    pass

class RaspiDeskStatsApp(App):
    def build(self):
        return Main()

if __name__ == '__main__':
    RaspiDeskStatsApp().run()
