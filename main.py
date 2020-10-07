from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.checkbox import CheckBox
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen
from integrations.ToDoIntegrations.ToDo import ToDoIntegration
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.base import runTouchApp
import threading

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

class ToDoWidget(BoxLayout):
    integration = ToDoIntegration()
    access_code_thread = None
    token = None
    sign_in_label_text = "Sign in to Microsoft"
    tasks = None
    grid_layout = ObjectProperty() # Will want to stream line this eventually
    def __init__(self, **kwargs):
        super(ToDoWidget, self).__init__(**kwargs)
        print("Grid_layout:", self.grid_layout)
        #self.grid_layout.bind(minimum_height=self.grid_layout.setter('height'))
    #    integration = ToDoIntegration()

    def get_access_code_threaded(self):
        access_code_thread = threading.Thread(target=self.get_access_code)
        access_code_thread.setDaemon(True)
        access_code_thread.start()

    def get_access_code(self):
        self.token = self.integration.Aquire_Access_Token()
        if(self.token != None):
            sign_in_label_text = "You are signed in to Microsoft"
            #self.ids.microsoft_sign_in.disabled = True
            self.Aquire_Task_Info()

    def Aquire_Task_Info(self):
        self.tasks = self.integration.Get_Tasks(self.token)
        self.Render_Tasks()

    def Render_Tasks(self):
        #This is how it should be able to work. Not sure why this doesn't
        #grid_layout = self.ids['tasks_list']
        for task in self.tasks:
            new_task_item = TaskItem(task)
            self.grid_layout.add_widget(new_task_item)

class TaskItem(RelativeLayout):
    task = None
    task_name = StringProperty()
    #taskName = ""
    def __init__(self, task, **kwargs):
        super(TaskItem, self).__init__(**kwargs)
        self.task = task
        print("Adding new task:", task['subject'])
        self.task_name = self.task['subject']

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
        print("Screen Manager IDs are", self.ids)
    
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
        manager = Screen_Manager()
        grid_layout = manager.ids.tasks_list
        grid_layout.bind(minimum_height=grid_layout.setter('height'))
        return manager

if __name__ == '__main__':
    RaspiDeskStatsApp().run()
    #root = Screen_Manager()
    #runTouchApp(root)
