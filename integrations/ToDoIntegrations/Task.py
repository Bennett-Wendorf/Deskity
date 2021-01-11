from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.relativelayout import RelativeLayout
import json

class TaskItem(RelativeLayout):
    """
    A task item object. Holds info about the task it contains and sets up a layout with that information. 
    
    Layout set up in raspideskstats.kv
    """
    title = StringProperty()

    def __init__(self, task_data, list_id, **kwargs):
        self.importance = task_data['importance']
        self.is_reminder_on = task_data['isReminderOn']
        self.status = task_data['status']
        self.title = task_data['title']
        self.created_date_time = task_data['createdDateTime']
        self.last_modified_date_time = task_data['lastModifiedDateTime']
        self.id = task_data['id']
        self.body = task_data['body']
        self.list_id = list_id

        super(TaskItem, self).__init__(**kwargs)

    def Mark_Complete(self):
        self.status = "completed"
        if self.Get_Status() == "completed":
            return True
        else:
            return False

    def Mark_Uncomplete(self):
        self.status = "notStarted"
        if self.Get_Status() == "notStarted":
            return True
        else:
            return False

    def Get_Title(self):
        return self.title

    def Set_Title(self, new_title):
        self.title = new_title
        if self.title == new_title:
            return True
        else:
            return False

    def Get_Status(self):
        return self.status
    
    def Get_Id(self):
        return self.id

    def Get_List_Id(self):
        return self.list_id

    def Get_Body(self):
        return self.body

    def Get_Importance(self):
        return self.importance

    def Build_Json(self):
        dictionary = {
            'importance': self.importance, 
            'isReminderOn': self.is_reminder_on, 
            'status': self.status, 
            'title': self.title, 
            'createdDateTime': self.created_date_time, 
            'lastModifiedDateTime': self.last_modified_date_time, 
            'id': self.id, 
            'body': self.body
        }
        return json.dumps(dictionary)

    def __eq__(self, other):
        if not isinstance(other, TaskItem):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id