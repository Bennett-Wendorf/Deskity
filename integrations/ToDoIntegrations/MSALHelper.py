#region Imports

import requests
import webbrowser
import http.server
from urllib.parse import urlparse, parse_qs
from msal import PublicClientApplication, SerializableTokenCache
from requests_oauthlib import OAuth2Session
import os
import atexit
import threading

import logging
logger = logging.getLogger("To Do Widget")

from dynaconf_settings import settings

from helpers.APIError import APIError

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
        logger.debug("Got response from HTTP server.")
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def Run_Localhost_Server(server_class=http.server.HTTPServer, handler_class=RequestHandler):
    '''
    Start a basic web server on localhost port 1080 using the custom request handler defined at the start of this file.

    This will only handle one request and then terminate.
    '''
    server_address = ('127.0.0.1', 1080)
    httpd = server_class(server_address, handler_class)
    httpd.handle_request()

# The instance of the Public Client Application from MSAL. This is assigned in __init__
app = None

redirect_uri = "http://localhost:1080"
scopes = ["user.read", "Tasks.ReadWrite"]
headers = ""

# The access token aquired in Aquire_Access_Token. This is a class variable for the cases
# where there is an attempt to make a request again in the short time this token is valid for.
# If that should happen, storing the token like this minimalizes the amount of requests needed
# to Microsoft's servers
access_token = None

# This is necessary because Azure does not guarantee
# the return of scopes in the same case and order as requested
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

def Setup_Msal(to_do_widget_instance):
    '''Set up the msal helper so it can be used later. This should be run at __init__ of the To_Do_Widget'''
    global app

    cache = Deserialize_Cache("integrations/ToDoIntegrations/microsoft_cache.bin")

    # Instantiate the Public Client App
    app = PublicClientApplication(settings.To_Do_Widget.get('app_id', '565467a5-8f81-4e12-8c8d-e6ec0a0c4290'), authority="https://login.microsoftonline.com/common", token_cache=cache)

    # Begin setting up tasks in the to do widget
    setup_thread = threading.Thread(target=to_do_widget_instance.Setup_Tasks)
    setup_thread.start()

def Get_Msal_Headers():
    '''Return the headers needed to make API calls to Microsoft'''
    global headers
    return headers

def Set_Msal_Headers(new_headers):
    '''Change the headers that are needed to make API calls to Microsoft'''
    global headers
    headers = new_headers

def Deserialize_Cache(cache_path):
    '''Create the cache object, deserialize it for use, and register it to be reserialized before the application quits.'''
    cache = SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r").read())
        logger.info("Reading MSAL token cache")

    # Register a function with atexit to make sure the cache is written to just before the application terminates.
    atexit.register(lambda:
        open(cache_path, "w").write(cache.serialize())
        # Hint: The following optional line persists only when state changed
        if cache.has_state_changed else None
    )

    return cache

def Aquire_Access_Token():
    '''
    If there is an access token in the cache, get it and obtain an authorization code using it. 
    Else run the Aquire_Auth_Code method to have the user authenticate.
    '''
    global app, access_token, scopes, redirect_uri, settings
    result = None
    accounts = app.get_accounts()

    if(access_token == None):

        # Since I don't have a token, check the cache to see if I can get one that way
        result = Pull_From_Token_Cache()

        if (result == None):
            # Then there was no token in the cache

            # Get auth code
            authCode = Aquire_Auth_Code(settings)

            # Aquire token from Microsoft with auth code and scopes from above
            result = app.acquire_token_by_authorization_code(authCode, scopes=scopes, redirect_uri=redirect_uri)
        
        # Strip down the result and convert it to a string to get the final access token
        access_token = str(result['access_token'])
    
    if access_token == None:
        raise APIError("Something went wrong and no Microsoft access token was obtained")
    
    return access_token

def Pull_From_Token_Cache():
    '''If there is a vaild account in the cache, obtain it and then use it to get and return an access token.'''
    global app, scopes
    
    accounts = app.get_accounts()
    if accounts:
        # TODO: Will implement better account management later. For now, the first account found is chosen.
        return app.acquire_token_silent(scopes, account=accounts[0])
    else:
        logger.info("No accounts were found in the cache. Reauthenticating...")
        return None

def Aquire_Auth_Code(settings):
    '''Aquire MSAL authorization code from Microsoft.'''
    # Use the global variables instead of a local ones
    global authorization_response, scopes, redirect_uri

    # Begin localhost web server in a new thread to handle the get request that will come from Microsoft
    webServerThread = threading.Thread(target=Run_Localhost_Server)
    webServerThread.setDaemon(True)
    webServerThread.start()

    # Begins OAuth session with app_id, scopes, and redirect_uri from yml
    aadAuth = OAuth2Session(settings.To_Do_Widget.get('app_id'), scope=scopes, redirect_uri=redirect_uri)

    # Obtain final login url from the OAuth session
    sign_in_url, state = aadAuth.authorization_url("https://login.microsoftonline.com/common/oauth2/v2.0/authorize")

    # Opens a web browser with the new sign in url
    webbrowser.open(sign_in_url, new=2, autoraise=True)

    # Waits until the web server thread closes before continuing
    # This ensures that an authorization response will be returned.
    webServerThread.join()

    # This function returns the global authorization_response when it is not equal to None
    return authorization_response