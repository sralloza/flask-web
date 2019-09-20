from argparse import ArgumentParser

from app import create_app
from app.menus.core.daily_menus_manager import DailyMenusManager


def main():
    parser = ArgumentParser('Menus')
    subparsers = parser.add_subparsers(title='commands', dest='command')

    subparsers.add_parser('add')

    opt = parser.parse_args()

    if opt.command is None:
        return parser.error('Use add command')

    return DailyMenusManager.add_manual()


if __name__ == '__main__':
    with create_app(config_object='app.config.Config').app_context():
        main()
