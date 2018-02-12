class FBError(Exception):
    pass

class FacebookError(FBError):


    def __init__(self, msg = None):
        self.msg = msg

        super().__init__()

class ValidationError(FacebookError):
    pass

class NotFoundError(FacebookError):
    pass
