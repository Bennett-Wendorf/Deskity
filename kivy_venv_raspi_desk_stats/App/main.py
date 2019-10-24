from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox

class ToDoWidget(Widget):
    def on_touch_down(self, touch):
        print(touch)

class RaspiDeskStatsApp(App):
    def build(self):
        mainBoxLayout = BoxLayout(orientation='horizontal')
        leftBoxLayout = BoxLayout(orientation='vertical')
        appLauncher = BoxLayout(orientation='horizontal')
        appLauncher.add_widget(CheckBox(pos=(50,150)))
        leftBoxLayout.add_widget(appLauncher)
        leftBoxLayout.add_widget(Button(text="App Location Placeholder"))
        toDo = Label(text="To Do List Placeholder")
        mainBoxLayout.add_widget(leftBoxLayout)
        mainBoxLayout.add_widget(toDo)
        return mainBoxLayout

if __name__ == '__main__':
    RaspiDeskStatsApp().run()
