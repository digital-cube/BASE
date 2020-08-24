class NoEnoughInformationToCreateModel(NameError):
    def __init__(self, missing_key):
        self.missing_key = missing_key
