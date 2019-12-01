from msal import PublicClientApplication
import yaml
from requests_oauthlib import OAuth2Session
import os
import webbrowser
import http.server
import threading

#class RequestHandler(BaseHTTPRequestHandler):
 #   def do_GET(self):



def aquireAuthCode(settings):
    authorize_url = '{0}{1}'.format(settings['authority'], settings['authorize_endpoint'])
    print("Authorize URL:", authorize_url)
    aadAuth = OAuth2Session(settings['app_id'], scope=settings['scopes'])#, redirect_uri=settings['redirect_uri'])
    sign_in_url, state = aadAuth.authorization_url(authorize_url, prompt='login')
    webServerThread = threading.Thread(target=RunLocalhostServer)
    webServerThread.setDaemon(True)
    webServerThread.start()
    print("Sign in URL:", sign_in_url)
    webbrowser.open(sign_in_url, new=1, autoraise=True)
    authorization_response = input('Enter the auth code: ')
    return authorization_response

def RunLocalhostServer(server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
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
        authCode = aquireAuthCode(settings)
        # No suitable token exists in cache. Let's get a new one from AAD.
        result = app.acquire_token_by_authorization_code(authCode, scopes=settings["scopes"])
        print("Token:", result)