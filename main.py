import os
os.environ["KIVY_NO_ARGS"]="1"

from helpers.ArgHandler import Parse_Args, Get_Args

from logger.AppLogger import build_logger
logger = build_logger(debug=Get_Args().verbose)

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from integrations.ToDoIntegrations.ToDoWidget import ToDoWidget
from integrations.WeatherIntegrations.WeatherWidget import WeatherWidget
from kivy.uix.boxlayout import BoxLayout

# Set the default size of the window to 480x320, the size of my 3.5" touchscreen module for a Raspberry Pi
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

class MainBoxLayout(BoxLayout):
    '''The main box layout of the app. Only one of these should be instantiated at a time. See raspideskstats.kv for layout.'''
    def __init__(self):
        super().__init__()

class RaspiDeskStatsApp(App):
    '''The main setup for the app. Instantiates the screen manager and binds the height of the tasks grid layout.'''
    def build(self):
        return MainBoxLayout()

# Run the app when this file is run.
if __name__ == '__main__':
    Parse_Args()
    RaspiDeskStatsApp().run()
