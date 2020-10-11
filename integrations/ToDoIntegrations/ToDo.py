from msal import PublicClientApplication
from msal import SerializableTokenCache
import yaml
from requests_oauthlib import OAuth2Session
import os
import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs
import requests
import json
import atexit

# The authorization code returned by Microsoft
# This needs to be global to allow the request handler to obtain it and pass it back to Aquire_Auth_Code()
authorization_response = None

# Request handler to parse url's get request and strip out authorization code as string. 
# Sets the global authorization_response variable to this value.
# Note that this class needs to be at the top of this file.
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global authorization_response
        query_components = parse_qs(urlparse(self.path).query)
        code = str(query_components['code'])
        authorization_response = code[2:len(code)-2]
        if self.path == '/':
            self.path = 'index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

class ToDoIntegration():

    # Load the authentication_settings.yml file
    # Note: this file is not tracked by github, so it will need to be created before running
    stream = open('integrations/ToDoIntegrations/microsoft_authentication_settings.yml', 'r')
    settings = yaml.safe_load(stream)

    # The instance of the Public Client Application from MSAL. This is assigned in __init__
    app = None

    # The access token aquired in Aquire_Access_Token. This is a class variable for the cases
    # where there is an attempt to make a request again in the short time this token is valid for.
    # If that should happen, storing the token like this minimalizes the amount of requests needed
    # to Microsoft's servers
    access_token = None

    def __init__(self):
        # This is necessary because Azure does not guarantee
        # to return scopes in the same case and order as requested
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

        cache = self.Deserialize_Cache("integrations/ToDoIntegrations/microsoft_cache.bin")
        
        # Instantiate the Public Client App
        self.app = PublicClientApplication(self.settings['app_id'], authority=self.settings["authority"], token_cache=cache)

    # Create the cache object, deserialize it for use, and register it to be reserialized before the application quits.
    def Deserialize_Cache(self, cache_path):

        cache = SerializableTokenCache()
        if os.path.exists(cache_path):
            cache.deserialize(open(cache_path, "r").read())
            print("Reading token cache")
        atexit.register(lambda:
            open(cache_path, "w").write(cache.serialize())
            # Hint: The following optional line persists only when state changed
            if cache.has_state_changed else None
            )

        return cache

    # Gets access token however it is needed and returns that token
    def Aquire_Access_Token(self):
        result = None
        accounts = self.app.get_accounts()

        if(self.access_token == None):

            result = self.Pull_From_Token_Cache()

            if (result == None):
                # Get auth code
                authCode = self.Aquire_Auth_Code(self.settings)

                # Aquire token from Microsoft with auth code and scopes from above
                result = self.app.acquire_token_by_authorization_code(authCode, scopes=self.settings["scopes"])
                # Strip down the result and convert it to a string to get the final access token

            self.access_token = str(result['access_token'])
        
        return self.access_token

    def Pull_From_Token_Cache(self):
        accounts = self.app.get_accounts()
        if accounts:
            # Will implement better account management later. For now, the first account found is chosen.
            return self.app.acquire_token_silent_with_error(self.settings["scopes"], account=accounts[0])
        else:
            print("No accounts were found.")
            return None

    # Aquire msal auth code from Microsoft
    def Aquire_Auth_Code(self, settings):

        # Use the global variable authorization_response instead of a local one
        global authorization_response

        # Begin localhost web server in a new thread to handle the get request that will come from Microsoft
        webServerThread = threading.Thread(target=self.Run_Localhost_Server)
        webServerThread.setDaemon(True)
        webServerThread.start()

        # Builds url from yml settings
        authorize_url = '{0}{1}'.format(settings['authority'], settings['authorize_endpoint'])

        # Begins OAuth session with app_id, scopes, and redirect_uri from yml
        aadAuth = OAuth2Session(settings['app_id'], scope=settings['scopes'], redirect_uri=settings['redirect_uri'])

        # Obtain final login url from the OAuth session
        sign_in_url, state = aadAuth.authorization_url(authorize_url)

        # Opens a web browser with the new sign in url
        webbrowser.open(sign_in_url, new=2, autoraise=True)

        # Waits here until the web server receives an authorization_response
        while(authorization_response == None):
            pass

        # This function returns the global authorization_response when it is not equal to None
        return authorization_response
    
    # Gets To Do Tasks from Microsoft
    def Get_Tasks(self, token):

        # Set up endpoint and headers for request
        endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks"
        headers = {'Content-Type':'application/json', 'Authorization':'Bearer {0}'.format(token)}

        # Run the get request to the endpoint
        response = requests.get(endpoint,headers=headers)

        # If the request was a success, return the JSON data, else print an error code
        # TODO: replace print with thrown exception
        if(response.status_code == 200):
            json_data = json.loads(response.text)
            return json_data['value']
        else:
            print("The response did not return a success code. Returning nothing.")
            return None

    # Starts a basic web server on localhost port 1080
    # This will only handle one request and then terminate
    def Run_Localhost_Server(self, server_class=http.server.HTTPServer, handler_class=RequestHandler):
        server_address = ('127.0.0.1', 1080)
        httpd = server_class(server_address, handler_class)
        httpd.handle_request()