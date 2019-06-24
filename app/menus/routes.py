import re
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, request

from app.menus.motor import DailyMenusManager
from app.utils import get_last_menus_page
from . import menus


@menus.route('/menus')
def menus_view():
    dmm = DailyMenusManager.load()

    last_url = get_last_menus_page()
    all = request.args.get('all') is not None
    beta = request.args.get('beta') is not None

    show = dmm.menus

    if all and beta:
        return redirect('/menus?beta')

    if not all and not beta:
        show = dmm.menus[:15]

    template_name = 'index.html'

    if beta:
        template_name = 'beta.html'

    return render_template(template_name, menus=show, last_url=last_url)


@menus.route('/n')
@menus.route('/new_menus')
@menus.route('/new-menus')
def menus_redirect():
    return redirect('menus')


@menus.route('/menus/reload')
def menus_reload():
    return redirect(url_for('menus.menus_view', _external=True))


@menus.route('/hoy')
def today():
    dmm = DailyMenusManager.load()
    day = request.args.get('day')

    asked = datetime.today()

    if day in (None, ''):
        menu = dmm[datetime.today().date()]
    else:
        asked = datetime.strptime(day, '%Y-%m-%d')
        menu = dmm[asked.date()]

    delta = timedelta(days=1)
    tomorrow = asked + delta
    yesterday = asked - delta

    day = re.search(r'\((\w+)\)', menu.format_date()).group(1).capitalize()
    day = f'{day} {menu.date.day}'

    previous_url = None
    next_url = None
    if yesterday.date() in dmm:
        previous_url = url_for('menus.today', _external=True) + '?day=' + str(yesterday.date())
    if tomorrow.date() in dmm:
        next_url = url_for('menus.today', _external=True) + '?day=' + str(tomorrow.date())

    return render_template(
        'today.html', menu=menu, day=day, last_url=get_last_menus_page(),
        previous_url=previous_url, next_url=next_url
    )
