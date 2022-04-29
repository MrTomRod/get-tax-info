from os.path import dirname, realpath

ROOT = dirname(realpath(__file__))


class TaxIdNnotFoundError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Could not find taxid: " + repr(self.data)


class UniqueNameNotFoundError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Could not find unique_name: " + repr(self.data)


class NameNotFoundError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "Could not find unique_name: " + repr(self.data)


class BuscoParentNotFoundError(Exception):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        return "TaxID has no BUSCO-parent: " + repr(self.data)
