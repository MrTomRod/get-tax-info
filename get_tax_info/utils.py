from os.path import dirname, realpath
from pprint import pprint

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


def query_options(options: list, query_text: str = 'Choose among your options:') -> str:
    print('These are your options:')
    options_dict = {str(i): o for i, o in enumerate(options)}
    pprint(options_dict)

    response = ''
    while response not in options_dict:
        response = input(query_text)

    return response
