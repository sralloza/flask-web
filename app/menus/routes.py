import json
import re
from datetime import datetime, timedelta

from flask import render_template, redirect, url_for, request

from app.utils import get_last_menus_page, now
from . import menus_blueprint
from .core.daily_menus_manager import DailyMenusManager
from .core.structure import DailyMenu, Meal


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
    force = request.args.get('force') is not None \
            or request.args.get('f') is not None \
            or request.args.get('reload') is not None

    dmm = DailyMenusManager.load(force=force)
    data = json.dumps(dmm.to_json())
    return render_template('today-js.html', menus=data)


@menus_blueprint.route('/api/menus/add', methods=['POST'])
def add_menu_api():
    json_data = dict(request.form)
    for key, value in json_data.items():
        json_data[key] = value[0]

    try:
        api_key = json_data['api_key']
        day = int(json_data['day'])
        month = int(json_data['month'])
        year = int(json_data['year'])
        lunch1 = json_data['lunch1']
        lunch2 = json_data['lunch2']
        dinner1 = json_data['dinner1']
        dinner2 = json_data['dinner2']
    except KeyError as key:
        return 'Missing %s' % key, 403
    except ValueError as v:
        return 'ValueError: %r' % ', '.join(v.args), 403

    real_api_key = now().strftime('%Y%m%d%H%M')

    if real_api_key != api_key:
        return 'Invalid api key', 403

    lunch = Meal(lunch1, lunch2)
    dinner = Meal(dinner1, dinner2)
    menu = DailyMenu(day, month, year, lunch, dinner)

    dmm = DailyMenusManager()
    dmm.add_to_menus(menu)
    dmm.save_to_database()
    return repr(menu)


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
            asked = now()
            menu = dmm[asked.date()]
        else:
            asked = datetime.strptime(day, '%Y-%m-%d')
            menu = dmm[asked.date()]
    except ValueError:
        asked = now()
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
