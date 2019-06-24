import json
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
    _all = request.args.get('all') is not None
    beta = request.args.get('beta') is not None

    show = dmm.menus

    if _all and beta:
        return redirect('/menus?beta')

    if not _all and not beta:
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

    yesterday_url = None
    tomorrow_url = None
    disabled_yesterday = 'disabled'
    disabled_tomorrow = 'disabled'

    if yesterday.date() in dmm:
        yesterday_url = url_for('menus.today', _external=True) + '?day=' + str(yesterday.date())
        disabled_yesterday = ''
    if tomorrow.date() in dmm:
        tomorrow_url = url_for('menus.today', _external=True) + '?day=' + str(tomorrow.date())
        disabled_tomorrow = ''

    return render_template(
        'today.html', menu=menu, day=day, title_url=get_last_menus_page(),
        yesterday_url=yesterday_url, tomorrow_url=tomorrow_url,
        disabled_yesterday=disabled_yesterday, disabled_tomorrow=disabled_tomorrow
    )


@menus.route('/api/menus')
def api_menus():
    dmm = DailyMenusManager.load()
    out = []

    for menu in dmm:
        foo = {}
        day = re.search(r'\((\w+)\)', menu.format_date()).group(1).capitalize()
        foo["day"] = f'{day} {menu.date.day}'
        foo["lunch"] = {"p1": menu.lunch.p1, "p2": menu.lunch.p2}
        foo["dinner"] = {"p1": menu.dinner.p1, "p2": menu.dinner.p2}
        out.append(foo)

    return json.dumps(out), 200

