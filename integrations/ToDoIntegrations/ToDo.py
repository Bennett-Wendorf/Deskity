from msal import PublicClientApplication
import yaml
from requests_oauthlib import OAuth2Session
import os
import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs
from time import sleep
import requests
import json

authorization_response = None
webServerThread = None

# Request handler to parse url's get request and strip out authorization code as string. 
# Sets the global authorization_response variable to this value.
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_response
        query_components = parse_qs(urlparse(self.path).query)
        code = str(query_components['code'])
        authorization_response = code[2:len(code)-2]

class ToDoIntegration():

    # Load the authentication_settings.yml file
    # Note: this file is not tracked by github, so it will need to be created before running
    stream = open('integrations/ToDoIntegrations/microsoft_authentication_settings.yml', 'r')
    settings = yaml.load(stream, yaml.SafeLoader)

    app = PublicClientApplication(settings['app_id'], authority=settings["authority"])

    access_token = None
    result = None
    accounts = app.get_accounts()

    def __init__(self):
        # This is necessary because Azure does not guarantee
        # to return scopes in the same case and order as requested
        os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
        os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

    # Gets access token however it is needed and returns that token
    def Aquire_Access_Token(self):
        if(self.access_token == None):
            if self.accounts:
                print("Pick the account you would like to use to proceed:")
                for a in self.accounts:
                    print(a["username"])
                #assuming the user selected the first one
                chosen = self.accounts[0]
                self.result = self.app.acquire_token_silent(self.settings["scopes"], account=chosen)

            if (self.result == None):
                # Get auth code
                authCode = self.Aquire_Auth_Code(self.settings)
                # No suitable token exists in cache. Let's get a new one from AAD.

                # Obtain scopes from yml and split them into a list format
                scopes = self.settings["scopes"].split()
                # Aquire token from Microsoft with auth code and scopes from above
                self.result = self.app.acquire_token_by_authorization_code(authCode, scopes=scopes)
                # Strip down the result and convert it to a string to get the final access token
                self.access_token = str(self.result['access_token'])
        return self.access_token
    
    # Starts a basic web server on the localhost http port
    def Run_Localhost_Server(self, server_class=http.server.HTTPServer, handler_class=RequestHandler):
        server_address = ('127.0.0.1', 80)
        httpd = server_class(server_address, handler_class)
        httpd.serve_forever()

    # Aquire msal auth code from Microsoft
    def Aquire_Auth_Code(self, settings):
        global authorization_response
        # Begin localhost web server in a new thread to handle the get request that will come from Microsoft
        webServerThread = threading.Thread(target=self.Run_Localhost_Server)
        webServerThread.setDaemon(True)
        webServerThread.start()
        # Builds url from yml variables
        authorize_url = '{0}{1}'.format(settings['authority'], settings['authorize_endpoint'])
        print("Authorize URL:", authorize_url)
        # Begins OAuth session with app_id, scopes, and redirect_uri from yml
        aadAuth = OAuth2Session(settings['app_id'], scope=settings['scopes'], redirect_uri=settings['redirect_uri'])
        # Obtain final login url from the OAuth session
        sign_in_url, state = aadAuth.authorization_url(authorize_url, prompt='login')
        print("Sign in URL:", sign_in_url)
        # Opens a web browser with the new sign in url
        webbrowser.open(sign_in_url, new=1, autoraise=True)
        # Waits here until the web server receives an authorization_response
        while(authorization_response == None):
            pass
        # This function returns the global authorization_response when it is not equal to None
        return authorization_response
    
    # Gets To Do Tasks from Microsoft
    def Get_Tasks(self, token):

        endpoint = "https://graph.microsoft.com/beta/me/outlook/tasks"
        headers = {'Content-Type':'application/json', 'Authorization':'Bearer {0}'.format(token)}

        response = requests.get(endpoint,headers=headers)
        if(response.status_code == 200):
            json_data = json.loads(response.text)
            print("JSON data is:", json_data)
            return json_data['value']
        else:
            print("The response did not return a success code. Returning nothing.")
            return None
        