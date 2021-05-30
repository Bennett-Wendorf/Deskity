from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, DictProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import json

class TaskItem(RelativeLayout, RecycleDataViewBehavior):
    """
    A task item object. Holds info about the task it contains and sets up a layout with that information. 
    
    Layout set up in raspideskstats.kv
    """
    importance = StringProperty()
    isReminderOn = BooleanProperty()
    status = StringProperty()
    title = StringProperty()
    createdDateTime = StringProperty()
    lastModifiedDateTime = StringProperty()
    id = StringProperty()
    body = DictProperty()
    list_id = StringProperty()
    visible = ObjectProperty()
    isCompleted = BooleanProperty()
    index = None

    def __init__(self, **kwargs):
        super(TaskItem, self).__init__(*kwargs)

        self.children[1].bind(active=self.Box_Checked)

    # def __init__(self, task_data, list_id, **kwargs):
    #     self.importance = task_data['importance']
    #     self.is_reminder_on = task_data['isReminderOn']
    #     self.status = task_data['status']
    #     self.title = task_data['title']
    #     self.created_date_time = task_data['createdDateTime']
    #     self.last_modified_date_time = task_data['lastModifiedDateTime']
    #     self.id = task_data['id']
    #     self.body = task_data['body']
    #     self.list_id = list_id

    #     super(TaskItem, self).__init__(**kwargs)

    #     self.children[1].bind(active=self.Box_Checked)

    def Box_Checked(self, checkbox, value, *kwargs):
        # kwargs is needed here since Clock.schedule_once passes the time difference between scheduling and method call.
        # We don't really care about that time difference, so I'm just ignoring it here.
        print(checkbox, "checked with value", value)
        old_status = self.Get_Status()

        if value:
            self.Set_Status('completed')
        else:
            print("Task '", self.Get_Title(), "' is already complete.")
            self.Set_Status('notStarted')

        # TODO: Update the remote task
        # if old_status != task.Get_Status():
        #         self.Update_Task(task)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        self.status = data['status']
        return super(TaskItem, self).refresh_view_attrs(rv, index, data)

    # TODO: get rid of these legacy functions in favor of Set_Status
    def Mark_Complete(self):
        return self.Set_Status('completed')

    def Mark_Incomplete(self):
        return self.Set_Status('notStarted')

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

    def Set_Status(self, new_status):
        valid_statuses = ['completed', 'notStarted']
        if valid_statuses.count(new_status) > 0:
            self.status = new_status
            if self.parent and self.parent.parent:
                self.parent.parent.data[self.index]['status'] = new_status
            return self.Get_Status() == new_status
    
    def Get_Id(self):
        return self.id

    def Get_List_Id(self):
        return self.list_id

    def Get_Body(self):
        return self.body

    def Get_Importance(self):
        return self.importance

    def Build_Dict(self):
        return {
            'importance': self.importance, 
            'isReminderOn': self.is_reminder_on, 
            'status': self.status, 
            'title': self.title, 
            'createdDateTime': self.created_date_time, 
            'lastModifiedDateTime': self.last_modified_date_time, 
            'id': self.id, 
            'body': self.body
        }

    def Build_Json(self):
        return json.dumps(self.Build_Dict())

    def Set_Visibility(self, visible):
        self.visible = visible

    def __eq__(self, other):
        if not isinstance(other, TaskItem):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id