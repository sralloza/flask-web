"""Command Line Interface for running server or more advanced
functions.
"""
import sys

from app import app
from app.menus.core.daily_menus_manager import DailyMenusManager

KEYWORD = "moises"


def show_help():
    """Prints the usage of the program."""
    print("Usage: ")
    print("- To run server normally:")
    print("    $ python cli.py ")
    print("- To parse all data found on the server:")
    print("    $ python cli.py %s" % KEYWORD)


def trigger_moises_protocol():
    """Triggers moises protocol and starts processing all urls."""
    print("MOISES PROTOCOL: parsing every data since moises' flood")
    with app.app_context():
        DailyMenusManager.load(parse_all=True)
    print("Done")


def main():
    """Main function of the program."""
    if len(sys.argv) == 1:
        app.run(port=80, host="0.0.0.0", debug=True)
    elif len(sys.argv) == 2:
        if sys.argv[1] == KEYWORD:
            trigger_moises_protocol()
        else:
            show_help()
    else:
        show_help()

    sys.exit()


if __name__ == "__main__":
    main()
