from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, DictProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.behaviors import HoverBehavior
import json

from kivy.core.window import Window

from helpers.ArgHandler import Get_Args

from kivymd.app import MDApp

from helpers.Helpers import getDateTimeObj as getDtObj

# Logging
from logger.AppLogger import build_logger
# Build the logger object, using the argument for verbosity as the setting for debug log level
logger = build_logger(logger_name="To Do Task", debug=Get_Args().verbose)

class TaskItem(FloatLayout, RecycleDataViewBehavior, HoverBehavior):
    """
    A task item object. Holds info about the task it contains and sets up a layout with that information. 
    
    Layout is set up in raspideskstats.kv
    """

    status = StringProperty()
    title = StringProperty()
    id = StringProperty()
    body = DictProperty()
    list_id = StringProperty()
    createdDateTime = StringProperty()
    dueDateTime = ObjectProperty(defaultvalue=None, allownone=True)
    lastModifiedDateTime = StringProperty()
    importance = StringProperty()
    isReminderOn = BooleanProperty()
    isVisible = BooleanProperty()
    index = None

    to_do_widget = None

    def __init__(self, **kwargs):
        super(TaskItem, self).__init__(*kwargs)
        if self.id != '':
            self.list_id = self.id[:-1]

        self.ids['checkbox'].bind(active=self.Box_Checked)
        self.to_do_widget = MDApp.get_running_app().root.ids['to_do_widget']

    def Box_Checked(self, checkbox, value: bool, *kwargs):
        """ Handle changing the status of the task and updating it on Microsoft when a checkbox is checked
        
        param checkbox: The checkbox object that was pressed.
        param value: The new value of the checkbox
        param kwargs: Extra arguments. This is needed to handle the time difference that the Clock object passes
        """

        logger.debug(f"[{self.title}] Checkbox pressed")

        if value:
            self.Set_Status('completed')
        else:
            self.Set_Status('notStarted')

        # self.parent here is needed to alleviate issues with this method getting called during setup
        # I need to make sure that Update_Task is only called if this task object has a parent assigned,
        # which IS NOT the case during setup
        if self.to_do_widget and self.parent:
            self.to_do_widget.Update_Task(self.index)

    def on_enter(self, *args):
        """Update the checkbox icon on hover"""

        logger.debug(f"[{self.title}] Entering")
        # Window.set_system_cursor('hand') # TODO: Figure out how too do this nicely
        if self.status == 'completed':
            self.ids['checkbox'].background_checkbox_down = f"{MDApp.get_running_app().atlas_path}/blue_check_bright_hover"
        else:
            self.ids['checkbox'].background_checkbox_normal = f"{MDApp.get_running_app().atlas_path}/blue_check_dark_hover"

    def on_leave(self, *args):
        """Update the checkbox icon on hover"""

        logger.debug(f"[{self.title}] Leaving")
        # Window.set_system_cursor('arrow') # TODO: Figure out how too do this nicely
        if self.status == 'completed':
            self.ids['checkbox'].background_checkbox_down = f"{MDApp.get_running_app().atlas_path}/blue_check"
        else:
            self.ids['checkbox'].background_checkbox_normal = f"{MDApp.get_running_app().atlas_path}/blue_check_unchecked"

    def on_touch_down(self, touch):
        """Update the checkbox status when any part of the task is touched"""

        if(self.hovering):
            logger.debug(f"[{self.title}] Setting checkbox active status")
            if(not self.ids['checkbox'].active):
                self.ids['checkbox'].active = True
            else:
                self.ids['checkbox'].active = False

    def refresh_view_attrs(self, rv, index, data):
        """Catch and handle the view changes"""
        
        self.index = index
        self.status = data['status']
        self.title = data['title']
        self.id = data['id']
        self.body = data['body']
        self.list_id = data['list_id']
        self.createdDateTime = data['createdDateTime']
        self.lastModifiedDateTime = data['lastModifiedDateTime']
        self.importance = data['importance']
        self.isReminderOn = data['isReminderOn']
        self.isVisible = data['isVisible']
        if 'dueDateTime' in data:
            self.dueDateTime = data['dueDateTime']
        else:
            self.dueDateTime = None

        logger.debug(f"[{data['title']}] Refreshing view attributes")
        return super(TaskItem, self).refresh_view_attrs(rv, index, data)

    def Get_Title(self):
        """Return the title of this task object"""
        
        return self.title

    def Set_Title(self, new_title):
        """Set the title of this task object and return whether it was properly set"""

        self.title = new_title
        if self.title == new_title:
            return True
        else:
            return False

    def Get_Status(self):
        """Return the status of this task object"""

        return self.status

    def Set_Status(self, new_status):
        """Set the status of this task to the specified status, as long as that status is a valid option"""

        valid_statuses = ['completed', 'notStarted']
        if valid_statuses.count(new_status) > 0:
            self.status = new_status
            if self.to_do_widget and self.parent:
                item = self.to_do_widget.to_do_tasks[self.index].copy()
                item['status'] = new_status
                self.to_do_widget.to_do_tasks[self.index] = item
            return self.Get_Status() == new_status
    
    def Get_Id(self):
        """Return the id of this task object"""

        return self.id

    def Get_List_Id(self):
        """Return the list id of this task object"""

        return self.list_id

    def Get_Body(self):
        """Return the body of this task object"""

        return self.body

    def Get_Importance(self):
        """Return the importance of this task object"""

        return self.importance

    def Build_Dict(self):
        """Return the attributes of this task as a dictionary"""

        return {
            'importance': self.importance, 
            'isReminderOn': self.isReminderOn, 
            'status': self.status, 
            'title': self.title, 
            'createdDateTime': self.createdDateTime, 
            'lastModifiedDateTime': self.lastModifiedDateTime, 
            'dueDateTime': self.dueDateTime,
            'id': self.id, 
            'body': self.body
        }

    def Build_Json(self):
        """Return the attributes of this object as JSON"""

        return json.dumps(self.Build_Dict())

    def __hash__(self):
        """Hashes TaskItem objects using their 'id' attribute to ensure that the same objects are always hashed the same"""

        return hash(self.id)

    def __eq__(self, other):
        """
        Return equality for TaskItem based on the 'id' attribute. 
        
        If two tasks have the same id, then they are effectively the same task.
        """
        
        if not isinstance(other, TaskItem):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id

    def Get_Display_String(self):
        return f"[{'✓' if self.status == 'completed' else ' '}] {self.title} due: {getDtObj(self.dueDateTime['dateTime']).strftime('%a, %b %-d, %Y') if self.dueDateTime != None else ''}"