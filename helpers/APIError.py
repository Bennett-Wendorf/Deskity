class APIError(Exception):
    '''
        An error that is thrown when there is an issue with an api call.
    '''

    def __init__(self, message):
        self.message = message
