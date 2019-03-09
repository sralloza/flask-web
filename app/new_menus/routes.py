from flask import render_template, redirect

from app.new_menus.motor import DailyMenusManager
from . import new_menus


# noinspection PyBroadException
@new_menus.route('/new-menus')
def new_menus_view():
    dmm = DailyMenusManager.load()
    for menu in dmm:
        menu.to_database()
    return render_template('index.html', menus=dmm.menus[:15])


@new_menus.route('/n')
@new_menus.route('/new_menus')
def new_menus_redirect():
    return redirect('new-menus')
