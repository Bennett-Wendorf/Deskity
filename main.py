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
from kivy.uix.image import AsyncImage
from integrations.ToDoIntegrations.ToDo import ToDoIntegration
from integrations.WeatherIntegrations.Weather import Weather
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.base import runTouchApp
import threading
from kivy.clock import Clock

# Set the default size of the window to 480x320, the size of my 3.5" touchscreen module for a Raspberry Pi
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '320')
Window.size=(480,320)

# The widget that handles all transactions for the Microsoft To Do integration.
class ToDoWidget(BoxLayout):
    integration = ToDoIntegration()
    access_code_thread = None
    token = None
    sign_in_label_text = "Sign in to Microsoft"
    tasks = None
    grid_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(ToDoWidget, self).__init__(**kwargs)

        # If an account exists in cache, get it now. If not, don't do anything and let user sign in on settings screen.
        if(self.integration.app.get_accounts()):
            self.Get_Access_Code_Threaded()

    # Run Get_Access_Code() in a new thread
    def Get_Access_Code_Threaded(self):
        access_code_thread = threading.Thread(target=self.Get_Access_Code)
        access_code_thread.setDaemon(True)
        access_code_thread.start()

    # Aquire a new access token or pull one from the cache. 
    # Assuming one was found, pull new task info from the API
    def Get_Access_Code(self):
        self.token = self.integration.Aquire_Access_Token()
        if(self.token != None):
            self.sign_in_label_text = "You are signed in to Microsoft"
            self.Aquire_Task_Info()

    # Aquire task information from the To Do integration and render them on screen
    def Aquire_Task_Info(self):
        self.tasks = self.integration.Get_Tasks(self.token)
        self.Render_Tasks()

    # For each task in the new list of tasks, instantiate a new task object and add the new object to the grid layout of tasks
    def Render_Tasks(self):
        #This is how it should be able to work. Not sure why this doesn't
        #grid_layout = self.ids['tasks_list']
        for task in self.tasks:
            new_task_item = TaskItem(task)
            self.grid_layout.add_widget(new_task_item)

# A task item object. Holds info about the task it contains and sets up a layout with that information. Layout set up in raspideskstats.kv
class TaskItem(RelativeLayout):
    task = None
    task_name = StringProperty()
    #taskName = ""
    def __init__(self, task, **kwargs):
        super(TaskItem, self).__init__(**kwargs)
        self.task = task
        print("Adding new task:", task['subject'])
        self.task_name = self.task['subject']

class WeatherWidget(BoxLayout):
    integration = Weather()

    val = 36

    weather_icon = ObjectProperty()

    def __init__(self, **kwargs):
        super(WeatherWidget, self).__init__(**kwargs)
        # Schedule the icon to populate itself next frame
        Clock.schedule_once(self.Update_UI, 0)
        print(self.integration.Get_Temp())

    def Update_UI(self, *args):
        self.weather_icon.source = self.integration.Get_Icon()

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
