import json
import re
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, request

from app.utils import get_last_menus_page, today
from . import menus_blueprint
from .core.daily_menus_manager import DailyMenusManager
from .core.structure import DailyMenu


@menus_blueprint.route('/menus')
def menus_view():
    _all = request.args.get('all') is not None
    beta = request.args.get('beta') is not None

    if _all and beta:
        return redirect('/menus?beta')

    dmm = DailyMenusManager.load()

    last_url = get_last_menus_page()
    show = dmm.menus

    if not _all and not beta:
        show = dmm.menus[:15]

    template_name = 'index.html'

    if beta:
        template_name = 'beta.html'

    return render_template(template_name, menus=show, last_url=last_url)


@menus_blueprint.route('/n')
@menus_blueprint.route('/new_menus')
@menus_blueprint.route('/new-menus')
def menus_redirect():
    return redirect('menus', code=301)


@menus_blueprint.route('/menus/reload')
def menus_reload():
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for('menus_blueprint.menus_view', _external=True))


@menus_blueprint.route('/h')
def today_redirect():
    return redirect('hoy', code=301)


@menus_blueprint.route('/hoy/reload')
def today_reload():
    # TODO: instead of having endpoint '/menus/reload', add argument in request 'force'
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for('menus_blueprint.today_js_view', _external=True))


@menus_blueprint.route('/hoy')
def today_js_view():
    return render_template('today-js.html')


@menus_blueprint.route('/api/menus')
def api_menus():
    force = request.args.get('force') is not None or request.args.get('f') is not None
    dmm = DailyMenusManager.load(force=force)
    data = dmm.to_json()
    return json.dumps(data), 200


@menus_blueprint.route('/old/hoy')
def today_old_view():
    dmm = DailyMenusManager.load()
    day = request.args.get('day')

    asked = None
    code = 200

    try:
        if day in (None, ''):
            asked = today()
            menu = dmm[asked.date()]
        else:
            asked = datetime.strptime(day, '%Y-%m-%d')
            menu = dmm[asked.date()]
    except ValueError:
        asked = today()
        menu = DailyMenu(asked.day, asked.month, asked.year)
        code = 404
    except KeyError:
        menu = DailyMenu(asked.day, asked.month, asked.year)
        code = 404

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
        yesterday_url = url_for('menus_blueprint.today_old_view', _external=True) + '?day=' + str(
            yesterday.date())
        disabled_yesterday = ''
    if tomorrow.date() in dmm:
        tomorrow_url = url_for('menus_blueprint.today_old_view', _external=True) + '?day=' + str(
            tomorrow.date())
        disabled_tomorrow = ''

    return render_template(
        'today-old.html', menu=menu, day=day, title_url=get_last_menus_page(),
        yesterday_url=yesterday_url, tomorrow_url=tomorrow_url,
        disabled_yesterday=disabled_yesterday, disabled_tomorrow=disabled_tomorrow
    ), code
