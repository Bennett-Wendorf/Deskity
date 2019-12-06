from msal import PublicClientApplication
import yaml
from requests_oauthlib import OAuth2Session
import os
import webbrowser
import http.server
import threading
from urllib.parse import urlparse, parse_qs
from time import sleep

authorization_response = None
webServerThread = None

# Request handler to parse url's get request and strip out authorization code as string. 
# Sets the global authorization_response variable to this value.
class RequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_response
        query_components = parse_qs(urlparse(self.path).query)
        code = str(query_components['code'])
        print("Query compnents are:", query_components)
        refinedCode = code[2:len(code)-2]
        authorization_response = refinedCode
        print("Authorization response is:", authorization_response)

# Aquire msal auth code from Microsoft
def aquireAuthCode(settings):
    global authorization_response
    # Begin localhost web server in a new thread to handle the get request that will come from Microsoft
    webServerThread = threading.Thread(target=RunLocalhostServer)
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

# Starts a basic web server on the localhost http port
def RunLocalhostServer(server_class=http.server.HTTPServer, handler_class=RequestHandler):
    server_address = ('127.0.0.1', 80)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == '__main__':
    # This is necessary because Azure does not guarantee
    # to return scopes in the same case and order as requested
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

    # Load the authentication_settings.yml file
    # Note: this file is not tracked by github, so it will need to be created before running
    stream = open('../../authentication_settings.yml', 'r')
    settings = yaml.load(stream, yaml.SafeLoader)

    app = PublicClientApplication(settings['app_id'], authority=settings["authority"])

    result = None
    accounts = app.get_accounts()
    if accounts:
        print("Pick the account you would like to use to proceed:")
        for a in accounts:
            print(a["username"])
        #assuming the user selected the first one
        chosen = accounts[0]
        result = app.acquire_token_silent(settings["scopes"], account=chosen)

    if not result:
        # Get auth code
        authCode = aquireAuthCode(settings)
        # No suitable token exists in cache. Let's get a new one from AAD.

        # Obtain scopes from yml and split them into a list format
        scopes = settings["scopes"].split()
        # Aquire token from Microsoft with auth code and scopes from above
        result = app.acquire_token_by_authorization_code(authCode, scopes=scopes)
        # Strip down the result and convert it to a string to get the final access token
        access_token = str(result['access_token'])
        print("Access token is:", access_token)