

class Error(Exception):
    """Base class for exceptions in octoductor."""
    def __init__(self, message):
        self.message = message

class FileNotFoundError(Error):
    def __init__(self, message):
        self.message = message

class RequestFailed(Error):
    def __init__(self, message):
        self.message = message
