from hermes.app import App
from inspect import getmembers, isfunction, ismethod

from hermes.core.exceptions import ActionDoesNotExistError

class Manager:
    def __init__(self, settings) -> None:
        self.app = App(settings)

    def get_actions(self) -> list:
        return self.app.get_actions()


    def process_command(self, command:str=None, *args, **kwargs):
        if command is None:
            raise NotImplementedError("`command` must be provided")

        try:
            action = command['action']
        except KeyError as e:
            print("required command line argument not found")
            raise e

        self.run(action=action)

    def get_actions(self) -> list:
        # get all functions that represent application modes of operation (actions), but dont include magic methods
        methods = getmembers(App, predicate=isfunction)
        methods = [method[0] for method in methods if not method[0].startswith("__")]
        return methods


    def run(self, action: str=None, *args, **kwargs):
        if action not in self.get_actions():
            raise ActionDoesNotExistError("Illegal action, should be safely filtered out before passing it here")

        process = getattr(self.app, action)
        process(*args, **kwargs)