#region Imports

# HTTP requests and url parsing
import requests
import aiohttp
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs

# Data formats
import json

from helpers.ArgHandler import Get_Args
from helpers.APIError import APIError
from helpers.Helpers import multikeysort

# Logging
from logger.AppLogger import build_logger
# Build the logger object, using the argument for verbosity as the setting for debug log level
logger = build_logger(logger_name="To Do Widget", debug=Get_Args().verbose)

# Scheduling and threading
import atexit
import time
from datetime import datetime
import asyncio
import threading
from kivy.clock import Clock
from functools import partial

# Integration
from integrations.ToDoIntegrations.Task import TaskItem
from integrations.ToDoIntegrations import MSALHelper

# Kivy
from kivy.properties import ObjectProperty, StringProperty, ListProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button 
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.datamodel import RecycleDataModel

# Settings
from dynaconf_settings import settings

#endregion

default_sort_order = ['-status', 'dueDateTime', 'title']
default_lists = []
default_task_visibility = True

class ToDoWidget(RecycleView):
    """
    Handle all transactions for the Microsoft To Do integration.
    """

    # This stores all the actual task data in dictionaries
    to_do_tasks = ListProperty()

    data = []

    delta_links = {}

    sign_in_label_text = StringProperty()
    sign_in_button = ObjectProperty()
    
    def __init__(self, **kwargs):
        """Initialize the To Do Widget and authenticate to Microsoft Graph"""

        super(ToDoWidget, self).__init__(**kwargs)
        MSALHelper.Setup_Msal(self)
        Clock.schedule_interval(self.Start_Local_Update_Process, settings.To_Do_Widget.get('update_interval', 30))

    def refresh_from_data(self, *largs, **kwargs):
        """Ensure that the display of tasks gets resorted any time the data is updated"""

        # Resort the data after information updates
        self.to_do_tasks = multikeysort(self.to_do_tasks, settings.To_Do_Widget.get('task_sort_order', default_sort_order))
        super(ToDoWidget, self).refresh_from_data(largs, kwargs)

    def Setup_Tasks(self, *kwargs):
        """
        Make sure all the tasks are set up properly during initialization.

        Ensure that a valid access token is present, pull all the tasks 
        from the API, sort them correctly, and display them on screen.
        """

        start = time.time()
        logger.info("Starting task setup")
        
        asyncio.run(self.Get_All_Tasks())
        self.to_do_tasks = multikeysort(self.to_do_tasks, settings.To_Do_Widget.get('task_sort_order', default_sort_order))

        logger.info("Finished setting up tasks during initialization")
        logger.debug(f"This task setup took {time.time() - start} seconds.")

    def Get_Task_Lists(self):
        """
        Get To Do task lists from Microsoft's graph API.

        NOTE: This is usually only run by the Get_All_Tasks method, there should
        be no need to get task lists without pulling the tasks from them.
        """

        logger.debug("Getting task lists")

        # Pull the specified lists from the config file. If that setting does not exist, default to an empty list that will pull all tasks
        lists_to_use = settings.To_Do_Widget.get('lists_to_use', default_lists)

        to_return = []

        # This specifies how many lists to pull on every request. For some reason, Microsoft's API
        # will only give an odata.nextLink url if this is specified. If not, it will only return 16
        # lists, even if there are more.
        pull_per_request = 20

        # Set up endpoint and headers for request
        lists_endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists?$top=" + str(pull_per_request)

        while True:
            # Run the get request to the endpoint
            lists_response = requests.get(lists_endpoint, headers=MSALHelper.Get_Msal_Headers())

            # If the request was a success, return the JSON data, else print an error code
            if(lists_response.status_code == 200):
                json_data = json.loads(lists_response.text)
                # This is a list of task lists available
                lists = json_data['value']

                if lists_to_use:
                    for task_list in lists:
                        if lists_to_use.count(task_list['displayName']) > 0:
                            # Then this list is in my list of lists to use and I should be pulling data from it
                            to_return.append(task_list)
                else:
                    to_return.extend(lists)
                
                if not '@odata.nextLink' in json_data:
                    # Then I got all the tasks needed, so I can return
                    logger.info("Obtained task lists successfully")
                    logger.debug(f"Pulled {len(to_return)} lists")
                    return to_return
                else:
                    lists_endpoint = json_data['@odata.nextLink']
            else:
                logger.error("The response did not return a success code. Returning nothing.")
                raise APIError("The response did not return a success code. Returning nothing.")

    async def Get_Tasks_From_List(self, session, list_name, list_id, all_tasks):
        """
        Asynchronously get data from the specified list and append the tasks to the 'all_tasks' list.
        """

        logger.info(f"Pulling tasks from list '{list_name}'")
        # Set up the first endpoint for this list
        endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists/" + list_id + "/tasks/delta"

        while True:
            # Pull this set of data from the specified endpoint, and allow the code to switch to another coroutine here
            async with session.get(endpoint, headers=MSALHelper.Get_Msal_Headers()) as response:

                # If the response came back OK
                if response.status == 200:
                    # Load the json from the response
                    json_data = json.loads(await response.text())
                    # Parse out the data from the response
                    json_value = json_data['value']
                    for task in json_value:
                        # Add the list idea to the data so I can update the remote task later
                        task['list_id'] = list_id
                        # Set the visiblity for the new task
                        if task['status'] == "completed":
                            # TODO in-app toggle for this
                            task['isVisible'] = False
                        else:
                            task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', default_task_visibility)
                        all_tasks.append(task)

                    # TODO Find a more logical way to do this
                    # If there is no more data in this list, then break out of the loop
                    if not '@odata.nextLink' in json_data or not json_value:
                        if '@odata.deltaLink' in json_data:
                            self.delta_links[list_id] = json_data['@odata.deltaLink']
                        break

                    # If this line is run, then there is more data in this list, so set up the endpoint and loop
                    endpoint = json_data['@odata.nextLink']
                elif response.status == 429:
                    # TODO Fix throttling issue.
                    logger.warning("Throttling from MS Graph. Retrying request.")
                    # time.sleep(int(response.headers['Retry-After']))
                else:
                    logger.error(f"Failed to get tasks from list '{list_name}'")
        
    async def Get_All_Tasks(self):
        """
        Pull individual tasks from the list returned by Get_Task_Lists and return them as a single list of dicts.
        """

        # TODO: Consider moving this to MSALHelper
        MSALHelper.Set_Msal_Headers({'Content-Type':'application/json', 'Authorization':'Bearer {0}'.format(MSALHelper.Aquire_Access_Token())})
        task_lists = self.Get_Task_Lists()

        if not task_lists:
            logger.error("There was an issue getting task lists")
            return None

        all_tasks = []

        logger.debug("Getting tasks")

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            request_task_list = []

            for task_list in task_lists:
                request_task = asyncio.create_task(self.Get_Tasks_From_List(session, task_list['displayName'], task_list['id'], all_tasks))
                request_task_list.append(request_task)
            await asyncio.gather(*request_task_list, return_exceptions=False)

        logger.debug(f"Downloaded {len(all_tasks)} tasks in {time.time() - start_time} seconds")

        # Set the data and make sure it is displayed on screen, in sorted order
        self.to_do_tasks = all_tasks
        self.refresh_from_data()
    
    def Update_Task(self, task_index):
        """
        Send a patch request to Microsoft's graph API to update the task data for the specified task.

        Also updates the task locally in terms of sort order, etc.
        """

        if task_index >= len(self.to_do_tasks):
            return
        
        task = self.to_do_tasks[task_index].copy()

        # Update local task
        # This section can contain any checks that need to be made any time a local task is updated
        # TODO in-app toggle for this
        if task['status'] == "completed":
            task['isVisible'] = False
        else:
            task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', default_task_visibility)

        # This needs to happen so that the ListProperty for data properly picks up the change
        self.to_do_tasks[task_index] = task

        # Update the recycleview with the new data. This ensures that any sorting other other changes are
        # properly displayed
        self.refresh_from_data()

        # Start the process of updating the task on the remote server in a new thread.
        # This is in a new thread so that the UI can update immediately, while the request
        # to Microsoft takes a small amount of time.
        remote_task_thread = threading.Thread(target=self.Push_Updated_Task, args=(task,))
        remote_task_thread.start()

    def Push_Updated_Task(self, task):
        """
        Updates the given task on the remote server. This is designed to be run in a thread so as to not 
        delay the main UI when waiting for Microsoft's API.
        """

        task_endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists/" + task['list_id'] + "/tasks/" + task['id']
        task_data = {k: task[k] for k in task.keys() - {'list_id', 'isVisible'}}
        requests.patch(task_endpoint, data=json.dumps(task_data), headers=MSALHelper.Get_Msal_Headers())

    def Start_Local_Update_Process(self, dt):
        """
        Start a new thread for updating the local task information from the server.
        """

        update_thread = threading.Thread(target=self.Locally_Update_All_Tasks)
        update_thread.setDaemon(True)
        update_thread.start()

    def Locally_Update_All_Tasks(self):
        """
        Make a request to the delta endpoint on Microsoft graph and update 
        the local tasks as specified.
        """
        
        logger.info("Starting tasks update")
        # TODO Look into a more pythonic way to do this with list comprehension
        # or something using async functions.
        for list_id in self.delta_links:
            # TODO Handle the case where the token in self.msal['headers'] may not be valid anymore
            response = requests.get(self.delta_links[list_id], headers=MSALHelper.Get_Msal_Headers())
            if response.status_code == 200:
                json_data = json.loads(response.text)
                # Reassign the new delta link provided by the api
                self.delta_links[list_id] = json_data['@odata.deltaLink']
                if json_data['value']:
                    for task in json_data['value']:
                        # I can use next here since the task id's are going to be unique coming from Microsoft;
                        # I don't have to worry about multiple local tasks with the same id
                        # Return the index of an existing task in to_do_tasks, or None if 'task' is not in the list
                        local_task_index = next((i for i, item in enumerate(self.to_do_tasks) if item['id']==task['id']), None)

                        if '@removed' in task:
                            logger.info(f"Removed task titled '{self.to_do_tasks[local_task_index]['title']}'")
                            # Remove the task from the local list and then move on to the next item in the list
                            self.to_do_tasks.pop(local_task_index)
                            continue

                        # Set task visibility based on new completion status
                        if task['status'] == "completed":
                            # TODO in-app toggle for this
                            task['isVisible'] = False
                        else:
                            task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', default_task_visibility)

                        task['list_id'] = list_id

                        # TODO There is a small chance here that the local_task_index changes between the time I obtain it and reassign the task back
                        # Make sure to fix this issue!
                        if local_task_index != None:
                            logger.info(f"Updating existing task titled '{task['title']}'")
                            self.to_do_tasks[local_task_index] = task
                        else:
                            logger.info(f"Adding new task titled '{task['title']}'")
                            self.to_do_tasks.append(task)
                    
                    self.refresh_from_data()
            elif response.status_code == 410:
                # TODO: Figure out what to do here
                logger.warning(f"The entire dataset for list id '{list_id}' must be redownloaded")
            else:
                logger.error(f"Something went wrong checking for updated tasks on list id '{list_id}'")