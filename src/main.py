import os
import sys

# Set up some Kivy arguments for proper operation on Raspberry Pi
os.environ["KIVY_NO_ARGS"]="1"
os.environ["KIVY_WINDOW"]="sdl2"
os.environ["KIVY_GL_BACKEND"]="sdl2"

from helpers.ArgHandler import Parse_Args, Get_Args

from logger.AppLogger import build_logger
logger = build_logger(debug=Get_Args().verbose)

from kivymd.app import MDApp
from kivy.config import Config
from kivy.core.window import Window
from integrations.ToDoIntegrations.ToDoWidget import ToDoWidget
from integrations.WeatherIntegrations.WeatherWidget import WeatherWidget
from integrations.SpotifyIntegrations.SpotifyWidget import SpotifyWidget
from kivy.uix.boxlayout import BoxLayout

# Set the default size of the window to 480x320, the size of my 3.5" touchscreen module for a Raspberry Pi
Config.set('graphics', 'width', '480')  # TODO: Try to get rid of this
Config.set('graphics', 'height', '320')
Window.size=(480,320)

class MainBoxLayout(BoxLayout):
    """The main box layout of the app. Only one of these should be instantiated at a time. See deskity.kv for layout"""

    def __init__(self):
        super().__init__()

class DeskityApp(MDApp):
    """The main setup for the app. Instantiates the screen manager and binds the height of the tasks grid layout"""

    def build(self):

        # Allow for different paths to res directory depending on whether we're running an executable or not
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle, the PyInstaller bootloader
            # extends the sys module by a flag frozen=True and sets the app 
            # path into variable _MEIPASS'.
            self.main_path = sys._MEIPASS
            logger.debug(f"Main path: {self.main_path}")
            self.project_path = os.path.normpath(self.main_path)
            logger.debug(f"Project path: {self.project_path}")
        else:
            self.main_path = os.path.dirname(os.path.abspath(__file__))
            logger.debug(f"Main path: {self.main_path}")
            self.project_path = os.path.normpath(self.main_path + "/..")
            logger.debug(f"Project path: {self.project_path}")
        
        self.atlas_path = 'atlas://' + self.project_path + '/res/icons/custom_atlas'
        logger.debug(f"Atlas path: {self.atlas_path}")

        self.theme_cls.primary_palette = "Cyan"
        self.theme_cls.theme_style = "Dark"
        super(DeskityApp, self).build()
        return MainBoxLayout()

# Run the app when this file is run.
if __name__ == '__main__':
    Parse_Args()
    DeskityApp().run()
