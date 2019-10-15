import json
from datetime import datetime

from flask import redirect, render_template, request, url_for

from app.utils import get_last_menus_page, get_post_arg, gen_token
from . import menus_blueprint
from .core.daily_menus_manager import DailyMenusManager
from .core.structure import DailyMenu, Meal


@menus_blueprint.route("/menus")
def menus_view():
    _all = request.args.get("all") is not None
    beta = request.args.get("beta") is not None

    if _all and beta:
        return redirect("/menus?beta")

    dmm = DailyMenusManager.load()

    last_url = get_last_menus_page()
    show = dmm.menus

    if not _all and not beta:
        show = dmm.menus[:15]

    template_name = "index.html"

    if beta:
        template_name = "beta.html"

    return render_template(template_name, menus=show, last_url=last_url)


@menus_blueprint.route("/n")
@menus_blueprint.route("/new_menus")
@menus_blueprint.route("/new-menus")
def menus_redirect():
    return redirect("menus", code=301)


@menus_blueprint.route("/menus/reload")
def menus_reload():
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for("menus_blueprint.menus_view", _external=True))


@menus_blueprint.route("/h")
def today_redirect():
    return redirect("hoy", code=301)


@menus_blueprint.route("/hoy/reload")
def today_reload():
    # TODO: instead of having endpoint '/menus/reload', add argument in request 'force'
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for("menus_blueprint.today_js_view", _external=True))


@menus_blueprint.route("/hoy")
def today_js_view():
    force = (
        request.args.get("force") is not None
        or request.args.get("f") is not None
        or request.args.get("reload") is not None
    )

    dmm = DailyMenusManager.load(force=force)
    last_url = get_last_menus_page()
    data = json.dumps(dmm.to_json())
    return render_template("today-js.html", menus=data, title_url=last_url)


@menus_blueprint.route("/api/menus/add", methods=["POST"])
def add_menu_api():
    json_data = dict(request.form)
    for key, value in json_data.items():
        json_data[key] = value[0]

    try:
        token = get_post_arg("token", required=True, strip=True)
        day = int(get_post_arg("day", required=True, strip=True))
        month = int(get_post_arg("month", required=True, strip=True))
        year = int(get_post_arg("year", required=True, strip=True))
        lunch1 = get_post_arg("lunch-1", required=False, strip=True)
        lunch2 = get_post_arg("lunch-2", required=False, strip=True)
        dinner1 = get_post_arg("dinner-1", required=False, strip=True)
        dinner2 = get_post_arg("dinner-2", required=False, strip=True)
    except ValueError as err:
        return "ValueError: %r" % str(err.args[0]), 403
    except RuntimeError as err:
        return str(err.args[0]), 403

    real_token = gen_token()

    if real_token != token:
        return "Invalid token", 403

    lunch = Meal(lunch1, lunch2)
    dinner = Meal(dinner1, dinner2)
    menu = DailyMenu(day, month, year, lunch, dinner)

    dmm = DailyMenusManager()
    dmm.add_to_menus(menu)
    dmm.save_to_database()
    return repr(menu)


@menus_blueprint.route("/api/menus")
def api_menus():
    force = request.args.get("force") is not None or request.args.get("f") is not None
    dmm = DailyMenusManager.load(force=force)
    data = dmm.to_json()
    return json.dumps(data), 200


@menus_blueprint.route("/add", methods=["GET", "POST"])
def add_menu_interface():
    if request.method == "GET":
        return render_template("add-interface.html")

    try:
        date = get_post_arg("date", required=True, strip=True)
        lunch1 = get_post_arg("lunch-1", required=False, strip=True)
        lunch2 = get_post_arg("lunch-2", required=False, strip=True)
        dinner1 = get_post_arg("dinner-1", required=False, strip=True)
        dinner2 = get_post_arg("dinner-2", required=False, strip=True)
        token = get_post_arg("token", required=True, strip=True)
    except RuntimeError as err:
        return str(err.args[0]), 403

    if token != gen_token():
        return "Invalid token", 403

    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as err:
        return "Invalid date format: " + err.args[0], 403

    menu = DailyMenu(
        date.day, date.month, date.year, Meal(lunch1, lunch2), Meal(dinner1, dinner2)
    )

    result = menu.to_database()
    meta = '<meta http-equiv="refresh" content="15; url=/">'
    meta += '<br><a href="/">Home</a><br><a href="/add">Add more</a>'

    status = "Saved" if result else "Not saved"
    code = 200 if result else 409

    return f"{status}:\n<br>" + repr(menu) + meta, code


@menus_blueprint.route("/del", methods=["GET", "POST"])
def del_menu_interface():
    if request.method == "GET":
        return render_template("del-interface.html")

    try:
        date = get_post_arg("date", required=True, strip=True)
        token = get_post_arg("token", required=True, strip=True)
    except RuntimeError as err:
        return str(err.args[0]), 403

    if token != gen_token():
        return "Invalid token", 403

    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as err:
        return "Invalid date format: " + err.args[0], 403

    menu = DailyMenu(date.day, date.month, date.year)
    result = menu.remove_from_database()

    meta = '<meta http-equiv="refresh" content="15; url=/">'
    meta += '<br><a href="/">Home</a><br><a href="/del">Del more</a>'

    status = "Deleted" if result else "Not deleted"
    code = 200 if result else 409

    return f"{status}:\n<br>" + menu.format_date() + meta, code
