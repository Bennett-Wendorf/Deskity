#region Imports

# HTTP requests and url parsing
import requests
import aiohttp
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs

# Data formats
import json
import yaml

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

# MSAL authentication
from msal import PublicClientApplication, SerializableTokenCache
from requests_oauthlib import OAuth2Session
import os

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

# The authorization code returned by Microsoft
# This needs to be global to allow the request handler to obtain it and pass it back to Aquire_Auth_Code()
authorization_response = None

# Note that this class needs to be at the top of this file.
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    '''
    Request handler to parse urls during a get request and strip out authorization code
    as a string. It also sets the global autorization_response variable to the authorization code.
    '''

    def do_GET(self):
        global authorization_response
        query_components = parse_qs(urlparse(self.path).query)
        code = str(query_components['code'])
        authorization_response = code[2:len(code)-2]
        if self.path == '/':
            self.path = 'index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

class ToDoWidget(RecycleView):
    '''
    Handle all transactions for the Microsoft To Do integration.
    '''
    # Load the authentication_settings.yml file
    # Note: this file is not tracked by github, so it will need to be created before running
    stream = open('integrations/ToDoIntegrations/microsoft_authentication_settings.yml', 'r')
    settings = yaml.safe_load(stream)

    # The instance of the Public Client Application from MSAL. This is assigned in __init__
    app = None

    # This stores all the actual task data in dictionaries
    to_do_tasks = ListProperty()

    data = []

    delta_links = {}

    # The settings required for msal to properly authenticate the user
    msal = {
        'authority': "https://login.microsoftonline.com/common",
        'authorize_endpoint': "/oauth2/v2.0/authorize",
        'redirect_uri': "http://localhost:1080",
        'token_endpoint': "/oauth2/v2.0/token",
        'scopes': ["user.read", "Tasks.ReadWrite"],
        'headers': "",

        # The access token aquired in Aquire_Access_Token. This is a class variable for the cases
        # where there is an attempt to make a request again in the short time this token is valid for.
        # If that should happen, storing the token like this minimalizes the amount of requests needed
        # to Microsoft's servers
        'access_token': None
    }

    sign_in_label_text = StringProperty()
    sign_in_button = ObjectProperty()
    
    def __init__(self, **kwargs):

        super(ToDoWidget, self).__init__(**kwargs)

        # This is necessary because Azure does not guarantee
        # the return of scopes in the same case and order as requested
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

        cache = self.Deserialize_Cache("integrations/ToDoIntegrations/microsoft_cache.bin")

        # Instantiate the Public Client App
        self.app = PublicClientApplication(self.settings['app_id'], authority=self.msal['authority'], token_cache=cache)

        # If an account exists in cache, get it now. If not, don't do anything and let user sign in on settings screen.
        if(self.app.get_accounts()):
            setup_thread = threading.Thread(target=self.Setup_Tasks)
            setup_thread.start()

        Clock.schedule_interval(self.Start_Update_Loop, settings.To_Do_Widget.get('update_interval', 30))

    #region MSAL

    def Deserialize_Cache(self, cache_path):
        '''Create the cache object, deserialize it for use, and register it to be reserialized before the application quits.'''
        cache = SerializableTokenCache()
        if os.path.exists(cache_path):
            cache.deserialize(open(cache_path, "r").read())
            print("[To Do Widget] [{0}] Reading MSAL token cache".format(self.Get_Timestamp()))

        # Register a function with atexit to make sure the cache is written to just before the application terminates.
        atexit.register(lambda:
            open(cache_path, "w").write(cache.serialize())
            # Hint: The following optional line persists only when state changed
            if cache.has_state_changed else None
        )

        return cache

    # Gets access token however it is needed and returns that token
    def Aquire_Access_Token(self):
        '''
        If there is an access token in the cache, get it and obtain an authorization code using it. 
        Else run the Aquire_Auth_Code method to have the user authenticate.
        '''
        result = None
        accounts = self.app.get_accounts()

        if(self.msal['access_token'] == None):

            result = self.Pull_From_Token_Cache()

            if (result == None):
                # Then there was no token in the cache

                # Get auth code
                authCode = self.Aquire_Auth_Code(self.settings)

                # Aquire token from Microsoft with auth code and scopes from above
                result = self.app.acquire_token_by_authorization_code(authCode, scopes=self.msal["scopes"], redirect_uri=self.msal['redirect_uri'])
            
            # Strip down the result and convert it to a string to get the final access token
            self.msal['access_token'] = str(result['access_token'])
        
        if self.msal['access_token'] != None:
            self.sign_in_label_text = "You are signed in to Microsoft"
            # self.sign_in_button.visible = False # TODO: Re-enable this
            return True
        else:
            print(f"[To Do Widget] [{self.Get_Timestamp()}] Something went wrong and no token was obtained!")
            return False


    def Pull_From_Token_Cache(self):
        '''If there is a vaild account in the cache, obtain it and then use it to get and return an access token.'''
        accounts = self.app.get_accounts()
        if accounts:
            # TODO: Will implement better account management later. For now, the first account found is chosen.
            return self.app.acquire_token_silent(self.msal["scopes"], account=accounts[0])
        else:
            print(f"[To Do Widget] [{self.Get_Timestamp()}] No accounts were found.")
            return None

    def Aquire_Auth_Code(self, settings):
        '''Aquire MSAL authorization code from Microsoft.'''
        # Use the global variable authorization_response instead of a local one
        global authorization_response

        # Begin localhost web server in a new thread to handle the get request that will come from Microsoft
        webServerThread = threading.Thread(target=self.Run_Localhost_Server)
        webServerThread.setDaemon(True)
        webServerThread.start()

        # Builds url from yml settings
        authorize_url = '{0}{1}'.format(self.msal['authority'], self.msal['authorize_endpoint'])

        # Begins OAuth session with app_id, scopes, and redirect_uri from yml
        aadAuth = OAuth2Session(settings['app_id'], scope=self.msal['scopes'], redirect_uri=self.msal['redirect_uri'])

        # Obtain final login url from the OAuth session
        sign_in_url, state = aadAuth.authorization_url(authorize_url)

        # Opens a web browser with the new sign in url
        webbrowser.open(sign_in_url, new=2, autoraise=True)

        # Waits until the web server thread closes before continuing
        # This ensures that an authorization response will be returned.
        webServerThread.join()

        # This function returns the global authorization_response when it is not equal to None
        return authorization_response
    
    #endregion

    def refresh_from_data(self, *largs, **kwargs):
        # Resort the data after the update
        self.to_do_tasks = self.multikeysort(self.to_do_tasks, settings.To_Do_Widget.get('task_sort_order', ['-status', 'title']))
        super(ToDoWidget, self).refresh_from_data(largs, kwargs)

    def Setup_Tasks(self, *kwargs):
        '''
        Make sure all the tasks are set up properly during initialization.

        Ensure that a valid access token is present, pull all the tasks 
        from the API, sort them correctly, and display them on screen.
        '''
        start = time.time()
        print(f"[To Do Widget] [{self.Get_Timestamp()}] Starting task setup")
        success = self.Aquire_Access_Token()
        if success:
            asyncio.run(self.Get_Tasks())
            self.to_do_tasks = self.multikeysort(self.to_do_tasks, settings.To_Do_Widget.get('task_sort_order', ['-status', 'title']))
            self.last_task_update = time.time()

            print(f"[To Do Widget] [{self.Get_Timestamp()}] Finished setting up tasks during initialization in {time.time() - start} seconds.")

    def Start_Update_Loop(self, dt):
        # TODO: Consider moving this to the main python file for a unified update loop across integrations.
        update_thread = threading.Thread(target=self.Update_All_Tasks)
        update_thread.setDaemon(True)
        update_thread.start()

    def Update_All_Tasks(self):
        print(f"[To Do Widget] [{self.Get_Timestamp()}] Starting tasks update.")
        # TODO Look into a more pythonic way to do this with list comprehension
        # or something using async functions.
        for list_id in self.delta_links:
            # TODO Handle the case where the token in self.msal['headers'] may not be valid anymore
            response = requests.get(self.delta_links[list_id], headers=self.msal['headers'])
            if response.status_code == 200:
                json_data = json.loads(response.text)
                # Reassign the new delta link provided by the api
                self.delta_links[list_id] = json_data['@odata.deltaLink']
                if json_data['value']:
                    self.Update_Given_Tasks(json_data['value'], list_id)
            elif response.status_code == 410:
                print(f"[To Do Widget] [{self.Get_Timestamp()}] The entire dataset for list id '{list_id}' must be redownloaded.")
            else:
                print(f"[To Do Widget] [{self.Get_Timestamp()}] Something went wrong checking for updated tasks on list id '{list_id}'")

    def Update_Given_Tasks(self, tasks_to_update, list_id):
        for task in tasks_to_update:

            # I can use next here since the task id's are going to be unique coming from Microsoft
            # Return the index of an existing task in to_do_tasks, or None if 'task' is not in the list
            local_task_index = next((i for i, item in enumerate(self.to_do_tasks) if item['id']==task['id']), None)

            if '@removed' in task:
                print(f"[To Do Widget] [{self.Get_Timestamp()}] Removed task titled '{self.to_do_tasks[local_task_index]['title']}'")
                removed_task = self.to_do_tasks.pop(local_task_index)
                continue

            if task['status'] == "completed":
                # TODO in-app toggle for this
                task['isVisible'] = False
            else:
                task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', True)

            task['list_id'] = list_id

            # TODO There is a small chance here that the local_task_index changes between the time I obtain it and reassign the task back
            # Make sure to fix this issue!
            if local_task_index != None:
                print(f"[To Do Widget] [{self.Get_Timestamp()}] Updating existing task titled '{task['title']}'")
                self.to_do_tasks[local_task_index] = task
            else:
                print(f"[To do Widget] [{self.Get_Timestamp()}] Adding new task titled '{task['title']}'")
                self.to_do_tasks.append(task)
        
        self.refresh_from_data()

    def Get_Task_Lists(self):
        '''
        Get To Do task lists from Microsoft's graph API.

        NOTE: This is usually only run by the Get_Tasks method, there should
        be no need to get task lists without pulling the tasks from them.
        '''
        print("[To Do Widget] [{0}] Getting task lists".format(self.Get_Timestamp()))

        # Pull the specified lists from the config file. If that setting does not exist, default to an empty list that will pull all tasks
        lists_to_use = settings.To_Do_Widget.get('lists_to_use', [])

        to_return = []

        # Set up endpoint and headers for request
        lists_endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists"

        # Run the get request to the endpoint
        lists_response = requests.get(lists_endpoint, headers=self.msal['headers'])

        # If the request was a success, return the JSON data, else print an error code
        # TODO: replace print with thrown exception
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
            
            print("[To Do Widget] [{0}] Obtained task lists successfully".format(self.Get_Timestamp()))
            return to_return
        else:
            print("The response did not return a success code. Returning nothing.")
            return None

    async def Get_Tasks_From_List(self, session, list_name, list_id, all_tasks):
        '''
        Asynchronously get data from the specified list and append the tasks to the 'all_tasks' list.
        '''
        print(f"[To Do Widget] [{self.Get_Timestamp()}] Pulling tasks from list '{list_name}'")
        # Set up the first endpoint for this list
        endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists/" + list_id + "/tasks/delta"

        while True:
            # Pull this set of data from the specified endpoint, and allow the code to switch to another coroutine here
            async with session.get(endpoint, headers=self.msal['headers']) as response:

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
                            task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', True)
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
                    print(f"[To Do Widget] [{self.Get_Timestamp()}] Throttling from MS Graph. Retrying request.")
                    # time.sleep(int(response.headers['Retry-After']))
                else:
                    print(f"[To Do Widget] [{self.Get_Timestamp()}] Failed to get tasks from list '{list_name}'")
        
    async def Get_Tasks(self):
        '''
        Pull individual tasks from the list returned by Get_Task_Lists and return them as a single list of dicts.
        '''
        self.msal['headers'] = {'Content-Type':'application/json', 'Authorization':'Bearer {0}'.format(self.msal['access_token'])}
        task_lists = self.Get_Task_Lists()

        if not task_lists:
            print("There was an issue getting task lists.")
            return None

        all_tasks = []

        print(f"[To Do Widget] [{self.Get_Timestamp()}] Getting tasks")

        start_time = time.time()

        async with aiohttp.ClientSession() as session:
            request_task_list = []

            for task_list in task_lists:
                request_task = asyncio.create_task(self.Get_Tasks_From_List(session, task_list['displayName'], task_list['id'], all_tasks))
                request_task_list.append(request_task)
            await asyncio.gather(*request_task_list, return_exceptions=False)

        duration = time.time() - start_time
        print(f"[To Do Widget] [{self.Get_Timestamp()}] Downloaded {len(all_tasks)} tasks in {duration} seconds")

        # Set the data and make sure it is displayed on screen, in sorted order
        self.to_do_tasks = all_tasks
        self.refresh_from_data()
    
    def Update_Task(self, task_index):
        '''
        Send a patch request to Microsoft's graph API to update the task data for the specified task.

        Also updates the task locally in terms of sort order, etc.
        '''
        if task_index >= len(self.to_do_tasks):
            return
        
        task = self.to_do_tasks[task_index].copy()

        # Update local task
        # This section can contain any checks that need to be made any time a local task is updated
        # TODO in-app toggle for this
        if task['status'] == "completed":
            task['isVisible'] = False
        else:
            task['isVisible'] = settings.To_Do_Widget.get('incomplete_task_visibility', True)

        # This needs to happen so that the ListProperty for data properly picks up the change
        self.to_do_tasks[task_index] = task

        # Update the recycleview with the new data. This ensures that any sorting other other changes are
        # properly displayed
        self.refresh_from_data()

        # Start the process of updating the task on the remote server in a new thread.
        remote_task_thread = threading.Thread(target=self.Update_Remote_Task, args=(task,))
        remote_task_thread.start()

    def Update_Remote_Task(self, task):
        '''
        Updates the given task on the remote server. This is designed to be run in a thread so as to not 
        delay the main UI when waiting for Microsoft's API.
        '''
        task_endpoint = "https://graph.microsoft.com/v1.0/me/todo/lists/" + task['list_id'] + "/tasks/" + task['id']
        task_data = {k: task[k] for k in task.keys() - {'list_id', 'isVisible'}}
        requests.patch(task_endpoint, data=json.dumps(task_data), headers=self.msal['headers'])
    
    def Run_Localhost_Server(self, server_class=http.server.HTTPServer, handler_class=RequestHandler):
        '''
        Start a basic web server on localhost port 1080 using the custom request handler defined at the start of this file.

        This will only handle one request and then terminate.
        '''
        server_address = ('127.0.0.1', 1080)
        httpd = server_class(server_address, handler_class)
        httpd.handle_request()

    # TODO Add this to a helper class for use accross integrations
    def Get_Timestamp(self):
        '''
        Return the current timestamp in the format that is used for all output for this program.
        '''
        return datetime.now().strftime("%m/%d/%y %H:%M:%S.%f")[:-4]

    def multikeysort(self, items, columns):
        '''
        Return the sorted list of dictionaries 'items' sorted in order by the keys in 'columns'. 
        
        These keys are specified as a list of strings in 'columns'. A '-' can be added to the 
        front of each key to reverse the sort order.
        '''
        from operator import itemgetter
        from functools import cmp_to_key
        comparers = [((itemgetter(col[1:].strip()), -1) if col.startswith('-') else (itemgetter(col.strip()), 1))
                    for col in columns]
        def cmp(x, y):
            return (x > y) - (x < y)

        def comparer(left, right):
            comparer_iter = (
                cmp(fn(left), fn(right)) * mult
                for fn, mult in comparers
            )
            return next((result for result in comparer_iter if result), 0)
        return sorted(items, key=cmp_to_key(comparer))