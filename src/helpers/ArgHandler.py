import argparse

def Parse_Args():
    global args
    # TODO: Update this prog and description.
    parser = argparse.ArgumentParser(description="An app built on Kivy that shows information that might be useful at a glance. This is designed to be run on a raspberry pi with a touchscreen.")
    parser.add_argument('-v', '--verbose', action='store_true', help="Output detailed debug information.")
    args = parser.parse_args()

def Get_Args():
    global args
    if not "args" in globals():
        Parse_Args()
    return args