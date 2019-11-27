from msal import PublicClientApplication
import yaml
from requests_oauthlib import OAuth2Session
import os

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
    # No suitable token exists in cache. Let's get a new one from AAD.
    result = app.acquire_token_by_authorization_code(, scopes=settings["scopes"])