from flask import render_template

from app.new_menus.motor import DailyMenusManager
from . import new_menus


# noinspection PyBroadException
@new_menus.route('/new_menus')
@new_menus.route('/new-menus')
def new_menus():
    dmm = DailyMenusManager.load()
    for menu in dmm:
        menu.to_database()
    return render_template('index.html', menus=dmm.menus[:15])
