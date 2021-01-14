from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from integrations.ToDoIntegrations.ToDoWidget import ToDoWidget
from integrations.WeatherIntegrations.WeatherWidget import WeatherWidget
from kivy.base import runTouchApp

# Set the default size of the window to 480x320, the size of my 3.5" touchscreen module for a Raspberry Pi
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

#region Kivy Screens and Manager

# A Main Screen object. Only one of these should be instantiated at a time. See raspideskstats.kv for layout.
class MainScreen(Screen):
    pass       

# A Settings Screen object. Only one of these should be instantiated at a time. See raspideskstats.kv for layout.
class SettingsScreen(Screen):
    pass

# A Screen Manager object. This is the root widget of the kivy hierarchy and handles switching between screens in app. See raspideskstats.kv for layout.
class Screen_Manager(ScreenManager):
    def __init__(self, **kwargs):
        #super(Screen_Manager, self).__init__(**kwargs)
        super().__init__()
        Window.bind(on_key_down = self.On_Key_Press)
    
    # Handles key presses for switching to main and settings screens.
    def On_Key_Press(self, *args):
        key_pressed = args[3]
        print ("Got key event. Key pressed was: ", key_pressed)
        if(key_pressed == 's'):
            self.Switch_To_Settings()
        elif(key_pressed == 'm'):
            self.Switch_To_Main()

    # Switch to main screen from any other screen.
    def Switch_To_Main(self):
        self.transition.direction = 'down'
        self.current = 'main_screen'
        print("Attempting Switch_To_Main()")
    
    # Switch to settings screen from any other screen.
    def Switch_To_Settings(self):
        self.transition.direction = 'up'
        self.current = 'settings_screen'
        print("Attempting Switch_To_Settings()")

#endregion

# The main setup for the app. Instantiates the screen manager and binds the height of the tasks grid layout.
class RaspiDeskStatsApp(App):
    def build(self):
        manager = Screen_Manager()
        grid_layout = manager.ids.tasks_list
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        return manager

# Run the app when this file is run.
if __name__ == '__main__':
    RaspiDeskStatsApp().run()
    #root = Screen_Manager()
    #runTouchApp(root)
