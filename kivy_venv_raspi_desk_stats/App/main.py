from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class ToDoWidget(Widget):
    def on_touch_down(self, touch):
        print(touch)

class RaspiDeskStatsApp(App):
    def build(self):
        mainBoxLayout = BoxLayout(orientation='horizontal')
        leftBoxLayout = BoxLayout(orientation='vertical')
        appLauncher = Widget()
        leftBoxLayout.add_widget(appLauncher)
        leftBoxLayout.add_widget(Button(text='App location'))
        toDo = Label(text="To Do List Placeholder")
        mainBoxLayout.add_widget(leftBoxLayout)
        mainBoxLayout.add_widget(toDo)
        return mainBoxLayout

if __name__ == '__main__':
    RaspiDeskStatsApp().run()
