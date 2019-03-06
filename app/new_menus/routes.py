from . import new_menus


# noinspection PyBroadException
@new_menus.route('/new_menus')
def new_menus():
    return '<h1>New menus</h1><br>Working on it'
