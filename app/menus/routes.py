from flask import render_template, redirect, url_for, request

from app.menus.motor import DailyMenusManager
from app.utils import get_last_menus_page
from . import menus


@menus.route('/menus')
def menus_view():
    dmm = DailyMenusManager.load()
    for menu in dmm:
        menu.to_database()

    last_url = get_last_menus_page()

    if request.args.get('all'):
        show = dmm.menus
    else:
        show = dmm.menus[:15]
    return render_template('index.html', menus=show, last_url=last_url)





@menus.route('/n')
@menus.route('/new_menus')
@menus.route('/new-menus')
def menus_redirect():
    return redirect('menus')


@menus.route('/menus/reload')
def menus_reload():
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for('menus.menus_view', _external=True))
