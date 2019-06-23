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
