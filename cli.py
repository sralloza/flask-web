import sys

from app import app
from app.menus.core.daily_menus_manager import DailyMenusManager

KEYWORD = "moises"


def show_help():
    print("Usage: ")
    print("- To run server normally:")
    print("    $ cli.py ")
    print("- To parse all data found on the server:")
    print("    $ cli.py %s" % KEYWORD)


def do_it():
    print("MOISES PROTOCOL: parsing every data since moises' flood")
    with app.app_context():
        DailyMenusManager.load(parse_all=True)
    print("Done")


def main():
    if len(sys.argv) == 1:
        app.run(port=80, host="0.0.0.0", debug=True)
    elif len(sys.argv) == 2:
        if sys.argv[1] == KEYWORD:
            do_it()
        else:
            show_help()
    else:
        show_help()

    exit()


if __name__ == "__main__":
    main()
