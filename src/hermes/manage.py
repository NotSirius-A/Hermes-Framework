import argparse
from hermes.manage_commands import Manager

class Hermes:
    def main(self, settings):
        manager = Manager(settings)
        choices = manager.get_actions()

        parser = argparse.ArgumentParser(description='Notifer Framework manager tool')
        parser.add_argument('action', action="store", type=str, choices=choices, help='Specify action that app will execute')
        kwargs = parser.parse_args()._get_kwargs()
        kwargs = dict(kwargs)

        manager.process_command(kwargs)
