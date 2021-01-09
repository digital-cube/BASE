

class NoEnoughInformationToCreateModel(NameError):
    def __init__(self, missing_key):
        self.missing_key = missing_key


class DatabaseIntegrityError(NameError):
    def __init__(self, message=None):
        self.message = message


class InternalServerError(NameError):
    def __init__(self, message=None):
        self.message = message
