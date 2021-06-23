from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, DictProperty
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.recycleview.views import RecycleDataViewBehavior
import json

class TaskItem(RelativeLayout, RecycleDataViewBehavior):
    """
    A task item object. Holds info about the task it contains and sets up a layout with that information. 
    
    Layout set up in raspideskstats.kv
    """
    status = StringProperty()
    title = StringProperty()
    id = StringProperty()
    body = DictProperty()
    list_id = StringProperty()
    # isCompleted = BooleanProperty()
    createdDateTime = StringProperty()
    dueDateTime = None
    lastModifiedDateTime = StringProperty()
    importance = StringProperty()
    isReminderOn = BooleanProperty()
    isVisible = BooleanProperty()
    index = None

    def __init__(self, **kwargs):
        super(TaskItem, self).__init__(*kwargs)
        if self.id != '':
            self.list_id = self.id[:-1]
        self.children[1].bind(active=self.Box_Checked)

    def Box_Checked(self, checkbox, value, *kwargs):
        # kwargs is needed here since Clock.schedule_once passes the time difference between scheduling and method call.
        # We don't really care about that time difference, so I'm just ignoring it here.

        if value:
            self.Set_Status('completed')
        else:
            self.Set_Status('notStarted')

        if self.parent and self.parent.parent:
            self.parent.parent.Update_Task(self.index)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        # self.status = data['status']
        # self.title = data['title']
        # self.id = data['id']
        # self.body = data['body']
        # self.list_id = data['list_id']
        # self.createdDateTime = data['createdDateTime']
        # self.lastModifiedDateTime = data['lastModifiedDateTime']
        # self.importance = data['importance']
        # self.isReminderOn = data['isReminderOn']
        # self.isVisible = data['isVisible']
        # if 'dueDateTime' in data:
        #     self.dueDateTime = data['dueDateTime']
        return super(TaskItem, self).refresh_view_attrs(rv, index, data)

    def Get_Title(self):
        '''Return the title of this task object.'''
        return self.title

    def Set_Title(self, new_title):
        '''Set the title of this task object and return whether it was properly set.'''
        self.title = new_title
        if self.title == new_title:
            return True
        else:
            return False

    def Get_Status(self):
        '''Return the status of this task object.'''
        return self.status

    def Set_Status(self, new_status):
        '''Set the status of this task to the specified status, as long as that status is a valid option.'''
        valid_statuses = ['completed', 'notStarted']
        if valid_statuses.count(new_status) > 0:
            self.status = new_status
            if self.parent and self.parent.parent:
                item = self.parent.parent.to_do_tasks[self.index].copy()
                item['status'] = new_status
                self.parent.parent.to_do_tasks[self.index] = item
            return self.Get_Status() == new_status
    
    def Get_Id(self):
        '''Return the id of this task object.'''
        return self.id

    def Get_List_Id(self):
        '''Return the list id of this task object.'''
        return self.list_id

    def Get_Body(self):
        '''Return the body of this task object.'''
        return self.body

    def Get_Importance(self):
        '''Return the importance of this task object.'''
        return self.importance

    def Build_Dict(self):
        '''Return the attributes of this task as a dictionary.'''
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
        '''Return the attributes of this object as JSON.'''
        return json.dumps(self.Build_Dict())

    def __hash__(self):
        '''Hashes TaskItem objects using their 'id' attribute to ensure that the same objects are always hashed the same.'''
        return hash(self.id)

    def __eq__(self, other):
        '''
        Return equality for TaskItem based on the 'id' attribute. 
        
        If two tasks have the same id, then they are effectively the same task.
        '''
        if not isinstance(other, TaskItem):
            # Don't attempt to compare against unrelated types
            return NotImplemented

        return self.id == other.id