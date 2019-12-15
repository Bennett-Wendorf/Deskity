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
    token = None
    sign_in_label_text = "Sign in to Microsoft"
    tasks = None
    #def __init__(self):
    #    super().__init__()
    #    integration = ToDoIntegration()

    def get_access_code(self):
        self.token = self.integration.Aquire_Access_Token()
        print("Access token is:", self.token)
        if(self.token != None):
            print("About to change sign in label text")
            sign_in_label_text = "You are signed in to Microsoft"
            #self.ids.microsoft_sign_in.disabled = True
            self.Aquire_Task_Info()

    def Aquire_Task_Info(self):
        self.tasks = self.integration.Get_Tasks(self.token)
        print(self.tasks)
        print(type(self.tasks))

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
