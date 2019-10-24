import kivy

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.app import App

class TestApp(App):
    def build(self):
        boxLayout = BoxLayout(orientation='horizontal', padding=50)
        boxLayout.add_widget(Button(text='Button1'))
        boxLayout.add_widget(Button(text='Button2'))
        return boxLayout

if __name__ == '__main__':
    TestApp().run()