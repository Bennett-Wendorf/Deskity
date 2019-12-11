from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from integrations.ToDoIntegrations.ToDo import ToDoIntegration

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

class ToDoWidget(BoxLayout):
    integration = ToDoIntegration()
    #def __init__(self):
    #    super().__init__()
    #    integration = ToDoIntegration()

    def get_access_code(self):
        code = self.integration.AquireAccessToken()
        print("Access code is:", code)

class MainScreen(Screen):
    pass        

class SettingsScreen(Screen):
    pass

class Screen_Manager(ScreenManager):
    def __init__(self, **kwargs):
        #super(Screen_Manager, self).__init__(**kwargs)
        super().__init__()
        Window.bind(on_key_down = self.on_key_press)
        #self.current = 'main'
    
    def on_key_press(self, *args):
        keyPressed = args[3]
        print ("Got key event. Key pressed was: ", keyPressed)
        if(keyPressed == 's'):
            self.switchToSettings()
        elif(keyPressed == 'm'):
            self.switchToMain()

    def switchToMain(self):
        self.transition.direction = 'up'
        self.current = 'main_screen'
        print("Attempting switchToMain()")
    
    def switchToSettings(self):
        self.transition.direction = 'down'
        self.current = 'settings_screen'
        print("Attempting switchToSettings()")

class RaspiDeskStatsApp(App):
    def build(self):
        return Screen_Manager()

if __name__ == '__main__':
    RaspiDeskStatsApp().run()
