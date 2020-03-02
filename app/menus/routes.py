import json
from collections import namedtuple
from datetime import datetime

from flask import redirect, render_template, request, url_for
from flask.helpers import flash

from app.menus.core.utils import PRINCIPAL_URL, get_last_menus_url
from app.utils import Tokens, get_post_arg

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

    last_url = get_last_menus_url()
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


@menus_blueprint.route("/menus/update")
def menus_update():
    dmm = DailyMenusManager.load(force=True)

    for menu in dmm:
        menu.to_database()

    return redirect(url_for("menus_blueprint.menus_view", _external=True))


@menus_blueprint.route("/h")
def today_redirect():
    return redirect("hoy", code=301)


@menus_blueprint.route("/hoy/update")
def today_update():
    return redirect(url_for("menus_blueprint.today_view", _external=True) + "?update")


@menus_blueprint.route("/hoy")
def today_view():
    update = request.args.get("update") is not None

    dmm = DailyMenusManager.load(force=update)
    data = json.dumps(dmm.to_json())
    update = json.dumps(dmm.updated)
    return render_template(
        "today.html", menus=data, default=PRINCIPAL_URL, update=update
    )


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

    if not Tokens.check_token(token):
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
    FormData = namedtuple("FormData", "date lunch1 lunch2 dinner1 dinner2".split())
    form_data = FormData("", "", "", "", "")

    if request.method == "GET":
        return render_template("add-interface.html", data=form_data)

    try:
        date = get_post_arg("date", required=True, strip=True)
        lunch1 = get_post_arg("lunch-1", required=False, strip=True)
        lunch2 = get_post_arg("lunch-2", required=False, strip=True)
        dinner1 = get_post_arg("dinner-1", required=False, strip=True)
        dinner2 = get_post_arg("dinner-2", required=False, strip=True)
        token = get_post_arg("token", required=True, strip=True)
    except RuntimeError as err:
        return str(err.args[0]), 403

    form_data = FormData(date, lunch1, lunch2, dinner1, dinner2)

    if not Tokens.check_token(token):
        flash("Invalid token", "danger")
        return render_template("add-interface.html", data=form_data), 403

    try:
        date = datetime.strptime(date, r"%Y-%m-%d")
    except ValueError as err:
        flash("Invalid date format: " + err.args[0], "danger")
        form_data = form_data._replace(date=None)
        return render_template("add-interface.html", data=form_data), 403

    menu = DailyMenu(
        date.day, date.month, date.year, Meal(lunch1, lunch2), Meal(dinner1, dinner2)
    )

    result = menu.to_database()

    if result:
        flash("Menú guardado: %s" % menu.format_date(), "success")
    else:
        flash("Menú no guardado: %s" % menu.format_date(), "warning")

    code = 200 if result else 409

    form_data = FormData("", "", "", "", "")
    return render_template("add-interface.html", data=form_data), code


@menus_blueprint.route("/del", methods=["GET", "POST"])
def del_menu_interface():
    FormData = namedtuple("FormData", ["date"])
    date = ""

    if request.method == "GET":
        return render_template("del-interface.html", data=FormData(date))

    try:
        date = get_post_arg("date", required=True, strip=True)
        token = get_post_arg("token", required=True, strip=True)
    except RuntimeError as err:
        flash(err, "info")
        flash(str(err.args[0]), "danger")
        return render_template("del-interface.html", data=FormData(date)), 403

    if not Tokens.check_token(token):
        flash("Invalid token", "danger")
        return render_template("del-interface.html", data=FormData(date)), 403

    try:
        date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError as err:
        flash("Invalid date format: " + err.args[0], "danger")
        date = ""
        return render_template("del-interface.html", data=FormData(date)), 403

    menu = DailyMenu(date.day, date.month, date.year)
    result = menu.remove_from_database()

    if result:
        flash("Menú eliminado: %s" % menu.format_date(), "success")
    else:
        flash("Menú no eliminado: %s" % menu.format_date(), "warning")

    code = 200 if result else 409
    date = ""

    return render_template("del-interface.html", data=FormData(date)), code
