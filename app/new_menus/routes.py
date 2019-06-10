from flask import render_template, redirect, url_for, request

from app.new_menus.motor import DailyMenusManager
from app.utils import get_last_menus_page
from . import new_menus


# noinspection PyBroadException
@new_menus.route('/new-menus')
def new_menus_view():
    dmm = DailyMenusManager.load()
    for menu in dmm:
        menu.to_database()

    last_url = get_last_menus_page()
    print(request.data)
    if request.args.get('all'):
        show = dmm.menus
    else:
        show = dmm.menus[:15]
    return render_template('index.html', menus=show, last_url=last_url)


@new_menus.route('/n')
@new_menus.route('/new_menus')
def new_menus_redirect():
    return redirect('new-menus')


@new_menus.route('/new-menus/reload')
def new_menus_reload():
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for('new_menus.new_menus_view', _external=True))
